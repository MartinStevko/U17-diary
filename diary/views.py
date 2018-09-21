from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse

from django.contrib import admin
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required

from django.db.models import Q
from django.template.context_processors import csrf
import subprocess

from datetime import datetime, timedelta, date
import random
import string

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from .models import *
from .variables import directories, cmd_list

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
        elif message[0] == 'info':
            return render(request, template, {'info':message[1]})
        else:
            return render(request, template, {'info':message})

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
            elif message[0] == 'info':
                return render(request, template, {'info':message[1]})
            else:
                return render(request, template, {'info':message})

        else:
            return render(request, template, {})

    else:
        request.session['message'] = 'Stránka, ktorú chceš navštíviť vyžaduje prihlásenie. Najprv sa prihlás.'
        request.session['back_redirection'] = 'home'
        return redirect('diary:log_in')

def other(request):
    request.session['message'] = ['warn','Hľadaná stránka nebola nájdená.']

    if request.user.is_authenticated:
        return redirect('diary:home')
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

            try:
                back_redirection = request.session['back_redirection']
            except(KeyError):
                back_redirection = None;

            if back_redirection:
                redirect_string = 'diary:' + back_redirection
                return redirect(redirect_string)
            else:
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
                    profile.save()
                    Week.objects.create(
                        idAccount = profile,
                        ordinal_number = 0,
                        points = 0
                    )

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

            except(User.MultipleObjectsReturned):
                pass

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
        except(Account.MultipleObjectsReturned):
            message = 'Pre tvoj účet ({}) existuje viacero profilov. Kontaktuj admina stránky so žiadosťou o vyriešenie problému.'
            DuplicateError.objects.create(idUser=request.user, error_message=message)
            request.session['message'] = ['error', message]
            return redirect('diary:home')

        update_points(profile)

        first_date = date(2018, 7, 16)
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
        request.session['back_redirection'] = 'profile'
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
        except(Account.MultipleObjectsReturned):
            message = 'Pre tvoj účet ({}) existuje viacero profilov. Kontaktuj admina stránky so žiadosťou o vyriešenie problému.'
            DuplicateError.objects.create(idUser=request.user, error_message=message)
            request.session['message'] = ['error', message]
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
            approval_code = request.POST['code']

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

                except(User.MultipleObjectsReturned):
                    message = 'Zadaný e-mail sa už používa.'
                    return render(request, template, {
                        'profile':profile,
                        'state':state,
                        'clubs':clubs,
                        'error':message
                    })

                else:
                    message = 'Zadaný e-mail sa už používa.'
                    return render(request, template, {
                        'profile':profile,
                        'state':state,
                        'clubs':clubs,
                        'error':message
                    })

            if approval_code != '':
                try:
                    code = Code.objects.get(value=approval_code)
                except:
                    pass
                else:
                    profile.approved = True
                    profile.save()

                    code.delete()

            return redirect('diary:profile')

        else:
            return render(request, template, {
                'profile':profile,
                'state':state,
                'clubs':clubs
            })

    else:
        request.session['message'] = 'Stránka, ktorú chceš navštíviť vyžaduje prihlásenie. Najprv sa prihlás.'
        request.session['back_redirection'] = 'change_profile'
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
        except(Account.MultipleObjectsReturned):
            message = 'Pre tvoj účet ({}) existuje viacero profilov. Kontaktuj admina stránky so žiadosťou o vyriešenie problému.'
            DuplicateError.objects.create(idUser=request.user, error_message=message)
            request.session['message'] = ['error', message]
            return redirect('diary:home')

        update_points(profile)
        points_total = profile.points

        actions = Action.objects.filter(idAccount=profile).order_by('-date')
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

        return render(request, template, {
            'points':points_total,
            'table':table
        })

    else:
        request.session['message'] = 'Stránka, ktorú chceš navštíviť vyžaduje prihlásenie. Najprv sa prihlás.'
        request.session['back_redirection'] = 'my_diary'
        return redirect('diary:log_in')

