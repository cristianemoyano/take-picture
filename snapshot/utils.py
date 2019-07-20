import os
import json
import requests

from django.conf import settings
import redis

from celery.result import AsyncResult
from requests_toolbelt.multipart.encoder import MultipartEncoder

import logging


def upload(filename):
    api_url = 'http://patent-recognizer.herokuapp.com/'
    file_path = os.path.join(settings.BASE_DIR, filename)
    with open(file_path, 'rb') as file:
        multipart_data = MultipartEncoder(
            fields={
                '': (filename, file, 'image/png'),
            },
        )
        r = requests.post(api_url, data=multipart_data, headers={'Content-Type': multipart_data.content_type})
    response = {
        'status_code': r.status_code,
        'response': r.text,
    }
    return json.dumps(response)


def get_result(work_id):
    work = AsyncResult(work_id)
    if work.ready():
        try:
            result = work.get(timeout=1)
            return result
        except Exception as e:
            logging.exception(e, exc_info=True)
    return "The result is not ready yet. Please wait. You can refresh this page to ask for the result."


def getRedisClient():
    redis_url = os.getenv('REDIS_URL', None)
    if redis_url:
        r = redis.Redis.from_url(redis_url)
    else:
        r = redis.Redis(host='localhost', port=6379, db=0)
    return r


def set_key(key, value):
    client = getRedisClient()
    client.set(key, value)


def get_key(key):
    client = getRedisClient()
    value = client.get('key')
    return value
