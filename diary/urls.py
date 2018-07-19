from django.urls import path, re_path

from . import views

app_name = 'diary'

urlpatterns = [
    ### Authentication ###
    path('diary/login', views.log_in, name='log_in'),
    path('diary/logout', views.log_out, name='log_out'),
    path('register', views.register, name='register'),
    ######################

    ### My diary ###
    path('home', views.home, name='home'),
    path('profile/me', views.profile, name='profile'),
    path('profile/me/change', views.change_profile, name='change_profile'),
    path('graph', views.graph, name='graph'),
    path('diary/my', views.my_diary, name='my_diary'),
    path('diary/action/<int:action_id>', views.view_action, name='view_action'),
    path('diary/action/add', views.add_action, name='add_action'),
    path('diary/activities', views.activities, name='activities'),
    ################

    ### Staff things ###
    path('activity/list', views.staff_activities, name='staff_activities'),
    path('diary/list', views.all_diaries, name='all_diaries'),
    path('diary/user/<str:username>/action/<int:action_id>', views.not_my_action, name='not_my_action'),
    path('diary/user/<str:username>', views.not_my_diary, name='not_my_diary'),
    path('console', views.console, name='console'),
    path('console/post', views.console_post, name='console_post'),
    ####################

    path('index', views.index, name='index'),
    path('', views.other, name='other'),
]
