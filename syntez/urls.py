from django.urls import path
from . import views
from . import api_views


urlpatterns = [
    path('', views.index),
    path('api/v1/get_file', api_views.Get_file.as_view())
]
