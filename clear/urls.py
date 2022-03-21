from django.urls import path
from . import views

app_name = 'clear'
urlpatterns = [
    path('', views.clear, name='clear'),
    path('update/', views.update, name='update'),
]
