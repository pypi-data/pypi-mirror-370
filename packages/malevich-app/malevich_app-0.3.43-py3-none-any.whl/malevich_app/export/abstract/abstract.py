from typing import Optional, Any, List, Union, Dict, Tuple, Set
from pydantic import BaseModel

from malevich_app.export.abstract.pipeline import Pipeline

DOC = str


class Image(BaseModel):
    ref: str
    tag: Optional[str] = None
    user: Optional[str] = None
    token: Optional[str] = None


class App(BaseModel):
    appId: str
    inputId: Optional[str]
    processorId: str
    outputId: Optional[str]
    cfg: Optional[str]
    image: Image
    extraCollectionsFrom: Optional[Dict[str, List[str]]] = None


class AnyInit(BaseModel):
    cfg: Optional[str] = None   # should set in init or in run
    infoUrl: Optional[str] = None
    debugMode: bool
    profileMode: Optional[str] = None
    operationId: str
    dagHost: str


class InitPipeline(AnyInit):
    login: str
    pipeline: Pipeline
    schemesNames: List[str]
    image: Image
    index: int
    hash: str
    processorIds: Set[str]
    secret: str
    singlePod: bool
    continueAfterProcessor: bool    # TODO use it
    saveFails: bool = True
    # loop/cluster structs
    loopOrderDeps: Dict[str, List[str]] = {}
    alternativeLoopOrderDeps: Dict[str, Set[str]] = {}
    loopIterationIncrement: Dict[str, Set[str]] = {}        # increment iteration for x -> y (for y in set)
    clusters: Dict[str, Set[int]] = {}
    bindIdsList: List[str] = []


class Init(AnyInit):
    login: str
    app: App
    taskId: Optional[str]
    isInitApp: bool     # there are no apps before it
    schemesNames: List[str]
    scale: int
    hash: str
    secret: str
    singlePod: bool
    continueAfterProcessor: bool    # continue without run output function (it run separately), app success even if output fail


class AppsBeforeInfo(BaseModel):
    indexStart: int
    indexEnd: int
    taskId: Optional[str]
    appId: str


class AppsAfterInfo(BaseModel):
    topics: List[str]


class KafkaInitRun(BaseModel):
    index: int
    appsBeforeInfo: List[AppsBeforeInfo]
    appsAfterInfo: Optional[AppsAfterInfo]


class InitRun(AnyInit):
    runId: str
    kafkaInitRun: Optional[KafkaInitRun]


class SchemesNames(BaseModel):
    schemesNames: List[str]


class GetAppInfo(SchemesNames):
    operationId: str


class GetAppFunctionsInfo(GetAppInfo):
    image: Image


class FunctionInfo(BaseModel):
    id: str
    name: str
    arguments: List[Tuple[str, Optional[str]]]
    finishMsg: Optional[str]
    doc: Optional[str]
    cpuBound: bool
    tags: Optional[Dict[str, str]] = None


class InputFunctionInfo(FunctionInfo):
    collectionsNames: Optional[List[str]] = None
    extraCollectionsNames: Optional[List[str]] = None
    query: Optional[str] = None
    mode: str


class ProcessorFunctionInfo(FunctionInfo):
    isStream: bool
    contextClass: Optional[Dict[str, Any]] = None


class OutputFunctionInfo(FunctionInfo):
    collectionOutNames: Optional[List[str]]


class ConditionFunctionInfo(FunctionInfo):
    pass


class InitInfo(BaseModel):
    id: str
    enable: bool
    tl: Optional[int]
    prepare: bool
    argname: Optional[str]
    doc: Optional[str]
    cpuBound: bool
    tags: Optional[Dict[str, str]] = None


class AppFunctionsInfo(BaseModel):
    inputs: Dict[str, InputFunctionInfo] = {}
    processors: Dict[str, ProcessorFunctionInfo] = {}
    outputs: Dict[str, OutputFunctionInfo] = {}
    conditions: Dict[str, ConditionFunctionInfo] = {}
    schemes: Dict[str, str] = {}
    inits: Dict[str, InitInfo] = {}
    logs: Optional[str] = None
    version: Optional[str] = None


class FunMetadata(BaseModel):
    runId: Optional[str]
    operationId: str


class InputCollections(FunMetadata):
    data: List[Tuple[str, ...]]
    index: int
    singleRequest: bool


class Run(FunMetadata):
    data: List[Tuple[str, ...]]
    index: int


class IntPair(BaseModel):
    first: int
    second: int


