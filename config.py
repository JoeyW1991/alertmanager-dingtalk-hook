import os

redis_host = os.getenv('REDIS_SERVICE_HOST')
if not redis_host:
    redis_host = 'localhost'

redis_port = os.getenv('REDIS_SERVICE_PORT')
if not redis_port:
    redis_port = 6379

redis_db = os.getenv('REDIS_DB')
if not redis_db:
    redis_db = 0


redis_pssword = os.getenv('REDIS_SERVICE_PASSWORD')

RATE_LIMIT = os.getenv('RATE_LIMIT')
if not RATE_LIMIT:
    RATE_LIMIT = '20/m'

DINGTALK_TOKEN = os.getenv('DINGTALK_TOKEN')

CELERY_BROKER_URL = 'redis://{}:{}/{}'.format(redis_host, redis_port, redis_db)
CELERY_RESULT_BACKEND = 'redis://{}:{}/{}'.format(redis_host, redis_port, redis_db)
