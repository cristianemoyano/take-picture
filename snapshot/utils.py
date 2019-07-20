import json
import requests

import redis

from celery.result import AsyncResult
from requests_toolbelt.multipart.encoder import MultipartEncoder


def upload(filename):
    api_url = 'http://patent-recognizer.herokuapp.com/'
    with open(filename, 'rb') as file:
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
        except Exception:
            pass
    return "The result is not ready yet. Please wait. You can refresh this page to ask for the result."


def set_key(key, value):
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.set(key, value)


def get_key(key):
    r = redis.Redis(host='localhost', port=6379, db=0)
    value = r.get('key')
    return value
