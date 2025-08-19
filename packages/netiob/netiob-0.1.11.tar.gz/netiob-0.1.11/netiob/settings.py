from decouple import config

MAX_WORKERS = config("MAX_WORKERS", default=4, cast=int)
OREF0_API_SERVER_URL = config("OREF0_API_SERVER_URL", default="http://localhost:3000", cast=str)

