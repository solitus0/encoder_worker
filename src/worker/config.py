from starlette.config import Config

config = Config(".env")

RABBITMQ_HOST = config("RABBITMQ_HOST", default=None)
RABBITMQ_USER = config("RABBITMQ_USER", default=None)
RABBITMQ_PASS = config("RABBITMQ_PASS", default=None)

RABBITMQ_ENCODE_QUEUE = config("RABBITMQ_ENCODE_QUEUE", default=None)
RABBITMQ_ENCODE_RESULTS_QUEUE = config("RABBITMQ_ENCODE_RESULTS_QUEUE", default=None)
RABBITMQ_PROBE_QUEUE = config("RABBITMQ_PROBE_QUEUE", default=None)
RABBITMQ_PROBE_RESULT_QUEUE = config("RABBITMQ_PROBE_RESULT_QUEUE", default=None)
RABBITMQ_ENCODE_PROGRESS_QUEUE = config("RABBITMQ_ENCODE_PROGRESS_QUEUE", default=None)

LOG_LEVEL = config("LOG_LEVEL", default="info")
PROGRESS_UPDATE_INTERVAL = config("PROGRESS_UPDATE_INTERVAL", default=3, cast=int)

LOG_FORMAT = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"
