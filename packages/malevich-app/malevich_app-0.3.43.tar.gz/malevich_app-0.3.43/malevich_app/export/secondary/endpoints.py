import malevich_app.export.secondary.const as C

# dag-manager
MONGO_LOAD = lambda host: f"{host}/mongo/load"
GET_KEYS_VALUES_ALL = lambda host: f"{host}/keys_values/get/all"
GET_KEYS_VALUES_RAW = lambda host: f"{host}/keys_values/get/raw"
GET_KEYS_VALUES = lambda host: f"{host}/keys_values/get"
POST_KEYS_VALUES = lambda host: f"{host}/keys_values/post"
POST_KEYS_VALUES_RAW = lambda host: f"{host}/keys_values/post/raw"
DELETE_KEYS_VALUES_ALL = lambda host: f"{host}/keys_values/delete/all"
GET_OBJ_STORAGE_KEYS = lambda host: f"{host}/object_storage/get/keys"
GET_OBJ_STORAGE_ALL = lambda host: f"{host}/object_storage/get/all"
GET_OBJ_STORAGE = lambda host: f"{host}/object_storage/get"
POST_OBJ_STORAGE = lambda host: f"{host}/object_storage/post"
POST_PRESIGNED_OBJ_STORAGE = lambda host: f"{host}/object_storage/presigned"
DELETE_OBJ_STORAGE = lambda host: f"{host}/object_storage/delete"
SYNCHRONIZE = lambda host: f"{host}/synchronize"
MESSAGE = lambda host: f"{host}/message"
KAFKA_INFO = lambda host: f"{host}/kafka_info"
STREAM_LOGS = lambda host: f"{host}/stream_logs"
OBJECTS = lambda host: f"{host}/objects"
COLLECTIONS = lambda host: f"{host}/collections"
PIPELINE_FINISH = lambda host: f"{host}/pipeline/finish"

# core
DOCS_COLLECTION = None
COPY_COLLECTION = None
OUTSIDE_COLLECTION = None
QUERY = None
MAPPING_SCHEMES_NAMES = None
MAPPING_SCHEMES_RAW = None
RUN_SCHEME = None
CREDENTIALS = None
ERROR_INFO = None


def reset_core_endpoints():
    global DOCS_COLLECTION, COPY_COLLECTION, OUTSIDE_COLLECTION, QUERY, MAPPING_SCHEMES_NAMES, MAPPING_SCHEMES_RAW, RUN_SCHEME, CREDENTIALS, ERROR_INFO
    DOCS_COLLECTION = f"{C.CORE_HOST_PORT}/internal/run/collection/data"
    COPY_COLLECTION = f"{C.CORE_HOST_PORT}/internal/run/collection/copyReal"
    OUTSIDE_COLLECTION = f"{C.CORE_HOST_PORT}/internal/run/collection/outside"
    QUERY = f"{C.CORE_HOST_PORT}/internal/run/collection/query"
    MAPPING_SCHEMES_NAMES = f"{C.CORE_HOST_PORT}/internal/run/mapping/schemes/names"
    MAPPING_SCHEMES_RAW = f"{C.CORE_HOST_PORT}/internal/run/mapping/schemes/raw"
    RUN_SCHEME = f"{C.CORE_HOST_PORT}/internal/run/schemes"
    CREDENTIALS = f"{C.CORE_HOST_PORT}/internal/run/credentials"
    ERROR_INFO = f"{C.CORE_HOST_PORT}/internal/run/errorInfo"

reset_core_endpoints()
