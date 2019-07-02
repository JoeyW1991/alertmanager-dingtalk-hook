import os

redis_host = os.getenv('REDIS_SERVICE_HOST')
if not redis_host:
    redis_host = 'localhost'

redis_port = os.getenv('REDIS_SERVICE_PORT')
if not redis_port:
    redis_port = 6379

send_limit = os.getenv('SEND_LIMIT')
if send_limit:
    send_limit = int(send_limit)
else:
    send_limit = 20

dingtalk_token = os.getenv('DINGTALK_TOKEN')
redis_key_pre = 'alert-dingtalk-' + dingtalk_token[-9: -1] + '-'
redis_key_index_name = redis_key_pre + 'index'
