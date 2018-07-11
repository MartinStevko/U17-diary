from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q

from datetime import datetime, timedelta, date

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
        request.session['message'] = 'Stránka, ktorú chceš navštíviť vyžaduje prihlásenie. Najprv sa prihlás.'
        return redirect('diary:log_in')

def other(request):
    request.session['message'] = ['warn','Hľadaná stránka nebola nájdená.']

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
        try:
            message = request.session['message']
        except(KeyError):
            message = None;

        if message:
            del request.session['message']

            return render(request, template, {'info':message})
        else:
            return render(request, template, {})

def log_out(request):
    logout(request)
    request.session['message'] = ['success','Bola si úspešne odhlásená.']

    return redirect('diary:index')

def register(request):
    template = 'diary/register.html'
    clubs = Club.objects.all()

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        club_id = request.POST['club']
        password = request.POST['password']
        password_again = request.POST['password_again']

        try:
            User.objects.get(username=username)

        except(User.DoesNotExist):
            if len(username) < 3:
                message = 'Zadané používateľské meno je príliš krátke, vyber si iné.'
                return render(request, template, {
                    'clubs':clubs,
                    'error':message,
                    'email':email
                })

            i = email.find('@') + 1
            if i >= 4:
                j = email[i:].find('.') + 1
                if j >= 2:
                    if len(email[j:]) >= 1:
                        pass
                    else:
                        message = 'Zadaj svoj platný e-mail.'
                        return render(request, template, {
                            'clubs':clubs,
                            'error':message,
                            'username':username
                        })

                else:
                    message = 'Zadaj svoj platný e-mail.'
                    return render(request, template, {
                        'clubs':clubs,
                        'error':message,
                        'username':username
                    })

            else:
                message = 'Zadaj svoj platný e-mail.'
                return render(request, template, {
                    'clubs':clubs,
                    'error':message,
                    'username':username
                })

            try:
                User.objects.get(email=email)

            except(User.DoesNotExist):
                try:
                    club_id = int(club_id)
                    club = Club.objects.get(pk=club_id)

                except(Club.DoesNotExist, ValueError):
                    message = 'Vyber si zo zoznamu svoj klub.'
                    return render(request, template, {
                        'clubs':clubs,
                        'error':message,
                        'username':username,
                        'email':email
                    })

                if len(password) < 5:
                    message = 'Zadané heslo je príliš krátke.'
                    return render(request, template, {
                        'clubs':clubs,
                        'error':message,
                        'username':username,
                        'email':email
                    })

                if password == password_again:
                    user = User.objects.create_user(username, email, password)
                    profile = Account.objects.create(idUser=user, club=club)

                    login(request, user)

                    request.session['message'] = ['success','Bola si úspešne zaregistrovaná. Teraz môžeš denníček používať, ale ak chceš vidieť ako sa darí tvojim kamarátkam, musíš počkať, kým ti niekto z coachov schváli účet.']
                    return redirect('diary:home')

                else:
                    message = 'Zadané heslá sa nezhodujú.'
                    return render(request, template, {
                        'clubs':clubs,
                        'error':message,
                        'username':username,
                        'email':email
                    })

            else:
                message = 'Zadaný e-mail sa už používa, vyber si iný.'
                return render(request, template, {
                    'clubs':clubs,
                    'error':message,
                    'username':username
                })

        else:
            message = 'Zadané používateľské meno sa už používa, vyber si iné.'
            return render(request, template, {
                'clubs':clubs,
                'error':message,
                'email':email
            })

    else:
        return render(request, template, {'clubs':clubs})

def update_points(profile):
    actions = Action.objects.filter(idAccount=profile)
    p = 0
    for act in actions:
        p += act.duration * act.idActivity.ppm

    profile.points = p
    profile.save()

def profile(request):
    template = 'diary/profile.html'

    if request.user.is_authenticated:
        current_user = request.user
        try:
            profile = Account.objects.get(idUser=current_user)
        except(Account.DoesNotExist):
            request.session['message'] = ['warn','Profil pre tvoj účet neexistuje. Ak máš dojem, že by mal, kontaktuj admina.']
            return redirect('diary:home')

        update_points(profile)

        first_date = date(2018, 7, 5)
        delta = datetime.now().date() - first_date
        date_difference = delta.days
        data = []

        for i in range(date_difference+1):
            date_now = first_date + timedelta(days=i)

            p = 0
            actions = Action.objects.filter(idAccount=profile)
            for act in actions:
                r = act.date.date() - date_now
                if r.days == 0:
                    p += act.duration * act.idActivity.ppm
            data.append([i, p])

        if profile.approved == True:
            state = 'Schválený'
        else:
            state = 'Čakajúci na schválenie'

        return render(request, template, {
            'profile':profile,
            'state':state,
            'date_difference':date_difference,
            'data':data
        })

    else:
        request.session['message'] = 'Stránka, ktorú chceš navštíviť vyžaduje prihlásenie. Najprv sa prihlás.'
        return redirect('diary:log_in')

