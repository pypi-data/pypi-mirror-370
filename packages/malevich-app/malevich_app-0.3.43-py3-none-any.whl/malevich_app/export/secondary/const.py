import os
import aiohttp
CORE_PORT = os.environ.get("CORE_PORT", "8080")
CORE_HOST = os.environ.get("CORE_HOST", "julius-core")
__kafka_host = os.environ.get("KAFKA_HOST", "julius-kafka")
__kafka_port = os.environ.get("KAFKA_PORT", "9092")
__dag_manager_port = os.environ.get("DAG_MANAGER_PORT", "8080")
__dag_manager_index = os.environ.get("DAG_MANAGER_INDEX", "00000")
IS_EXTERNAL = os.environ.get("EXTERNAL_APP", "false") == "true"
ALLOW_KAFKA = os.environ.get("ALLOW_KAFKA", "false") == "true"
SAVE_DF_FORMAT = os.environ.get("SAVE_DF_FORMAT", "csv")
LOGS_STREAM_DELAY_S = float(os.environ.get("LOGS_STREAM_DELAY", "0.5"))     # in seconds
LOGS_STREAMING = LOGS_STREAM_DELAY_S >= 0
WAIT_DELAY_S = float(os.environ.get("WAIT_DELAY", "0.1"))                   # in seconds
STRICT_APP_CFG_TYPE = os.environ.get("STRICT_APP_CFG_TYPE", "true") == "true"
IMAGE_TAG = os.environ.get("IMAGE_TAG", "")
assert SAVE_DF_FORMAT in ["parquet", "feather", "pickle", "csv"], f"wrong SAVE_DF_FORMAT: {SAVE_DF_FORMAT}"

ENV = {"CORE_PORT": CORE_PORT, "CORE_HOST": CORE_HOST, "KAFKA_HOST": __kafka_host, "KAFKA_PORT": __kafka_port, "DAG_MANAGER_PORT": __dag_manager_port}
IS_LOCAL = True     # is local runner

# settings
FINISH_SUBJ = "Malevich. Finish message"
SLEEP_BACKGROUND_TASK_S = 0.01
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

# internal
DEFAULT_CONTINUE_ID = "continue"
TEMP_OBJ_DIR = "temp_obj"
TEMP_FILES = "__files"
DAG_HOST = "malevich-dag-manager"
DAG_PVC = "pvc-dag-manager"
DOC_SCHEME_PREFIX = "$doc_"
DOCS_SCHEME_PREFIX = "$docs_"
WORKDIR = "/malevich"
APPS_DIR = os.environ.get("APPS_DIR", "apps")
APP_DIR = f"{WORKDIR}/{APPS_DIR}"
REGISTER_RAISE_ON_ERROR = os.environ.get("REGISTER_RAISE_ON_ERROR", "false") == "true"
MOUNT_PATH = os.environ.get("MOUNT_PATH", "/tmp/mnt")
MOUNT_PATH_OBJ = os.environ.get("MOUNT_PATH_OBJ", "/tmp/mnt_obj")
AIOHTTP_TIMEOUT = aiohttp.ClientTimeout(total=365 * 24 * 60 * 60)   # year
COLLECTIONS_PATH = lambda operation_id: f"{MOUNT_PATH}/{operation_id}/collections"
STORAGE_PATH = lambda operation_id: f"{MOUNT_PATH}/{operation_id}/storage"
SCHEMES_PATH = lambda operation_id: f"{MOUNT_PATH}/{operation_id}/schemes"
COLLECTIONS_OBJ_PATH = lambda login: f"{MOUNT_PATH_OBJ}/{login}"
EXTERNAL_PATH = os.environ.get("EXTERNAL_PATH", "/external")        # used for external app
INPUT_EXTERNAL_PATH = f"{EXTERNAL_PATH}/inputs"
CONTEXT_TYPE = "Context"    # type name
CONTEXT = (CONTEXT_TYPE,)
LOG_SEPARATOR = "\\\n"   # some kind of terrible non-meeting thing, then to replace it back to '\n'
ALLOW_AUTO_CREATE_TOPICS = False     # from kafka settings
## profile
DELIMITER = "-" * 50
START = "start"
END = "end"
FAILS_DIR = os.environ.get("FAILS_DIR", "fails")

# kafka
POOL_TIMEOUT_MS = 1000      # 1 sec
BOOTSTRAP_SERVICE = f"{__kafka_host}:{__kafka_port}"
SOCKET_REQUEST_MAX_BYTES = int(os.environ.get("SOCKET_REQUEST_MAX_BYTES", "104857600"))  # 100 mb
KAFKA_API_VERSION = None
KAFKA_API_VERSION_TIMEOUT = 5000    # 5 sec
GROUP_ID = "julius-apps"

# requests const
WS = None
WS_SEND = []
WS_LOOP = None
__CORE_PROXY_PREFIX = "api/v1/proxy/dag-manager"
APP_ID = os.environ.get("APP_ID", "app")
CORE_HOST_PORT = f"http://{CORE_HOST}:{CORE_PORT}"
DAG_HOST_PORT = lambda host: "" if WS is not None else f"http://{host}:{__dag_manager_port}" if not IS_EXTERNAL else f"{CORE_HOST_PORT}/{__CORE_PROXY_PREFIX}/{__dag_manager_index}"
WRONG_OPERATION_ID = "wrong operation id"
RETURN_OK = "OK"
RETURN_FAIL = "FAIL"
CHUNK_SIZE = 32768
DEFAULT_HEADERS = {'Content-type': 'application/json', 'Accept': 'application/json'}
