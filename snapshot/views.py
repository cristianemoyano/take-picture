import base64

from PIL import Image
from io import BytesIO

from django.views.generic import View
from django.shortcuts import render
from django.http import HttpResponse

from django.http import HttpResponseRedirect
from django.urls import reverse

from snapshot.utils import get_result, set_key
from snapshot.tasks import upload_task

snapshot_key = 'snapshot:work_id'


class Home(View):
    template_name = 'snapshot/index.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})

    def post(self, request, *args, **kwargs):
        data = request._post.get('image_input').split('data:image/png;base64,')[1]
        image = Image.open(BytesIO(base64.b64decode(data)))
        filename = "img.png"
        image.save(filename, "PNG")
        work = upload_task.delay(filename)
        set_key(snapshot_key, work.id)
        return HttpResponseRedirect(reverse('snapshot:result', kwargs={'work_id': work.id}))


class Result(View):

    def get(self, request, *args, **kwargs):
        result = get_result(kwargs.get('work_id'))
        return HttpResponse(result)
