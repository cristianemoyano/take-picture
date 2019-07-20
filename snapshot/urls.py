from django.urls import path
from snapshot import views

app_name = 'snapshot'

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path(r'result/(?P<work_id>)', views.Result.as_view(), name='result'),
]
