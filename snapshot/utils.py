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

from snapshot.models import Car
from requests_toolbelt.multipart.encoder import MultipartEncoder

PUBLIC_URL_KEY = 'snapshot:public_url'
LICENSE_PLATE_KEY = 'snapshot:license_plate'
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


def get_car(license_plate):
    try:
        car = Car.objects.get(license_plate=license_plate)
        return car
    except Car.DoesNotExist:
        return 'License plate not found.'


def recognize_license_plate(url):
    def parse_response(response):
        data = response.json()
        if data:
            license_plate = data[0].get('plate')
            set_key(LICENSE_PLATE_KEY, license_plate)
            car = get_car(license_plate)
            return {
                'code': 'SUCCESSFUL',
                'msg': 'License plate recognized.',
                'car': str(car),
                'license_plate': license_plate,
                'status_code': response.status_code,
                'response': data,
            }
        return {
            'code': 'NOT_RECOGNIZED',
            'msg': 'Not recognized.',
            'car': 'None',
            'license_plate': 'None',
            'status_code': response.status_code,
            'response': data,
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


def upload_image_and_recognize_license_plate(data):
    public_url = upload_image_remote(data)
    return recognize_license_plate(public_url)


def get_result(work_id):
    work = AsyncResult(work_id)
    if work.ready():
        try:
            result = work.get(timeout=1)
            return result
        except Exception as e:
            error = {
                'code': 'ERROR',
                'msg': "An error ocurred. Plase, try again."
            }
            logging.exception(e, exc_info=True)
            return json.dumps(error)
    default = {
        'code': 'NO_READY',
        'msg': "The result is not ready yet. Please wait. You can refresh this page to ask for the result."
    }
    return json.dumps(default)


def getRedisClient(url=None):
    if url:
        r = redis.Redis.from_url(url)
    else:
        redis_url = os.getenv('REDIS_URL', None)
        if redis_url:
            r = redis.Redis.from_url(redis_url)
        else:
            r = redis.Redis(host='localhost', port=6379, db=0)
    return r


def set_key(key, value, ex=None):
    client = getRedisClient()
    client.set(key, value, ex)


def get_key(key):
    client = getRedisClient()
    value = client.get(key)
    return value.decode("utf-8")
