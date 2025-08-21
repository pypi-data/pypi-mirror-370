import json
import os.path
import shutil
from pathlib import Path
import pandas as pd
import uuid
from typing import Dict, Optional, Tuple, List, Set, Union, Any
import malevich_app.export.secondary.const as C
from malevich_app.export.abstract.abstract import LocalRunStruct, LocalScheme
from malevich_app.export.secondary.collection.JsonCollection import JsonCollection
from malevich_app.local.LocalKV import LocalKV
from malevich_app.local.utils import filter_columns, scheme_json_columns, schemes_mapping_by_columns, remapping, \
    remapping_by_df


class LocalStorage:
    def __init__(self, local_settings: LocalRunStruct, schemes: Dict[str, Tuple[List[str], Set[str]]], local_schemes: Optional[Dict[str, LocalScheme]] = None):
        self.__data: Dict[str, str] = local_settings.data   # id to data path
        self.__results_dir = local_settings.results_dir
        self.fail_dir = local_settings.fail_dir if local_settings.fail_dir is not None or local_settings.results_dir is None else os.path.join(local_settings.results_dir, "fail_info")
        self.__login = local_settings.login
        self.__schemes = schemes
        self.__local_schemes = local_schemes or {}
        self.__kv = LocalKV()
        self.__check()

    def __check(self):
        for path in self.__data.values():
            assert os.path.exists(path), f"path \"{path}\" not exist"
        if self.__results_dir is not None:
            assert os.path.isdir(self.__results_dir), f"path \"{self.__results_dir}\" not exist"

    def _schemes_consider(self, schemes: Dict[str, LocalScheme]):
        for name, scheme in schemes.items():
            self.__schemes[name] = (scheme.keys, scheme.optionalKeys)

    @property
    def kv(self) -> LocalKV:
        return self.__kv

    def data(self, data: Optional[Union[pd.DataFrame, List, Dict]] = None, path: Optional[str] = None, id: Optional[str] = None) -> str:
        assert (data is not None) + (path is not None) == 1, "data create fail: should set data or path"

        if id is None:
            id = str(uuid.uuid4())
        assert id not in self.__data, f"data with id \"{id}\" already exist"

        if path is None:
            path = os.path.join("/tmp", id)
            if isinstance(data, pd.DataFrame):
                data.to_csv(path, header=True, index=False)
            elif isinstance(data, List) or isinstance(data, Dict):
                with open(path, 'w') as fw:
                    json.dump(data, fw)
            else:
                raise Exception(f"wrong data type: {type(data)}")
        assert os.path.exists(path), f"path \"{path}\" not exist"
        self.__data[id] = path

        return id

    def obj(self, obj_path: str, data: Optional[bytes] = None, path_from: Optional[str] = None):
        assert (data is not None) + (path_from is not None) == 1, "obj create fail: should set data or path_from"

        path = os.path.join(C.COLLECTIONS_OBJ_PATH(self.__login), obj_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        if path_from is not None:
            if Path(path_from).is_file():
                shutil.copy(path_from, path)
            elif Path(path_from).is_dir():
                shutil.copytree(path_from, path)
            else:
                raise Exception(f"path is not file or directory: {path_from}")
        else:
            with open(path, 'wb') as fw:
                fw.write(data)

    def save_data(self, operation_id: str, run_id: str, data: Union[pd.DataFrame, List, Dict], scheme: Optional[str], name: str, group_name: str, index: int, is_doc: bool):
        # ignore many values now, just save data
        id = str(uuid.uuid4())

        if is_doc:
            collection_name = "json"
            id = f"{JsonCollection.prefix}{id}"
        else:
            collection_name = "data"
        internal_path_prefix = C.COLLECTIONS_PATH(operation_id)
        internal_path = f"{internal_path_prefix}/{id}/{collection_name}"
        os.makedirs(os.path.dirname(internal_path), exist_ok=True)
        if is_doc:
            with open(internal_path, 'w') as fw:
                json.dump(data, fw)
        else:
            data.drop(["__id__", "__name__"], axis=1, errors="ignore", inplace=True)
            data.to_csv(internal_path, header=True, index=False)

        # extra save
        if self.__results_dir is not None:
            path = os.path.join(self.__results_dir, operation_id, run_id, name, str(index))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if is_doc:
                with open(f"{path}.json", 'w') as fw:
                    json.dump(data, fw)
            else:
                data.to_csv(f"{path}.csv", header=True, index=False)
        return id

    # FIXME allow not only csv later
    def get_data(self, operation_id: str, id: str, scheme: Optional[str] = None) -> Optional[str]:
        if id.startswith(JsonCollection.prefix):
            return self.__get_doc(operation_id, id)
        else:
            is_docs = scheme is not None and (scheme.startswith(C.DOC_SCHEME_PREFIX) or scheme.startswith(C.DOCS_SCHEME_PREFIX))
            if is_docs or scheme == "" or scheme == "*":
                scheme = None
            return self.__get_collection(operation_id, id, scheme, is_collection=not is_docs)

    def __get_doc(self, operation_id: str, id: str):
        internal_path_prefix = C.COLLECTIONS_PATH(operation_id)
        internal_path = f"{internal_path_prefix}/{id}/json"
        if not os.path.exists(internal_path):
            id_without_prefix = id.removeprefix(JsonCollection.prefix)
            path = self.__data.get(id_without_prefix)
            assert path is not None, f"unknown doc id: {id_without_prefix}"

            os.makedirs(os.path.dirname(internal_path), exist_ok=True)
            shutil.copyfile(path, internal_path)

    def __get_collection(self, operation_id: str, id: str, scheme: Optional[str], is_collection: bool) -> Optional[str]:
        if not is_collection:
            scheme = None

        collection_name = "data" if is_collection else "json"
        internal_path_prefix = C.COLLECTIONS_PATH(operation_id)
        internal_path = f"{internal_path_prefix}/{id}/{collection_name}"
        if os.path.exists(internal_path):
            if scheme is None:
                return None

            with open(internal_path, 'r') as f:
                columns = f.readline().rstrip().split(sep=",")

            columns = set(filter_columns(columns))
            if len(columns) == 0:
                return None

            scheme_struct = self.__schemes.get(scheme)
            assert scheme_struct is not None, f"unknown scheme: {scheme}"

            mapping = None
            columns_to, optional_columns_to = scheme_struct
            all_exists = True
            for column in columns_to:
                if column not in columns and column not in optional_columns_to:
                    all_exists = False
                    break

            if all_exists:
                if len(columns) == len(columns_to):
                    return None

                mapping = {}
                for column in columns_to:
                    if column in columns:
                        mapping[column] = column

            if mapping is None:
                # TODO add schemes mapping
                mapping = schemes_mapping_by_columns(columns, columns_to, optional_columns_to)

            new_id = str(uuid.uuid4())
            remapping(internal_path_prefix, id, new_id, mapping, collection_name)
            return new_id

        path = self.__data.get(id)
        assert path is not None, f"unknown data id: {id}"

        os.makedirs(os.path.dirname(internal_path), exist_ok=True)
        df = pd.read_csv(path)
        if is_collection:
            if scheme is not None:
                scheme_struct = self.__schemes.get(scheme)
                assert scheme_struct is not None, f"unknown scheme: {scheme}"

                if df.empty:
                    columns = scheme_struct[0]
                    df = pd.DataFrame(columns=columns)
                else:
                    columns = set(filter_columns(df.columns))
                    columns_to, optional_columns_to = scheme_struct
                    mapping = schemes_mapping_by_columns(columns, columns_to, optional_columns_to)

                    df.to_csv(internal_path, header=True, index=False)  # save base collection

                    new_id = str(uuid.uuid4())
                    remapping_by_df(df, mapping, new_path=os.path.join(internal_path_prefix, new_id, collection_name))
                    return new_id
            elif df.empty:
                df = pd.DataFrame()
            df.to_csv(internal_path, header=True, index=False)
        else:
            data = df.to_dict(orient="records")
            with open(internal_path, 'w') as fw:
                json.dump(data, fw)
        return None

    def get_mapping_schemes_raw(self, columns: List[str], scheme_to: str) -> Dict[str, str]:    # TODO allow user mapping
        scheme_struct = self.__schemes.get(scheme_to)
        assert scheme_struct is not None, f"unknown scheme: {scheme_to}"

        columns_to, optional_columns_to = scheme_struct
        mapping = schemes_mapping_by_columns(set(columns), columns_to, optional_columns_to)
        return mapping

    def get_mapping_schemes(self, scheme_from: str, scheme_to: str) -> Dict[str, str]:          # TODO allow user mapping
        scheme_struct = self.__schemes.get(scheme_from)
        assert scheme_struct is not None, f"unknown scheme: {scheme_from}"

        return self.get_mapping_schemes_raw(scheme_struct[0], scheme_to)

    def scheme(self, name: str, scheme_json: Optional[Union[str, Dict[str, Any]]] = None, path: Optional[str] = None):
        assert (scheme_json is not None) + (path is not None) == 1, "scheme create fail: should set scheme_json or path"

        if path is not None:
            with open(path, 'r') as fr:
                scheme_json = fr.read()
        res = scheme_json_columns(scheme_json)
        self.__schemes[name] = res
        self.__local_schemes[name] = LocalScheme(keys=res[0], optionalKeys=res[1])

    def schemes(self, dir_path: str):
        assert os.path.isdir(dir_path), "wrong path - expected dir with schemes json"
        for name in os.listdir(dir_path):
            if name.endswith(".json"):
                self.scheme(name[:-5], path=os.path.join(dir_path, name))