def view_action(request, action_id):
    if request.user.is_authenticated:
        template = 'diary/view_action.html'

        user = request.user
        try:
            profile = Account.objects.get(idUser=user)
        except(Account.DoesNotExist):
            request.session['message'] = ['warn','Profil pre tvoj účet neexistuje. Ak máš dojem, že by mal, kontaktuj admina.']
            return redirect('diary:home')
        except(Account.MultipleObjectsReturned):
            message = 'Pre tvoj účet ({}) existuje viacero profilov. Kontaktuj admina stránky so žiadosťou o vyriešenie problému.'
            DuplicateError.objects.create(idUser=request.user, error_message=message)
            request.session['message'] = ['error', message]
            return redirect('diary:home')

        try:
            act = Action.objects.get(pk=action_id)
        except(Action.DoesNotExist):
            request.session['message'] = ['warn','Hľadaná položka neexistuje.']
            return redirect('diary:home')

        if act.idAccount != profile:
            request.session['message'] = ['error','Táto akcia nie je tvoja. Nemôžeš si prezerať podrobnosti o akciách iných.']
            return redirect('diary:home')

        else:
            if request.method == 'POST':
                text = request.POST['send_text']

                if text != '':
                    Message.objects.create(
                        from_user = user,
                        idAction = act,
                        content = text
                    )

                    return redirect('diary:view_action', action_id)

            else:
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
                messages = Message.objects.filter(idAction=act).order_by('-time')

                action = [
                    act.idActivity.name,
                    act.description,
                    duration_string,
                    points,
                    act.date,
                ]

                return render(request, template, {
                    'action':action,
                    'messages':messages
                })

    else:
        request.session['message'] = 'Stránka, ktorú chceš navštíviť vyžaduje prihlásenie. Najprv sa prihlás.'
        request.session['back_redirection'] = 'view_action'
        return redirect('diary:log_in')

def add_action(request):
    template = 'diary/add_action.html'

    if request.user.is_authenticated:
        activities = Activity.objects.all()

        if request.method == 'POST':
            activity_id = request.POST['activity']
            dur_hours = request.POST['hours']
            dur_minutes = request.POST['minits']
            description = request.POST['description']
            datetime_ = request.POST['datetime']

            try:
                activity_id = int(activity_id)
                activity = Activity.objects.get(pk=activity_id)
            except(ValueError, Activity.DoesNotExist):
                message = 'Vyber si aktivitu zo zoznamu.'
                return render(request, template, {
                    'activities':activities,
                    'dur_hours':dur_hours,
                    'dur_minutes':dur_minutes,
                    'description':description,
                    'datetime':datetime_
                })

            try:
                profile = Account.objects.get(idUser=request.user)
            except(Account.DoesNotExist):
                request.session['message'] = ['error','Profil pre tvoj účet neexistuje. Nemôžeš pridávať aktivity.']
                return redirect('diary:domov')
            except(Account.MultipleObjectsReturned):
                message = 'Pre tvoj účet ({}) existuje viacero profilov. Kontaktuj admina stránky so žiadosťou o vyriešenie problému.'
                DuplicateError.objects.create(idUser=request.user, error_message=message)
                request.session['message'] = ['error', message]
                return redirect('diary:home')

            duration = int(dur_hours)*60 + int(dur_minutes)

            try:
                i = datetime_.find('-')
                year_ = int(datetime_[0:i])
                datetime_ = datetime_[(i+1):]

                i = datetime_.find('-')
                month_ = int(datetime_[0:i])
                datetime_ = datetime_[(i+1):]

                i = datetime_.find('T')
                day_ = int(datetime_[0:i])
                datetime_ = datetime_[(i+1):]

                i = datetime_.find(':')
                hour_ = int(datetime_[0:i])
                datetime_ = datetime_[(i+1):]

                minute_ = int(datetime_)
            except(ValueError):
                date_ = False
            else:
                date_ = datetime(year_, month_, day_, hour_, minute_)

            if date_:
                action = Action.objects.create(
                    idAccount = profile,
                    idActivity = activity,
                    duration = duration,
                    description = description,
                    date = date_
                )
            else:
                action = Action.objects.create(
                    idAccount = profile,
                    idActivity = activity,
                    duration = duration,
                    description = description
                )

            action.save()
            update_points(profile)

            new_points = action.duration * activity.ppm

            first_date = date(2018, 7, 16)
            delta = action.date.date() - first_date
            week_number = delta.days // 7 + 1

            try:
                week = Week.objects.get(idAccount=profile, ordinal_number=week_number)
            except(Week.DoesNotExist):
                week = Week.objects.create(
                    idAccount = profile,
                    ordinal_number = week_number,
                    points = new_points
                )
                week.save()
            except(Week.MultipleObjectsReturned):
                message = "Add Action - v databáze týždňov (Week) sa vyskytuje viacero týždňov pre účet {} s poradovým číslom {}".format(profile.idUser.username, ordinal_number)
                DuplicateError.objects.create(idUser=request.user, error_message=message)

                week = Week.objects.filter(idAccount=profile, ordinal_number=week_number)[0]

            week.points += new_points
            week.save()

            return redirect('diary:my_diary')

        else:
            now_time = datetime.now()
            time_string = ''
            time_string += str(now_time.year) + '-'
            if now_time.month < 10:
                time_string += '0' + str(now_time.month) + '-'
            else:
                time_string += str(now_time.month) + '-'
            if now_time.day < 10:
                time_string += '0' + str(now_time.day) + 'T'
            else:
                time_string += str(now_time.day) + 'T'
            if now_time.hour < 10:
                time_string += '0' + str(now_time.hour) + ':'
            else:
                time_string += str(now_time.hour) + ':'
            if now_time.minute < 10:
                time_string += '0' + str(now_time.minute)
            else:
                time_string += str(now_time.minute)

            return render(request, template, {
                'activities':activities,
                'now':time_string
            })
    else:
        request.session['message'] = 'Stránka, ktorú chceš navštíviť vyžaduje prihlásenie. Najprv sa prihlás.'
        request.session['back_redirection'] = 'add_action'
        return redirect('diary:log_in')