def change_profile(request):
    template = 'diary/change_profile.html'

    if request.user.is_authenticated:
        current_user = request.user
        try:
            profile = Account.objects.get(idUser=current_user)
        except(Account.DoesNotExist):
            request.session['message'] = ['warn','Profil pre tvoj účet neexistuje. Ak máš dojem, že by mal, kontaktuj admina.']
            return redirect('diary:home')

        update_points(profile)

        if profile.approved == True:
            state = 'Schválený'
        else:
            state = 'Čakajúci na schválenie'

        clubs = Club.objects.filter(~Q(pk=profile.club.id))

        if request.method == 'POST':
            new_username = request.POST['username']
            new_email = request.POST['email']
            new_club_id = int(request.POST['club'])

            if profile.club.id != new_club_id:
                try:
                    profile.club = Club.objects.get(pk=new_club_id)
                    profile.save()
                except(Club.DoesNotExist):
                    message = 'Vyber si klub zo zoznamu.'
                    return render(request, template, {
                        'profile':profile,
                        'state':state,
                        'clubs':clubs,
                        'error':message
                    })
                else:
                    clubs = Club.objects.filter(~Q(pk=profile.club.id))

            if current_user.username != new_username:
                if len(new_username) < 3:
                    message = 'Zadané používateľské meno je príliš krátke, vyber si iné.'
                    return render(request, template, {
                        'profile':profile,
                        'state':state,
                        'clubs':clubs,
                        'error':message,
                        'new_email':new_email
                    })

                try:
                    User.objects.get(username=new_username)
                except(User.DoesNotExist):
                    current_user.username = new_username
                    current_user.save()
                else:
                    message = 'Zadané používateľské meno sa už používa, vyber si iné.'
                    return render(request, template, {
                        'profile':profile,
                        'state':state,
                        'clubs':clubs,
                        'error':message,
                        'new_email':new_email
                    })

            if current_user.email != new_email:
                i = new_email.find('@') + 1
                if i >= 4:
                    j = new_email[i:].find('.') + 1
                    if j >= 2:
                        if len(new_email[j:]) >= 1:
                            pass
                        else:
                            message = 'Zadaj svoj platný e-mail.'
                            return render(request, template, {
                                'profile':profile,
                                'state':state,
                                'clubs':clubs,
                                'error':message
                            })

                    else:
                        message = 'Zadaj svoj platný e-mail.'
                        return render(request, template, {
                            'profile':profile,
                            'state':state,
                            'clubs':clubs,
                            'error':message
                        })

                else:
                    message = 'Zadaj svoj platný e-mail.'
                    return render(request, template, {
                        'profile':profile,
                        'state':state,
                        'clubs':clubs,
                        'error':message
                    })

                try:
                    User.objects.get(email=new_email)
                except(User.DoesNotExist):
                    current_user.email = new_email
                    current_user.save()

                else:
                    message = 'Zadaný e-mail sa už používa.'
                    return render(request, template, {
                        'profile':profile,
                        'state':state,
                        'clubs':clubs,
                        'error':message
                    })

            return redirect('diary:profile')

        else:
            return render(request, template, {
                'profile':profile,
                'state':state,
                'clubs':clubs
            })

    else:
        request.session['message'] = 'Stránka, ktorú chceš navštíviť vyžaduje prihlásenie. Najprv sa prihlás.'
        return redirect('diary:log_in')

def my_diary(request):
    if request.user.is_authenticated:
        template = 'diary/my_diary.html'

        user = request.user
        try:
            profile = Account.objects.get(idUser=user)
        except(Account.DoesNotExist):
            request.session['message'] = ['warn','Profil pre tvoj účet neexistuje. Ak máš dojem, že by mal, kontaktuj admina.']
            return redirect('diary:home')

        update_points(profile)
        points_total = profile.points

        actions = Action.objects.filter(idAccount=profile)
        table = []

        for act in actions:
            hours = act.duration // 60
            minits = act.duration - 60*hours

            if hours == 1:
                h_str = 'hodina'
            elif hours > 1 and hours < 5:
                h_str = 'hodiny'
            else:
                h_str = 'hodín'

            if minits == 1:
                m_str = 'minúta'
            elif minits > 1 and minits < 5:
                m_str = 'minúty'
            else:
                m_str = 'minút'

            duration_string = str(hours) + ' ' + h_str + ' ' + str(minits) + ' ' + m_str
            points = act.duration * act.idActivity.ppm
            message_count = len(Message.objects.filter(idAction=act))

            row = [
                act.id,
                act.idActivity.name,
                act.description,
                duration_string,
                points,
                act.date,
                message_count
            ]

            table.append(row)

        return render(request, template, {'points':points_total, 'table':table})

    else:
        request.session['message'] = 'Stránka, ktorú chceš navštíviť vyžaduje prihlásenie. Najprv sa prihlás.'
        return redirect('diary:log_in')
############

### Not done ###
# login
def view_action(request, action_id):
    pass

# login
def add_action(request):
    pass

# login, approved
def graph(request):
    pass

# staff
def activities(request):
    pass

# staff
def add_activity(request):
    pass

# staff
def all_diaries(request):
    pass

# staff
def not_my_diary(request, username):
    pass

# staff
def not_my_action(request, username, action_id):
    pass
