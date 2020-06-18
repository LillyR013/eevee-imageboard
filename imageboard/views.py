from django.shortcuts import render
from os import urandom

def generate_server_nonce():
    return urandom(16).hex


def index(request):
    return render(request, 'index.html')

def login(request):
    if request.method == "GET":
        nonce = generate_server_nonce()
        return render(request, 'login.html', {'nonce': nonce})
    else:
        return render(request, 'loggedIn.html')

def signup(request):
    if request.method == "GET":
        nonce = generate_server_nonce()
        return render(request, 'signup.html', {'nonce': nonce})
    else:
        return render(request, 'loggedIn.html')