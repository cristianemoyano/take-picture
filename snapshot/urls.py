from django.urls import path
from snapshot import views

app_name = 'snapshot'

urlpatterns = [
    path('', views.RecognizeView.as_view(), name='home'),
    path('search/', views.SearchPlateByCodeView.as_view(), name='search'),
    path(r'result/(?P<work_id>)', views.ResultRecognizeView.as_view(), name='result'),
    path(r'result-plate/<plate_code>', views.ResultByCode.as_view(), name='result-plate'),
]
