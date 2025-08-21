import traceback
from typing import List, Dict, Set, Tuple, Optional, Union
from uuid import uuid4
import pandas as pd
from fastapi import Response
from kafka import KafkaProducer
from pydantic import BaseModel
from malevich_app.docker_export.operations import save_df_local
from malevich_app.export.abstract.abstract import KafkaInitRun, KafkaAppMsg, AppsBeforeInfo, KafkaInfo, LogsOperation, \
    FinishKafkaMsg
from malevich_app.export.request.dag_requests import send_post_dag
from malevich_app.export.secondary.LogHelper import log_warn, log_error
from malevich_app.export.secondary.collection.Collection import Collection
from malevich_app.export.secondary.collection.KafkaCollection import KafkaCollection
from malevich_app.export.secondary.endpoints import KAFKA_INFO
from malevich_app.export.secondary.helpers import call_async_fun, fix_df_id_name
from malevich_app.export.secondary.logger import input_logger
import malevich_app.export.secondary.const as C


class KafkaHelper:  # TODO add custom timeout
    producer: KafkaProducer = None

    def __init__(self, init_run: KafkaInitRun, j_app):
        self.__j_app = j_app

        self.__index: int = init_run.index

        self.__need: Set[Tuple[Optional[str], str, int]] = set()
        self.__collections: List[List[List[pd.DataFrame]]] = []             # args | subarg | scale
        self.__extra_collections: List[pd.DataFrame] = []
        self.__schemes: List[List[Optional[str]]] = []                      # args | subarg
        self.__start_indexes: Dict[Tuple[str, str], Tuple[int, int]] = {}
        self.__scale: Dict[Tuple[str, str], int] = {}

        self.__coll_to_index: Dict[str, int] = {}
        self.__extra_coll_to_index: Dict[str, int] = {}
        self.__is_init_app = False
        self.__metadata: Optional[List[str]] = None

        self.__send_topics: Optional[List[str]] = None if init_run.appsAfterInfo is None else init_run.appsAfterInfo.topics

        self.__set_before(init_run.appsBeforeInfo)
        self.__ready = True
        self.__extra_ready = True

    def __set_before(self, apps_before_info: List[AppsBeforeInfo]):
        for i, info in enumerate(apps_before_info):   # apps_before_info empty for init app
            for ind in range(info.indexStart, info.indexEnd):
                self.__need.add((info.taskId, info.appId, ind))
            self.__collections.append(None)
            self.__schemes.append(None)
            self.__start_indexes[(info.taskId, info.appId)] = (i, info.indexStart)
            self.__scale[(info.taskId, info.appId)] = info.indexEnd - info.indexStart

    def __df(self, json_data) -> pd.DataFrame:
        if self.__j_app.docker_mode == "python" or self.__j_app.docker_mode == "pyspark":
            df = pd.read_json(json_data)
            fix_df_id_name(df)
        elif self.__j_app.docker_mode == "dask":
            import dask.dataframe as dd
            df = dd.read_json(json_data)
            fix_df_id_name(df)
        else:
            raise Exception(f"wrong app mode {self.__j_app.docker_mode}")
        return df

    def __set_collections(self):
        collections = []
        for i, collargs in enumerate(self.__collections):
            subcollections = []
            for j, collsubargs in enumerate(collargs):
                if self.__j_app.docker_mode == "python" or self.__j_app.docker_mode == "pyspark":
                    df = pd.concat(collsubargs)
                elif self.__j_app.docker_mode == "dask":
                    import dask.dataframe as dd
                    df = dd.concat(collsubargs)
                else:
                    raise Exception(f"wrong app mode {self.__j_app.docker_mode}")
                if self.__j_app.docker_mode == "pyspark":
                    from malevich_app.docker_export.funcs import spark
                    df = spark.createDataFrame(df)
                scheme_name = None if self.__is_init_app else self.__schemes[i][j]
                coll = save_df_local(self.__j_app, df, scheme_name=scheme_name)
                subcollections.append(coll)
            collections.append(tuple(subcollections))
        self.__j_app.set_collections(collections)

        if self.__is_init_app:
            for i, colls in enumerate(collections):
                coll = colls[0]
                self.__j_app.metadata[coll.get()] = self.__metadata[i]

    def __set_extra_collections(self):
        self.__j_app.set_extra_collections([(save_df_local(self.__j_app, df),) for df in self.__extra_collections])

    @property
    def __result_topic(self) -> str:
        return f"{self.__j_app.operation_id}.result"

    @property
    def ready(self) -> bool:
        return self.__ready and self.__extra_ready and len(self.__need) == 0

    @property
    def index(self) -> int:
        return self.__index

    def set_collection_names(self, collection_names: Optional[List[str]]):
        """used only for init app"""
        assert self.__collections is None or len(self.__collections) == 0, "internal error in KafkaHelper.set_collections"

        self.__is_init_app = True
        self.__ready = False
        self.__metadata = []
        for i, coll in enumerate(collection_names):
            self.__coll_to_index[coll] = i
            self.__collections.append(None)
            self.__metadata.append(None)

    def set_extra_collection_names(self, collection_names: List[str]):
        self.__extra_ready = len(collection_names) == 0
        for i, coll in enumerate(collection_names):
            self.__extra_coll_to_index[coll] = i
            self.__extra_collections.append(None)

    def add(self, kafka_msg: KafkaAppMsg) -> bool:
        if self.ready:
            self.__j_app.logs_buffer.write("error kafka add collection: all already added\n")
            return False

        if self.__is_init_app:
            if len(kafka_msg.data) != len(self.__coll_to_index) + len(self.__extra_coll_to_index):
                self.__j_app.logs_buffer.write(f"error: wrong kafka collections size in init app: expected {len(self.__coll_to_index)} + {len(self.__extra_coll_to_index)}, found {len(kafka_msg.data)}\n")
                return False

            for coll, json_data in kafka_msg.data.items():
                index = self.__coll_to_index.get(coll)
                if index is not None:
                    self.__collections[index] = [[self.__df(json_data)]]
                    self.__metadata[index] = kafka_msg.metadata.get(coll)
                else:
                    index = self.__extra_coll_to_index.get(coll)
                    if index is None:
                        self.__j_app.logs_buffer.write(f"error: wrong kafka collection: {coll}\n")
                        return False
                    self.__extra_collections[index] = self.__df(json_data)
            self.__ready = True
            self.__extra_ready = True

        else:
            assert kafka_msg.index is not None, "internal error in KafkaHelper: add: index is None"

            if kafka_msg.taskId is None and kafka_msg.appId == "":  # extra collections
                if len(kafka_msg.data) != len(self.__extra_coll_to_index):
                    self.__j_app.logs_buffer.write(f"error: wrong kafka extra collections size: expected {len(self.__extra_coll_to_index)}, found {len(kafka_msg.data)}\n")
                    return False

                for coll, json_data in kafka_msg.data.items():
                    index = self.__extra_coll_to_index.get(coll)
                    if index is None:
                        self.__j_app.logs_buffer.write(f"error: wrong kafka collection: {coll}\n")
                        return False
                    self.__extra_collections[index] = self.__df(json_data)
                self.__extra_ready = True
            else:
                need_key = (kafka_msg.taskId, kafka_msg.appId, kafka_msg.index)
                if need_key not in self.__need:
                    log_warn(f"kafka add: wrong need_key: {need_key}")
                    return False
                self.__need.remove(need_key)

                i, subi = self.__start_indexes[(kafka_msg.taskId, kafka_msg.appId)]
                if self.__collections[i] is None:
                    self.__collections[i] = [[None for _ in range(self.__scale[(kafka_msg.taskId, kafka_msg.appId)])] for _ in range(len(kafka_msg.data))]
                    if self.__schemes[i] is None:
                        self.__schemes[i] = []
                    for coll in kafka_msg.data.keys():
                        self.__schemes[i].append(kafka_msg.schemes[coll])
                for j, json_data in enumerate(kafka_msg.data.values()):
                    self.__collections[i][j][kafka_msg.index - subi] = self.__df(json_data)

        if self.ready:
            self.__set_collections()
            self.__set_extra_collections()
        return True

    async def run(self):
        assert self.ready, "internal error in KafkaHelper: run for not ready"
        from malevich_app.export.api.api import single_put, input_fun, logs

        try:
            response = Response()
            logs_operation = LogsOperation(operationId=self.__j_app.operation_id, runId=self.__j_app.run_id)

            logs_data = await logs(logs_operation, response)
            kafka_info = KafkaInfo(operationId=self.__j_app.operation_id, runId=self.__j_app.run_id,
                                   taskId="" if self.__j_app.task_id is None else self.__j_app.task_id,
                                   appId=self.__j_app.app_id, hostedAppId=C.APP_ID, secret=self.__j_app.secret,
                                   type=0, success=True, logs=logs_data)
            await send_post_dag(kafka_info.model_dump_json(), KAFKA_INFO(self.__j_app.dag_host_port), operation_id=self.__j_app.operation_id)

            self.__j_app.set_index(self.__index)
            ok, schemes_names, res = await call_async_fun(lambda: input_fun(self.__j_app, [], input_logger), input_logger, self.__j_app.debug_mode, self.__j_app.logs_buffer)
            if ok:
                ok, schemes_names, res = await single_put(self.__j_app, schemes_names)

            kafka_info.type = 1
            kafka_info.success = ok
            kafka_info.logs = await logs(logs_operation, response)
            await send_post_dag(kafka_info.model_dump_json(), KAFKA_INFO(self.__j_app.dag_host_port), operation_id=self.__j_app.operation_id)
        except:
            log_error(f"kafka run error: {traceback.format_exc()}")

    async def fail(self):
        """called instead of run on error"""
        if self.ready:
            log_error("internal error in KafkaHelper: fail for ready")

        from malevich_app.export.api.api import logs

        response = Response()
        logs_operation = LogsOperation(operationId=self.__j_app.operation_id, runId=self.__j_app.run_id)

        logs_data = await logs(logs_operation, response)
        kafka_info = KafkaInfo(operationId=self.__j_app.operation_id, runId=self.__j_app.run_id,
                               taskId="" if self.__j_app.task_id is None else self.__j_app.task_id,
                               appId=self.__j_app.app_id, hostedAppId=C.APP_ID, secret=self.__j_app.secret,
                               type=1, success=False, logs=logs_data)
        await send_post_dag(kafka_info.model_dump_json(), KAFKA_INFO(self.__j_app.dag_host_port), operation_id=self.__j_app.operation_id)

    # FIXME:  self.producer.send - 5 sec first time
    async def produce(self, dfs_schemes: List[Tuple[Union[pd.DataFrame, BaseModel], Optional[str]]]) -> List[Collection]:
        assert self.ready, "internal error in KafkaHelper: send for not ready"

        results = {}
        schemes = {}
        for df, scheme in dfs_schemes:
            if isinstance(df, Dict) or isinstance(df, List):
                res = df
            elif issubclass(df.__class__, BaseModel):
                res = df.model_dump_json()
            else:
                if self.__j_app.docker_mode == "pyspark":
                    df = df.toPandas()
                res = df.to_json()
            collection_id = str(uuid4())
            results[collection_id] = res
            schemes[collection_id] = scheme

        if self.__send_topics is None:  # only in the end
            msg = FinishKafkaMsg(operationId=self.__j_app.operation_id, runId=self.__j_app.run_id, data=results).model_dump_json()
            self.producer.send(self.__result_topic, msg.encode('utf-8'))
        else:
            msg = KafkaAppMsg(operationId=self.__j_app.operation_id, runId=self.__j_app.run_id, data=results, schemes=schemes,
                              index=self.__index, taskId=self.__j_app.task_id, appId=self.__j_app.app_id).model_dump_json()
            for topic in self.__send_topics:
                self.producer.send(topic, msg.encode('utf-8'))
        # self.producer.flush() # 5 sec - very long
        return [KafkaCollection(collection_id) for collection_id in results]
