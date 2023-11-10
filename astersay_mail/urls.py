from django.urls import path
from . import views


urlpatterns = [
    path('', views.index),
    path('api/v1/send', views.Send_email.as_view())
]