class PipelineStructureUpdate(BaseModel):
    iterationsConnection: Dict[int, Dict[int, Dict[int, int]]] = {}
    iterationsTransition: Dict[int, Dict[int, Dict[int, int]]] = {}
    clusterNextIteration: Dict[int, int] = {}
    zeroIterationMapping: Dict[str, int] = {}
    appWaitCounts: Optional[Dict[int, Dict[int, Dict[str, IntPair]]]] = None                                            # cluster num -> cluster index -> bind_id -> (bind_id iteration, count)
    appWaitCountsConditions: Optional[Dict[int, Dict[int, Dict[str, Dict[int, Dict[int, int]]]]]] = None                # cluster num -> cluster index -> bind_id -> bind_id iteration -> num -> count
    alternativeAppWaitCounts: Optional[Dict[int, Dict[int, Dict[str, Dict[int, Dict[str, Dict[int, int]]]]]]] = None    # cluster num -> cluster index -> bind_id -> bind_id iteration -> name -> num -> count


class RunPipeline(FunMetadata):
    iteration: int
    bindId: str         # that should start, mb other also start
    data: Optional[Dict[str, Tuple[str, ...]]] = None   # bindId to its results
    conditions: Optional[Dict[str, bool]] = None
    structureUpdate: Optional[PipelineStructureUpdate] = None
    bindIdsDependencies: Optional[Dict[str, int]] = None


class RunStream(BaseModel):
    operationId: str
    runId: str
    bindId: str     # empty for tasks

# data


class SchemesMappingNames(BaseModel):
    operationId: str
    schemeFromName: str
    schemeToName: str


class SchemesMappingRaw(BaseModel):     # schemeToName or schemeToId not None
    operationId: str
    columns: List[str]
    schemeToName: Optional[str] = None
    schemeToId: Optional[str] = None


class Credentials(BaseModel):
    operationId: str
    credentialsId: str


class DBQuery(BaseModel):
    url: str
    username: str
    password: str
    query: str


class FixScheme(BaseModel):
    schemeName: str
    mode: str = "not_check"


class QueryCollection(BaseModel):
    operationId: str
    query: str


class CollectionOutside(BaseModel):
    operationId: str
    appId: str
    type: str
    query: DBQuery
    fixScheme: Optional[FixScheme]


class CollectionAndScheme(BaseModel):
    operationId: str
    collectionId: str
    hostedAppId: str
    secret: str
    fixScheme: Optional[FixScheme]


class TempRunScheme(BaseModel):
    operationId: str
    data: str
    name: str
    prefix: bool = True

# dag extra data


class Keys(BaseModel):
    operationId: str
    data: List[str]
    runId: Optional[str] = None
    hostedAppId: str
    secret: str


class KeysWithSynchronize(Keys):
    synchronize: bool = True
    local: bool = False


class KeysPresigned(Keys):
    presigned: Optional[int]


class Presigned(BaseModel):
    operationId: str
    data: List[str]
    presigned: Optional[int]
    hostedAppId: str
    secret: str


class KeysValues(BaseModel):
    operationId: str
    data: Dict[str, Any]
    runId: Optional[str] = None
    hostedAppId: str
    secret: str


class Operation(BaseModel):
    operationId: str


class LogsOperation(Operation):
    runId: Optional[str] = None


class OperationWithRun(Operation):
    runId: Optional[str] = None
    hostedAppId: str
    secret: str


class OperationWithRunWithKey(OperationWithRun):
    key: str


class Info(BaseModel):
    operationId: str
    data: str
    infoType: str


class DocsCollectionRun(BaseModel):
    operationId: str
    runId: str
    data: List[DOC]
    fixScheme: Optional[FixScheme]
    name: Optional[str] = None
    groupName: Optional[str] = None
    metadata: Optional[str] = None
    index: int
    isDoc: bool = False


class CollectionCopy(BaseModel):
    operationId: str
    runId: str
    collectionId: str
    name: Optional[str] = None
    index: int
    groupName: Optional[str] = None


class AppSettings(BaseModel):
    taskId: Optional[str] = None
    appId: str
    saveCollectionsName: Optional[List[str]] = None


class Cfg(BaseModel):
    collections: Dict[str, Union[str, Dict[str, Any]]] = {}
    different: Dict[str, str] = {}
    schemes_aliases: Dict[str, str] = {}
    msg_url: Optional[str] = None
    init_apps_update: Dict[str, bool] = {}
    app_settings: List[AppSettings] = []
    email: Optional[str] = None


