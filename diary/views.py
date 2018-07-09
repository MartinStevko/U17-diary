from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.models import User
from .models import *

### Done ###
def log_first():
    request.session['message'] = ['info','Stránka, ktorú chceš navštíviť vyžaduje prihlásenie. Najprv sa prihlás.']

    return redirect('diary:index')

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

def home(request):
    if request.user.is_authenticated:
        template = 'diary/home.html'

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

    else:
        log_first()

def other(request):
    request.session['message'] = ['warn','Ops. Hľadaná stránka nebola nájdená.']

    if request.user.is_authenticated:
        return redirect('diary:domov')
    else:
        return redirect('diary:index')

def log_in(request):
    template = 'diary/login.html'

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('diary:home')

        else:
            message = 'Zadané používateľské meno alebo heslo je neprávne.'
            return render(request, template, {'error':message})

    else:
        return render(request, template, {})

def log_out(request):
    logout(request)
    request.session['message'] = ['success','Bola si úspešne odhlásená.']

    return redirect('diary:index')

def register(request):
    template = 'diary/register.html'

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password_again = request.POST['password_again']

        try:
            User.objects.get(username=username)

        except(User.DoesNotExist):
            i = email.find('@') + 1
            if i >= 4:
                j = email[i:].find('.') + 1
                if j >= 2:
                    if len(email[j:]) >= 1:
                        pass
                    else:
                        message = 'Zadaj svoj platný e-mail.'
                        return render(request, template, {'error':message, 'username':username})
                else:
                    message = 'Zadaj svoj platný e-mail.'
                    return render(request, template, {'error':message, 'username':username})
            else:
                message = 'Zadaj svoj platný e-mail.'
                return render(request, template, {'error':message, 'username':username})

            try:
                User.objects.get(email=email)

            except(User.DoesNotExist):
                if len(password) < 5:
                    message = 'Zadané heslo je príliš krátke.'
                    return render(request, template, {'error':message, 'username':username, 'email':email})

                if password == password_again:
                    user = User.objects.create_user(username, email, password)

                    login(request, user)
                    return redirect('diary:change_profile')

                else:
                    message = 'Zadané heslá sa nezhodujú.'
                    return render(request, template, {'error':message, 'username':username, 'email':email})

            else:
                message = 'Zadaný e-mail sa už používa, vyber si iný.'
                return render(request, template, {'error':message, 'username':username})

        else:
            message = 'Zadané používateľské meno sa už používa, vyber si iné.'
            return render(request, template, {'error':message, 'email':email})

    else:
        return render(request, template, {})
############

### Not done ###
def profile(request):
    pass

def change_profile(request):
    pass

def graph(request):
    pass

def my_diary(request):
    pass

def view_action(request, action_id):
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

def not_my_diary(request, username):
    pass

def not_my_action(request, username, action_id):
    pass
#############
