from django.urls import path
from snapshot import views

urlpatterns = [
    path('', views.Home.as_view()),
]
