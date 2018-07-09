from django.urls import path, re_path

from . import views

app_name = 'diary'

urlpatterns = [
    path('diary/login', views.log_in),
    path('diary/logout', views.log_out),
    path('diary/profile', views.profile),
    path('register', views.register),
    path('index', views.index),
    path('', views.other),
]

'''
    path('obdlznik/hra/', views.druzinka),
    path('obdlznik/ulohy/', views.opravovatel),
    path('obdlznik/spravca/', views.spravca),
    path('obdlznik/', views.index),
'''
