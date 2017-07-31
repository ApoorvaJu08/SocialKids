# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from forms import SignUpForm, LoginForm
from models import SignUpModel, SessionModel
from datetime import datetime
from django.contrib.auth.hashers import make_password, check_password

# Create your views here.


# signup view to display at the time of signup
def signup_view(request):
    date = datetime.now()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # saving data to DB
            user = SignUpModel(name=name, username=username, email=email, password=make_password(password))
            user.save()
            # returning user ro success page that you have successfully signup to the app
            return render(request, 'success.html')
        else:
            print("Error: Invalid form")
    else:
        form = SignUpForm()
    # returning to signup page if method is not post or there is no data in form or payload is empty
    return render(request, 'index.html', {'form': form}, {'Date': date})


# login view to display at the time of login or sign in
def login_view(request):
    date = datetime.now()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = SignUpModel.objects.filter(username=username).first()
            if user:
                # check for the password
                if check_password(password, user.password):
                    token = SessionModel(user=user)
                    token.create_token()
                    token.save()
                    response = redirect('feed.html')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    print("Incorrect Username or Password")
            else:
                print ("User does not exist")
        else:
            print ("Error: Invalid form")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form}, {'Date': date})


def check_validation(request):
    if request.COOKIES.get('session_token'):
        session_auth = SessionModel.objects.filter(session_token=request.COOKIES.get('session_token').first())
        if session_auth:
            return session_auth.user
        else:
            return None
