# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from forms import SignUpForm, LoginForm, PostForm, LikeForm, CommentForm
from models import SignUpModel, SessionModel, PostModel, LikeModel, CommentModel
from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password, check_password
from imgurpython import ImgurClient
from django.utils import timezone
from SocialKids.settings import BASE_DIR

'''
    imgur
    client-id-->    3ff9d37f4d24f68
    client-secret-->    7f139235b30f2a6104cc719f2256aafe2109a291
    client-name-->  Social Kids
'''

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
                    response = redirect('/feed/')
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
        session_auth = SessionModel.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session_auth:
            logged_in_time = session_auth.created_on + timedelta(days=1)
            if logged_in_time > timezone.now():
                return session_auth.user
            else:
                return None
        else:
            return None


def post_view(request):
    DIR = "E:\Background"
    user = check_validation(request)
    client_id = '3ff9d37f4d24f68'
    client_secret = '7f139235b30f2a6104cc719f2256aafe2109a291'

    if user:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data['image']
                caption = form.cleaned_data['caption']

                post = PostModel(user=user, image=image, caption=caption)
                path = DIR + "\\" + str(post.image.url)
                client = ImgurClient(client_id, client_secret)
                post.image_url = client.upload_from_path(path, anon=True)['link']
                post.save()
                return redirect('/feed/')
        else:
            form = PostForm()
        return render(request, 'post.html', {'form': form})
    else:
        return redirect('/login/')


def feed_view(request):
    user = check_validation(request)
    if user:
        posts = PostModel.objects.all().order_by('-created_on')
        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True
        return render(request, 'feed.html', {'posts': posts})
    else:
        return redirect('/login/')


def like_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            existing_like = LikeModel.objects.filter(post_id=post_id, user=user)
            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)
            else:
                existing_like.delete()
            return redirect('/feed/')
    else:
        return redirect('/login/')


def comment_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data['comment_text']
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()
            return redirect('/feed/')
    else:
        return redirect('/login/')


def logout_view(request):
    if request.COOKIES.get('session_token'):
        session_end = SessionModel.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session_end:
            request.COOKIES.clear()
            user = check_validation(request)
            if user:
                print "nope"
            else:
                return redirect('/login/')