class KafkaMsg(BaseModel):
    operationId: str
    runId: str
    data: Dict[str, str]            # collection_id (that in cfg) to json data
    metadata: Dict[str, str] = {}   # collection_id (that in cfg) to json metadata
    index: Optional[int]
    taskId: Optional[str]
    appId: str


class KafkaAppMsg(KafkaMsg):
    schemes: Optional[Dict[str, Optional[str]]]


class FinishKafkaMsg(BaseModel):
    operationId: str
    runId: str
    data: Dict[str, str]


class Message(BaseModel):
    operationId: str
    type: str = "gmail"
    receivers: List[str]
    subject: Optional[str]
    message: str
    hostedAppId: str
    secret: str


class ResponseResult(BaseModel):
    result: str = ""


class OSGetKeys(BaseModel):
    operationId: str
    local: bool
    hostedAppId: str
    secret: str
    allApps: bool


class OSGetBatch(Keys):
    force: bool
    allApps: bool


class OSGetAll(BaseModel):
    operationId: str
    local: bool
    force: bool
    hostedAppId: str
    secret: str
    allApps: bool


class LogsResult(BaseModel):
    data: str = ""                  # logs for operation_id or error
    logs: Dict[str, str] = {}       # logs by run_id
    userLogs: Dict[str, str] = {}   # logs by run_id (from context.logger)


class LogsResultExtended(LogsResult):
    taskId: Optional[str]
    appId: str
    index: int


class LogsResults(BaseModel):
    data: Dict[str, LogsResultExtended] = {}    # LogsResultExtended by operation_id


class SynchronizeSettings(BaseModel):
    operationId: str
    runId: Optional[str] = None
    paths: List[str]
    hostedAppId: str
    secret: str


class KafkaInfo(BaseModel):
    operationId: str
    runId: str
    taskId: str
    appId: str
    hostedAppId: str
    secret: str
    type: int
    success: bool
    logs: LogsResult


class Collection(BaseModel):
    operationId: str
    id: str
    isDoc: bool
    data: str
    metadata: Optional[str]
    scheme: Optional[FixScheme]
    mapping: Optional[Dict[str, str]] = None


class Objects(BaseModel):
    operationId: str
    runId: Optional[str]
    paths: List[str]        # mb not exist paths


class PipelineApp(BaseModel):
    processorId: Optional[str] = None
    outputId: Optional[str] = None
    conditionId: Optional[str] = None
    image: Image


class PipelineAppFinished(BaseModel):
    operationId: str
    runId: str
    bindId: str
    index: int
    iteration: int
    collections: Optional[List[str]]
    branch: Optional[bool]
    ok: bool
    structureUpdate: PipelineStructureUpdate
    hash: str   # for dm reload


class LocalRunStruct(BaseModel):
    data: Dict[str, str] = {}
    import_dirs: List[str]

    login: str = "test"
    workdir: Optional[str] = None
    appsdir: Optional[str] = None
    mount_path: Optional[str] = None
    mount_path_obj: Optional[str] = None
    results_dir: Optional[str] = None
    fail_dir: Optional[str] = None
    with_import_restrictions: bool = True


class LocalScheme(BaseModel):
    keys: List[str]
    optionalKeys: Set[str]


class FailStructure(BaseModel):
    operationId: str
    runId: str
    bindId: str
    funId: str
    iteration: int
    isProcessor: bool = True
    trace: str
    errType: str
    errArgs: List[str]
    isMalevichErr: bool
    cfg: Optional[Dict[str, Any]]
    schemes: Optional[Dict[str, LocalScheme]]   # local schemes
    args: List[List[Union[Union[str, List[str]], List[Union[str, List[str]]]]]]
    argsNames: List[str]


class WSInitSettings(BaseModel):
    id: str
    core_host: str
    core_port: str  # int
    save_df_format: str


class WSMessage(BaseModel):
    operationId: str
    payload: Optional[str] = None
    error: Optional[str] = None
    operation: str
    id: str


class WSObjectsReq(BaseModel):
    operationId: str
    runId: Optional[str] = None
    asset: bool = False
    payload: str


class WSContinueReq(BaseModel):
    operationId: str
    runId: str = None
    id: str
    payload: str


class ObjectRequest(BaseModel):
    operationId: str
    runId: Optional[str]
    hostedAppId: str
    payload: str


class CollectionsRequest(BaseModel):
    operationId: str
    asset: bool
    hostedAppId: str
    payload: str


class KVPostRawValuesDataRequest(BaseModel):
    operationId: str
    runId: Optional[str]
    key: str
    hostedAppId: str
    payload: str


class Cancel(BaseModel):
    hash: str
