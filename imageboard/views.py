from django.shortcuts import render
from os import urandom
from django.db import connection
import hashlib

def generate_server_nonce():
    return str(urandom(16))

def logout(request):
    if 'nonce' in request.session:
        del request.session['nonce']
    if not 'userID' in request.session:
        return render(request, 'notLoggedIn.html')
    else:
        request.session.flush()
        request.session.cycle_key()
        return render(request, 'logout.html')

def index(request):
    if 'nonce' in request.session:
        del request.session['nonce']
    if not 'userID' in request.session:
        request.session.set_expiry(0)
    return render(request, 'index.html')

def invalidSignupRequest(request):
    nonce = generate_server_nonce()
    request.session['nonce'] = nonce
    request.session.set_expiry(0)
    return render(request, 'signup.html', {'nonce': nonce, 'errortext': "Something went wrong. Please try again."})

def invalidLoginRequest(request):
    nonce = generate_server_nonce()
    request.session['nonce'] = nonce
    request.session.set_expiry(0)
    return render(request, 'login.html', {'nonce': nonce, 'errortext': "Something went wrong. Please try again."})

def invalidLoginCredentials(request):
    nonce = generate_server_nonce()
    request.session['nonce'] = nonce
    request.session.set_expiry(0)
    return render(request, 'login.html', {'nonce': nonce, 'errortext': "Incorrect username or password."})

def takenUsername(request):
    nonce = generate_server_nonce()
    request.session['nonce'] = nonce
    request.session.set_expiry(0)
    return render(request, 'signup.html', {'nonce': nonce, 'errortext': "That username is already taken."})

def takenEmail(request):
    nonce = generate_server_nonce()
    request.session['nonce'] = nonce
    request.session.set_expiry(0)
    return render(request, 'signup.html', {'nonce': nonce, 'errortext': "That email is registered with another account."})

def login(request):
    if request.method == "GET":
        if 'username' in request.session:
            return render(request, 'alreadySignedIn.html')
        else:
            nonce = generate_server_nonce()
            request.session['nonce'] = nonce
            request.session.set_expiry(0)
            return render(request, 'login.html', {'nonce': nonce})
    else:
        if not ('nonce' in request.session and 'cnonce' in request.POST
                and 'hashpass' in request.POST and 'username' in request.POST):
            return invalidLoginRequest(request)
        else:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, username, password, permissions, email FROM users WHERE username = %s", [request.POST['username']])
                row = cursor.fetchone()
                if(row is None):
                    return invalidLoginCredentials(request)
                else:
                    passHash = hashlib.sha512((row[2] + request.session['nonce'] + request.POST['cnonce']).encode("utf-8")).hexdigest()
                    if(not passHash == request.POST['hashpass']):
                        return invalidLoginCredentials(request)
                    else:
                        request.session['userID'] = row[0]
                        request.session['username'] = row[1]
                        request.session['permissions'] = row[3]
                        request.session['email'] = row[4]
                        if('remember' in request.POST):
                            request.session.set_expiry(604800)
                        request.session.cycle_key()
                        return render(request, 'loggedIn.html')

def signup(request):
    if request.method == "GET":
        if 'username' in request.session:
            return render(request, 'alreadySignedIn.html')
        else:
            nonce = generate_server_nonce()
            request.session['nonce'] = nonce
            request.session.set_expiry(0)
            return render(request, 'signup.html', {'nonce': nonce})
    else:
        if not ('nonce' in request.session and 'nonce' in request.POST
                and 'hashpass' in request.POST and 'email' in request.POST
                and 'username' in request.POST):
            return invalidSignupRequest(request)
        else:
            with connection.cursor() as cursor:
                cursor.execute("SELECT username FROM users WHERE username = %s", [request.POST['username']])
                row = cursor.fetchone()
                if(row is not None):
                    return takenUsername(request)
                else:
                    cursor.execute("SELECT username FROM users WHERE email = %s", [request.POST['email']])
                    row = cursor.fetchone()
                    if(row is not None):
                        return takenEmail(request)
                    else:
                        cursor.execute("INSERT INTO users(username, email, password) VALUES (%s, %s, %s)", [request.POST['username'], request.POST['email'], hashlib.sha512(request.POST['hashpass'].encode("utf-8")).hexdigest()])
                        cursor.execute("SELECT id, username, permissions, email FROM users WHERE username = %s", [request.POST['username']])
                        row = cursor.fetchone()
                        request.session['userID'] = row[0]
                        request.session['username'] = row[1]
                        request.session['permissions'] = row[2]
                        request.session['email'] = row[3]
                        if('remember' in request.POST):
                            request.session.set_expiry(604800)
                        request.session.cycle_key()
                        return render(request, 'loggedIn.html')