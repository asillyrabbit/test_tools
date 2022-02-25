from django.urls import path
from . import views

app_name = 'task'
urlpatterns = [
    path('', views.task, name='task'),
    path('update/', views.update, name='update'),
    path('score/', views.score, name='score'),
    path('page/<str:month>/<str:state>/<int:page>.html', views.page, name='page'),
]
