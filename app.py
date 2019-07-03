# -*- coding: UTF-8 -*-

from __future__ import absolute_import

import os
import json
import requests

import config
from flask import Flask
from flask import request
from celery import Celery


app = Flask(__name__)
app.config.from_object(config)


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


celery = make_celery(app)


@celery.task(name='send_alert_dingtalk', rate_limit=app.config['RATE_LIMIT'])
def send_sync_alert(data):
    url = 'https://oapi.dingtalk.com/robot/send?access_token=%s' % app.config['DINGTALK_TOKEN']
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    print(data)
    req = requests.post(url, json.dumps(data), headers=headers)
    req = json.loads(req.content)
    if req[u'errcode'] > 0:
        print(url)
        print(req)


@app.route('/', methods=['POST', 'GET'])
def send():
    if request.method == 'POST':
        post_data_str = request.get_data()
        post_data_json = bytes2json(post_data_str)
        post_data = json2markdown(post_data_json)
        send_sync_alert.delay(post_data)
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
