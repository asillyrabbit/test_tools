from django.urls import path
from . import views

app_name = 'task'
urlpatterns = [
    path('', views.task, name='task'),
    path('update/', views.update, name='update'),
]
