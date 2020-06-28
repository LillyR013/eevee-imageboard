import copy
import hashlib
import os
import random
from datetime import datetime
from os import urandom
import magic
from django.http import Http404
from django.db import connection
from django.shortcuts import render
from PIL import Image, warnings

random.seed(datetime.now())

def generate_server_nonce():
    return str(urandom(16))

def tags(request):
    if request.method == "GET":
        if 'nonce' in request.session:
            del request.session['nonce']
        if not 'userID' in request.session:
            return render(request, 'notLoggedIn.html')
        elif request.session['permissions'] < 2:
            return render(request, 'notAllowed.html')
        else:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM tags")
                rows = cursor.fetchall()
                return render(request, 'tags.html', {"rows": rows})
    else:
        if 'tagID' in request.POST and not request.POST['tagID'] == "":
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM tags WHERE id=%s", [request.POST["tagID"]])
                cursor.execute("DELETE FROM imageTags WHERE tagID=%s", [request.POST["tagID"]])
                cursor.execute("SELECT * FROM tags")
                rows = cursor.fetchall()
                return render(request, 'tags.html', {"rows": rows})
        elif 'tagName' in request.POST and not request.POST['tagName'] == "":
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM tags WHERE name = %s", [request.POST['tagName']])
                rows = cursor.fetchone()
                if rows is not None:
                    cursor.execute("SELECT * FROM tags")
                    rows = cursor.fetchall()
                    return render(request, 'tags.html', {"rows": rows, "errorMessage": "Tag already in use"})
                else:
                    cursor.execute("INSERT INTO tags(name) VALUES(%s)", [request.POST["tagName"]])
                    cursor.execute("SELECT * FROM tags")
                    rows = cursor.fetchall()
                    return render(request, 'tags.html', {"rows": rows})
        else:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM tags")
                rows = cursor.fetchall()
                return render(request, 'tags.html', {"rows": rows, "errorMessage": "Something went wrong, please try again."})
        

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

def validateImage(f):
    try:
        fileToValidate = copy.deepcopy(f)
        warnings.simplefilter('error', Image.DecompressionBombWarning)
        image = Image.open(fileToValidate)
        image.verify()    
        return True
    except:
        return False

def displayImage(request):
    imageID = request.path[6:]
    with connection.cursor() as cursor:
        cursor.execute("SELECT file_name, fileType FROM images WHERE id=%s", [imageID])
        image = cursor.fetchone()
        if image != None:
            return render(request, "viewImage.html", {"imageID": imageID, "imagePath": image[0] + "." + image[1]})
        else:
            raise Http404()

def stripImage(f, fileType):
    if(fileType != "image/gif"):
        image = Image.open(f)
        image = image.convert("RGB")
        oldData = image.load()
        newImage = Image.new(image.mode, image.size)
        data = newImage.load()
        for y in range(image.size[1]):
            for x in range(image.size[0]):
                data[(x, y)] = oldData[(x, y)]
        return newImage
    else:
        return f

def addToDatabase(fileType, uploaderID, POST):
    with connection.cursor() as cursor:
        cursor.execute("SELECT uuid();")
        uuid = cursor.fetchone()
        uuid = uuid[0]
        cursor.execute("INSERT INTO images(file_name, fileType, uploaded_by) VALUES(%s, %s, %s);", [uuid, fileType, uploaderID])
        for key in POST:
            if(POST[key] == "on"):
                cursor.execute("INSERT INTO imageTags(imageID, tagID) VALUES (LAST_INSERT_ID(), %s)", [key[8:]])
        return uuid

def parseImage(f, POST, userID):
    if validateImage(f):
        begin = f.tell()
        fileType = magic.from_buffer(f.read(1024), mime=True)
        f.seek(begin)
        image = stripImage(f, fileType)
        if fileType == "image/jpeg":
            fileNum = addToDatabase("jpeg", userID, POST)
            image.save('var/www/env/mysite/images/' + str(fileNum) + '.jpeg')
            return True
        elif fileType == "image/png":
            fileNum = addToDatabase("png", userID, POST)
            image.save('var/www/env/mysite/images/' + str(fileNum) + '.png')
            return True
        elif fileType == "image/gif":
            fileNum = addToDatabase("gif", userID, POST)
            with open('var/www/env/mysite/images/'+str(fileNum)+'.gif', 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            return True
        else:
            return False
    else:
        return False


def upload(request):
    if request.method == "GET":
        if 'nonce' in request.session:
            del request.session['nonce']
        if not 'userID' in request.session:
            return render(request, 'notLoggedIn.html')
        else:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM tags")
                rows = cursor.fetchall()
                return render(request, "upload.html", {"rows": rows})
    else:
        if "image" in request.FILES and "userID" in request.session:
            if parseImage(request.FILES["image"], request.POST, request.session["userID"]):
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM tags")
                    rows = cursor.fetchall()
                    return render(request, "upload.html", {"rows": rows, "errortext": "Upload successful."})
            else:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM tags")
                    rows = cursor.fetchall()
                    return render(request, "upload.html", {"rows": rows, "errortext": "Upload rejected."})
        else:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM tags")
                rows = cursor.fetchall()
                return render(request, "upload.html", {"rows": rows, "errortext": "Upload failed."})

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
