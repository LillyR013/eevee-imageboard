from django.shortcuts import render
from os import urandom
from django.http import HttpResponse

def generate_server_nonce():
    return str(urandom(16))

def index(request):
    return render(request, 'index.html')

def login(request):
    if request.method == "GET":
        nonce = generate_server_nonce()
        request.session['nonce'] = nonce
        return render(request, 'login.html', {'nonce': nonce})
    else:
        return render(request, 'loggedIn.html')

def signup(request):
    if request.method == "GET":
        nonce = generate_server_nonce()
        request.session['nonce'] = nonce
        return render(request, 'signup.html', {'nonce': nonce})
    else:
        if request.POST['nonce'] != request.session['nonce']:
            return HttpResponse('Invalid Nonce', 'utf-8')
        else:
            return render(request, 'loggedIn.html')