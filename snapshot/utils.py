import os
import time
import json
import hashlib
import requests
from urllib.request import urlopen
import logging
import base64
from io import BytesIO

from celery.result import AsyncResult
import dropbox
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import redis
from requests_toolbelt.multipart.encoder import MultipartEncoder

PUBLIC_URL_KEY = 'snapshot:public_url'
FILE_NAME = "img.png"


def decode_image(data):
    return BytesIO(base64.b64decode(data))


def save_file(name, file):
    fs = FileSystemStorage()
    fs.name = fs.save(name, file)
    return fs


def get_unique_file_name(file_name):
    timestamp = str(int(time.time()))
    h = hashlib.sha224(timestamp.encode('utf-8')).hexdigest()
    return '{hash}-{file}'.format(
        hash=h,
        file=file_name,
    )


def upload_file_dropbox_and_get_public_url(path_file, file_name_saved):
    with open(path_file, 'rb') as file:
        dbx = dropbox.Dropbox(settings.DROPBOX_ACCESS_TOKEN)
        res = dbx.files_upload(
            file.read(), '/' + file_name_saved,
            dropbox.files.WriteMode.add
        )
        create_shared_link = dbx.sharing_create_shared_link(res.path_display)
        link = create_shared_link.url
        url, dl = link.split('?')
        public_url = url + '?dl=1'
    os.remove(path_file)
    set_key(PUBLIC_URL_KEY, public_url)
    return public_url


def upload_image_remote(data):
    file = decode_image(data)
    file_name = FILE_NAME
    unique_name = get_unique_file_name(file_name)
    fs = save_file(unique_name, file)
    path_file = fs.location + '/' + fs.name
    # dropbox
    return upload_file_dropbox_and_get_public_url(path_file, fs.name)


def recognize_license_place(url):
    def parse_response(response):
        text = response.json()
        if text:
            return {
                'license_place': text.get('plate'),
                'status_code': response.status_code,
                'response': response.text,
            }
        return {
            'license_place': 'Not recognized.',
            'status_code': response.status_code,
            'response': text,
        }
    api_url = 'http://patent-recognizer.herokuapp.com/'
    with urlopen(url) as file:
        multipart_data = MultipartEncoder(
            fields={
                '': (FILE_NAME, file.read(), 'image/png'),
            },
        )
        response = requests.post(api_url, data=multipart_data, headers={'Content-Type': multipart_data.content_type})
    return json.dumps(parse_response(response))


def upload_image_and_recognize_license_place(data):
    public_url = upload_image_remote(data)
    return recognize_license_place(public_url)


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
    value = client.get(key)
    return value
