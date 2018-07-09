from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.models import User
from .models import *

### Done ###
def index(request):
    template = 'diary/index.html'

    try:
        message = request.session['message']
    except(KeyError):
        message = None;

    if message:
        del request.session['message']

        if message[0] == 'success':
            return render(request, template, {'success':message[1]})
        elif message[0] == 'warn':
            return render(request, template, {'warn':message[1]})
        elif message[0] == 'error':
            return render(request, template, {'error':message[1]})
        else:
            return render(request, template, {'info':message[1]})

    else:
        return render(request, template, {})

def other(request):
    request.session['message'] = ['warn','Ops. Hľadaná stránka nebola nájdená.']

    return redirect('diary:index')
############

### Not done ###
def log_in(request):
    pass

def log_out(request):
    logout(request)
    request.session['message'] = ['success','Bola si úspešne odhlásená.']

    return redirect('diary:index')

def register(request):
    pass

def home(request):
    pass

def profile(request):
    pass

def change_profile(request):
    pass

def graph(request):
    pass

def my_diary(request):
    pass

def view_action(request):
    pass

def add_action(request):
    pass
################

### Staff ###
def activities(request):
    pass

def add_activity(request):
    pass

def all_diaries(request):
    pass

def not_my_diary(request):
    pass

def not_my_action(request):
    pass
#############
