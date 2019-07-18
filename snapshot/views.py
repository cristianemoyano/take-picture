import base64
import requests
from PIL import Image
from io import BytesIO
from django.views.generic import View
from django.shortcuts import render
from django.http import HttpResponse
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
    return r


class Home(View):
    template_name = 'snapshot/index.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})

    def post(self, request, *args, **kwargs):
        data = request._post.get('image_input').split('data:image/png;base64,')[1]
        image = Image.open(BytesIO(base64.b64decode(data)))
        filename = "img.png"
        image.save(filename, "PNG")
        response = upload(filename)
        return HttpResponse(response)
