# -*- coding: UTF-8 -*-

import json
import requests

import config

from time import sleep
from flask import Flask
from flask import request
from redis import Redis


app = Flask(__name__)
redis = Redis(host=config.redis_host, port=config.redis_port,
              password=config.redis_pssword)


def send_data(data):
    for i in range(60):
        index_value = redis.get(config.redis_key_index_name)
        if not index_value:
            index = 0
        else:
            index = int(index_value)
        index = (index + 1) % config.send_limit
        key_name = config.redis_key_pre + str(index)
        last_send = redis.get(key_name)
        if not last_send:
            redis.set(config.redis_key_index_name, index, 120)
            redis.set(key_name, '1', 60)
            send_alert(data)
            return "send sess"
        else:
            print(key_name, last_send, i)
        sleep(5)
    print('time out')


@app.route('/', methods=['POST', 'GET'])
def send():
    if request.method == 'POST':
        post_data_str = request.get_data()
        post_data_json = bytes2json(post_data_str)
        post_data = json2markdown(post_data_json)
        send_data(post_data)
        return 'success'
    else:
        return 'weclome to use prometheus alertmanager dingtalk webhook server!'


def bytes2json(data_bytes):
    data = data_bytes.decode('utf8').replace("'", '"')
    return json.loads(data)


def json2markdown(data):
    markdown = {
        'title': data['commonLabels']['alertname']
    }

    text = '# {}\n'.format(markdown['title'])
    status = str(data['status'])
    text = text + '## 状态: {}\n'.format(status)

    if 'commonAnnotations' in data:
        annotation = ''
        for key, value in data['commonAnnotations'].items():
            annotation = annotation + '- {}: {}\n'.format(key, str(value))
        text = text + '## 注释: \n{}\n'.format(annotation)

    if 'commonLabels' in data:
        labels = ''
        lebel_ignore = ['endpoint', 'namespace', 'ZoneId', 'prometheus', 'alertname', 'pod', 'service']
        for key, value in data['commonLabels'].items():
            if key not in lebel_ignore:
                labels = labels + '- {}: {}\n'.format(key, str(value))
        text = text + '## 标签: \n{}'.format(labels)

    markdown['text'] = text

    postdata = {
        'msgtype': 'markdown',
        'markdown': markdown
    }

    return postdata


def send_alert(data):
    url = 'https://oapi.dingtalk.com/robot/send?access_token=%s' % config.dingtalk_token
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    req = requests.post(url, json.dumps(data), headers=headers)
    req = json.loads(req.content)
    if req[u'errcode'] > 0:
        print(req)


if __name__ == '__main__':
    if not config.dingtalk_token:
        print('you must set DINGTALK_TOKEN env')
        exit()
    app.run(host='0.0.0.0', port=5000)
