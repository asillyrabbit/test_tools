from django.urls import path
from . import views

app_name = 'config'
urlpatterns = [
    path('', views.index, name='index'),
]