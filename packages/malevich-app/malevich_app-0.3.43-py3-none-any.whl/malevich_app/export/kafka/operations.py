import asyncio
import traceback
from kafka import KafkaConsumer, KafkaProducer
from malevich_app.export.abstract.abstract import KafkaAppMsg
from malevich_app.export.kafka.KafkaHelper import KafkaHelper
from malevich_app.export.secondary.LogHelper import log_error, log_warn
from malevich_app.export.secondary.State import states
from malevich_app.export.secondary.const import BOOTSTRAP_SERVICE, SLEEP_BACKGROUND_TASK_S, SOCKET_REQUEST_MAX_BYTES, \
    KAFKA_API_VERSION, KAFKA_API_VERSION_TIMEOUT, APP_ID, GROUP_ID, POOL_TIMEOUT_MS
from malevich_app.export.secondary.helpers import send_background_task

__topic = APP_ID
__producer: KafkaProducer = None
__consumer: KafkaConsumer = None
__consume = False


async def __consumer_run():
    while True:
        topic_partitions = __consumer.poll(POOL_TIMEOUT_MS)
        # print("__consumer_run", time.time())
        if topic_partitions:
            # print(f"__consumer_run {topic_partitions.keys()}")
            for messages in topic_partitions.values():
                for message in messages:
                    state = None
                    j_app = None
                    try:
                        kafka_app_msg = KafkaAppMsg.parse_raw(message.value)
                        state = states.get(kafka_app_msg.operationId)
                        if state is None:
                            log_warn(f"kafka: wrong operationId, {kafka_app_msg.operationId}")
                            continue

                        j_app = state.j_apps.get(kafka_app_msg.runId)
                        if j_app is None:
                            log_warn(f"error kafka: wrong runId, {kafka_app_msg.runId}")
                            state.logs_buffer.write(f"error kafka: wrong runId, {kafka_app_msg.runId}\n")
                            continue

                        if not j_app.kafka_helper.add(kafka_app_msg):
                            j_app.logs_buffer.write("error: kafka add collections failed\n")
                            send_background_task(j_app.kafka_helper.fail, logs_buffer=j_app.logs_buffer)
                            await asyncio.sleep(SLEEP_BACKGROUND_TASK_S)
                        elif j_app.kafka_helper.ready:
                            send_background_task(j_app.kafka_helper.run, logs_buffer=j_app.logs_buffer)
                            await asyncio.sleep(SLEEP_BACKGROUND_TASK_S)
                    except:
                        log_error(f"kafka consumer_run fail: {traceback.format_exc()}")
                        if j_app is not None:
                            j_app.logs_buffer.write("kafka fail\n")
                            send_background_task(j_app.kafka_helper.fail, logs_buffer=j_app.logs_buffer)
                            await asyncio.sleep(SLEEP_BACKGROUND_TASK_S)
                        elif state is not None:
                            state.logs_buffer.write("kafka fail\n")


def init(retries: int = 3, bootstrap_servers=BOOTSTRAP_SERVICE):
    global __producer, __consumer
    for _ in range(retries):
        try:
            __producer = KafkaProducer(bootstrap_servers=bootstrap_servers, max_request_size=SOCKET_REQUEST_MAX_BYTES, api_version=KAFKA_API_VERSION, api_version_auto_timeout_ms=KAFKA_API_VERSION_TIMEOUT)
            break
        except:
            log_warn("KafkaProducer retry")
    assert __producer is not None, "creating kafka producer failed"
    KafkaHelper.producer = __producer

    for _ in range(retries):
        try:
            __consumer = KafkaConsumer(__topic, bootstrap_servers=bootstrap_servers, group_id=GROUP_ID, max_partition_fetch_bytes=SOCKET_REQUEST_MAX_BYTES, api_version=KAFKA_API_VERSION, api_version_auto_timeout_ms=KAFKA_API_VERSION_TIMEOUT)
            break
        except:
            log_warn("KafkaConsumer retry")
    assert __consumer is not None, "creating kafka consumer failed"


async def consume():
    global __consume
    if __consume:
        return
    __consume = True

    send_background_task(__consumer_run, new_loop=True)
    await asyncio.sleep(SLEEP_BACKGROUND_TASK_S)
