from django.shortcuts import render

def index(request):
    template = 'diary/index.html'

    try:
        message = request.session['message']
    except(KeyError):
        message = None;

    if message:
        del request.session['message']
        return render(request, template, {'message':message})
    else:
        return render(request, template, {})

def other(request):
    request.session['message'] = 'Hľadaná stránka nebola nájdená'
    return redirect('diary:index')

def log_in(request):
    pass

def log_out(request):
    pass

def register(request):
    pass

def profile(request):
    pass
