from django.urls import path
from . import views

app_name = 'operate'
urlpatterns = [
    path('', views.bugs, name='bugs'),
    path('search/', views.search, name='search'),
    path('clear/', views.clear, name='clear'),
    path('bugs/', views.bugs, name='bugs'),
    path('download/', views.download, name='download'),
    path('update/', views.update, name='update'),
    path('state/', views.state, name='state'),
    path('qrcode/', views.qrcode, name='qrcode'),
    path('recode/', views.recode, name='recode'),
    path('oplat/', views.oplat, name='oplat'),
    path('platopt/', views.platopt, name='platopt'),
    path('querysales/', views.querysales, name='querysales'),
    path('modmonth/', views.modmonth, name='modmonth'),
    path('postatus/', views.postatus, name='postatus'),
    path('newbugs/', views.newbugs, name='newbugs'),
    path('qmodule/', views.qmodule, name='qmodule'),
]