def add_missing_week(weeks, week_number):
    previous_ordinal = 0
    for i in range(week_number + 1):
        try:
            ord_ = weeks[i].ordinal_number
        except(IndexError):
            ord_ = week_number + 1
        while previous_ordinal + 1 < ord_:
            Week.objects.create(
                idAccount = weeks[0].idAccount,
                ordinal_number = previous_ordinal + 1,
                points = 0
            )
            previous_ordinal += 1

        if previous_ordinal + 1 > ord_:
            pass
        else:
            previous_ordinal += 1

def week_repair(profile):
    first_date = date(2018,7,16)

    weeks = Week.objects.filter(idAccount=profile)
    actions = Action.objects.filter(idAccount=profile)
    for week in weeks:
        obj = []
        ord_ = week.ordinal_number - 1
        d = ord_*7

        start_ = first_date + timedelta(days=d)
        end_ = first_date + timedelta(days=d+7)
        start_ = datetime.combine(start_, datetime.min.time())
        end_ = datetime.combine(end_, datetime.min.time())

        for act in actions:
            naive = act.date.replace(tzinfo=None)
            if (naive > start_ and naive < end_):
                obj.append(act)
        total_sum = 0

        for act in obj:
            total_sum += act.duration * act.idActivity.ppm

        week.points = total_sum
        week.save()

