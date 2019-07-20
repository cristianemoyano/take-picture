import json

from django.views.generic import View
from django.shortcuts import render
from django.http import HttpResponse

from django.http import HttpResponseRedirect
from django.urls import reverse

from snapshot.utils import get_result, set_key
from snapshot.tasks import recognize_license_plate_task

snapshot_key = 'snapshot:work_id'


class Home(View):
    template_name = 'snapshot/index.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})

    def post(self, request, *args, **kwargs):
        data = request._post.get('image_input').split('data:image/png;base64,')[1]
        work = recognize_license_plate_task.delay(data)
        set_key(snapshot_key, work.id)
        return HttpResponseRedirect(reverse('snapshot:result', kwargs={'work_id': work.id}))


class Result(View):

    def get(self, request, *args, **kwargs):
        result = get_result(kwargs.get('work_id'))
        parsed_data = json.loads(result)
        if parsed_data.get('code') == 'SUCCESSFUL':
            data = {
                'car': parsed_data.get('car'),
                'license_plate': parsed_data.get('license_plate'),
            }
            return HttpResponse(json.dumps(data))
        return HttpResponse(result)