def graph(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            pass
        else:
            try:
                profile = Account.objects.get(idUser=request.user)
            except(Account.DoesNotExist):
                request.session['message'] = ['warn','Profil pre tvoj účet neexistuje. Ak máš dojem, že by mal, kontaktuj admina.']
                return redirect('diary:home')
            except(Account.MultipleObjectsReturned):
                message = 'Pre tvoj účet ({}) existuje viacero profilov. Kontaktuj admina stránky so žiadosťou o vyriešenie problému.'
                DuplicateError.objects.create(idUser=request.user, error_message=message)
                request.session['message'] = ['error', message]
                return redirect('diary:home')

            if profile.approved == False:
                request.session['message'] = ['info','Tvoj účet ešte nebol schválený. Musíš počkať, kým to niekto z coachov spraví a až potom budeš môcť vidieť ako sa darí zvyšku.']
                return redirect('diary:home')

        template = 'diary/graph.html'

        first_date = date(2018, 7, 16)
        delta = datetime.now().date() - first_date
        week_number = delta.days // 7 + 1

        players = []
        accounts = Account.objects.filter(~Q(points=0), approved=True).order_by('pk')

        for acc in accounts:
            players.append(acc.idUser.username)
            weeks = Week.objects.filter(idAccount=acc).order_by('ordinal_number')
            add_missing_week(weeks, week_number)

        data = []
        for i in range(week_number + 1):
            weeks_temp = Week.objects.filter(ordinal_number=i).order_by('idAccount_id')
            weeks = []
            for week in weeks_temp:
                if week.idAccount.points != 0:
                    weeks.append(week)
            week_data = []
            week_str = str(i) + '.'
            total_points = 0
            for week in weeks:
                name_ = str(week.idAccount.idUser.username)

                previous_weeks = Week.objects.filter(idAccount=week.idAccount)
                previous_points = 0
                for w in previous_weeks:
                    if w.ordinal_number < i:
                        previous_points += w.points

                points_ = int(week.points + previous_points)
                total_points += int(week.points + previous_points)

                week_data.append([name_, points_])

            points_mean = total_points // len(week_data)
            for person in week_data:
                person[1] = str(person[1] - points_mean)
            data.append([week_str, week_data])

        return render(request, template, {'players':players, 'data':data})

    else:
        request.session['message'] = 'Stránka, ktorú chceš navštíviť vyžaduje prihlásenie. Najprv sa prihlás.'
        request.session['back_redirection'] = 'graph'
        return redirect('diary:log_in')

def activities(request):
    template = 'diary/activities.html'

    activities_ = Activity.objects.all()
    return render(request, template, {'activities':activities_})
############

### Not done ###
@login_required
@staff_member_required
def staff_activities(request):
    staff = True
    template = 'diary/activities.html'

    activities_ = Activity.objects.all()

    if request.method == 'POST':
        activity_value = []
        for activity in activities_:
            id_string = str(activity.id)
            try:
                activity_value.append(int(request.POST[id_string]))
            except(ValueError):
                pass

        if len(activities_) == len(activity_value):
            i = 0
            for activity in activities_:
                activity.ppm = activity_value[i]
                activity.save()
                i += 1

            activities_ = Activity.objects.all()
            return redirect('diary:staff_activities')

        else:
            message_ = 'Údaje neboli zmenené. Jeden alebo viacero údajov chýba.'
            return render(request, template, {
                'activities':activities_,
                'error':message_,
                'staff':staff
            })

    else:
        return render(request, template, {'activities':activities_, 'staff':staff})

@login_required
@staff_member_required
def all_diaries(request):
    template = 'diary/all_diaries.html'

    profiles = Account.objects.filter(approved=True)
    for profile in profiles:
        update_points(profile)
    profiles = Account.objects.filter(approved=True).order_by('idUser__username')

    return render(request, template, {'profiles':profiles})

@login_required
@staff_member_required
def not_my_diary(request, username):
    template = 'diary/my_diary.html'

    try:
        user_ = User.objects.get(username=username)
        profile = Account.objects.get(idUser=user_)
    except(User.DoesNotExist, Account.DoesNotExist):
        request.session['message'] = ['warn','Denníček hľadaného hráča neexistuje.']
        return redirect('diary:home')

    update_points(profile)
    points_total = profile.points

    actions = Action.objects.filter(idAccount=profile).order_by('-date')
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

    return render(request, template, {
        'diary_user':user_,
        'points':points_total,
        'table':table
    })

@login_required
@staff_member_required
def not_my_action(request, username, action_id):
    template = 'diary/view_action.html'

    try:
        user_ = User.objects.get(username=username)
        profile = Account.objects.get(idUser=user_)
    except(User.DoesNotExist, Account.DoesNotExist):
        request.session['message'] = ['warn','Denníček hľadaného hráča neexistuje.']
        return redirect('diary:home')

    try:
        act = Action.objects.get(pk=action_id)
    except(Action.DoesNotExist):
        request.session['message'] = ['warn','Hľadaná položka neexistuje.']
        return redirect('diary:home')

    if act.idAccount != profile:
        request.session['message'] = ['error','Táto akcia nie je tvoja. Nemôžeš si prezerať podrobnosti o akciách iných.']
        return redirect('diary:home')

    else:
        if request.method == 'POST':
            text = request.POST['send_text']

            if text != '':
                Message.objects.create(
                    from_user = request.user,
                    idAction = act,
                    content = text
                )

                return redirect('diary:not_my_action', username, action_id)

        else:
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
            messages = Message.objects.filter(idAction=act).order_by('-time')

            action = [
                act.idActivity.name,
                act.description,
                duration_string,
                points,
                act.date,
            ]

            return render(request, template, {
                'diary_username': username,
                'action':action,
                'messages':messages
            })

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required
@staff_member_required
def console(request):
    """Serves the console at /admin/console
    SECURE_CONSOLE
        values: True/False
        Defined in settings to denote whether to allow access from http or https
        default: False - ALLOW access to ALL.
    CONSOLE_WHITELIST
        values: list of ip strings
        defines list of ips to be allowed
        default: ALLOW ALL ips unless defined."""
    try:
        v1 = request.is_secure() == settings.SECURE_CONSOLE
    except AttributeError:
        v1 = True
    try:
        v2 = get_client_ip(request) in settings.CONSOLE_WHITELIST
    except AttributeError:
        v2 = True
    except:
        print("CONSOLE_WHITELIST needs to be a list of ip addresses to be allowed access")
        v2 = True
    settings_variables = v1 and v2

    context = {'STATIC_URL': settings.STATIC_URL}
    context.update(csrf(request))
    return render_to_response('diary/console.html', context)

def generate_results(number, all):
    if all:
        time_ = EvaulationChanges.objects.create()
    profiles = Account.objects.filter(approved=True)
    for profile in profiles:
        update_points(profile)

    try:
        number = int(number)
    except(ValueError):
        relevant = Account.objects.filter(approved=True).order_by('-points')
    else:
        relevant = Account.objects.filter(approved=True).order_by('-points')[:number]

    results_field = []
    for profile in relevant:
        points_old = OldPoints.objects.filter(account=profile).order_by('pk').last()

        try:
            if all:
                if profile.points > 0:
                    OldPoints.objects.create(account=profile, time=time_, value=profile.points)

                points_last = profile.points - points_old.value
            else:
                points_last = profile.points

            results_field.append(['{} - {}\n'.format(profile.idUser.username, points_last), points_last])
        except(AttributeError):
            results_field.append(['{} - {}\n'.format(profile.idUser.username, profile.points), profile.points])

    results_field.sort(key=lambda x: x[1])

    result = ''
    i = len(results_field)
    for profile in results_field:
        result = '   {}. '.format(i) + profile[0] + result
        i += -1

    result = 'Current results:\n' + result
    return result

@login_required
@staff_member_required
def console_post(request):
    if request.POST:
        command = request.POST.get("command")
        if command:
            if command == 'dir':
                data = ['olive', directories]

            elif command == 'active users':
                n = User.objects.filter(is_active=True)
                data = ['olive', str(n)]

            elif command == 'repair profiles':
                try:
                    profiles = Account.objects.all()
                    for profile in profiles:
                        update_points(profile)
                except:
                    data = ['red', 'Unexpected error']
                else:
                    data = ['green', 'Profiles were successfully repaired']

            elif command == 'repair weeks':
                first_date = date(2018, 7, 16)
                delta = datetime.now().date() - first_date
                week_number = delta.days // 7 + 1
                try:
                    profiles = Account.objects.all()
                    for profile in profiles:
                        weeks = Week.objects.filter(idAccount=profile).order_by('ordinal_number')
                        add_missing_week(weeks, week_number)
                        week_repair(profile)
                except:
                    data = ['red', 'Unexpected error']
                else:
                    data = ['green', 'Weeks were successfully repaired']

            elif command == 'results --five':
                result = generate_results(5, False)
                data = ['olive', result]

            elif command == 'results --ten':
                result = generate_results(10, False)
                data = ['olive', result]

            elif command == 'results --full':
                result = generate_results('full', False)
                data = ['olive', result]

            elif command == 'results --last':
                result = generate_results('full', True)
                data = ['olive', result]

            elif command == 'generate code':
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
                approval = Code.objects.create(value=code)
                approval.save()

                data = ['olive', code]

            elif command == 'active codes':
                data = ['olive', 'Active approval codes:\n']

                approvals = Code.objects.all()
                for code in approvals:
                    data[1] += '  {} (creation - {})'.format(str(code.value), str(code.time))

            elif command == 'error list':
                data = ['olive', 'Errors:\n']

                errors = DuplicateError.objects.filter(solved=False).order_by('-time')
                if errors:
                    for error in errors:
                        data[1] += '  - {} - {}: {})'.format(str(error.time), str(error.idUser.username), error.error_message)
                else:
                    data = ['green', 'No errors, good job!']

            elif command == 'test':
                data = ['olive', 'Hello world!']

            elif command == 'help':
                data = ['olive', cmd_list]

            elif command == 'exit':
                request.session.flush()
                data = ["green", "Session was successfully flushed"]

            else:
                data = ["red", "Unknown command, try to type 'help' into console"]

            output = "%c(@" + data[0] + ")%" + data[1] + "%c()"

        else:
            output = "%c(@orange)%" + 'Waiting for commands' + "%c()"
        return HttpResponse(output)

@login_required
@staff_member_required
def not_my_profile(request, username):
    template = 'diary/profile.html'

    try:
        profile_user = User.objects.get(username=username)
    except:
        request.session['message'] = ['warn','Chyba! Užívateľ nebol nájdený.']
        return redirect('diary:home')

    try:
        profile = Account.objects.get(idUser=profile_user)
    except(Account.DoesNotExist):
        request.session['message'] = ['warn','Profil pre tento účet neexistuje. Ak máš dojem, že by mal, kontaktuj admina.']
        return redirect('diary:home')
    except(Account.MultipleObjectsReturned):
        message = 'Pre tento účet ({}) existuje viacero profilov. Kontaktuj admina stránky so žiadosťou o vyriešenie problému.'
        DuplicateError.objects.create(idUser=request.user, error_message=message)
        request.session['message'] = ['error', message]
        return redirect('diary:home')

    update_points(profile)

    first_date = date(2018, 7, 16)
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
        'data':data,
        'profile_user':profile_user
    })
