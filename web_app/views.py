# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from forms import SignUpForm, LoginForm, PostForm, LikeForm, CommentForm, UpVoteForm
from models import SignUpModel, SessionModel, PostModel, LikeModel, CommentModel, UpVoteModel
from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password, check_password
from imgurpython import ImgurClient
from django.utils import timezone
from SocialKids.settings import BASE_DIR
import sendgrid
from sendgrid.helpers.mail import *
import ctypes
from clarifai.rest import ClarifaiApp
import requests
import json
import os

Pdots_apikey = ''
my_client = sendgrid.SendGridAPIClient(apikey='')
# Create your views here.


# function to send emails using sendgrid
def send_mail(email, subject, body):
    from_email = Email("")
    to_email = Email(email)
    subject = subject
    content = Content("text/plain", body)
    mail_request = Mail(from_email, subject, to_email, content)
    response = my_client.client.mail.send.post(request_body=mail_request.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)


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

            # using sendgrid
            subject = "Successfully Signed Up!"
            body = "Thank you for Signing Up"
            send_mail(email, subject, body)
            ctypes.windll.user32.MessageBoxW(0, u"Successfully signed up", u"Success", 0)
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
                    ctypes.windll.user32.MessageBoxW(0, u"Incorrect Username or Password", u"Error", 0)
                    return render(request, 'login.html', {'invalid': True})
            else:
                print ("User does not exist")
                ctypes.windll.user32.MessageBoxW(0, u"User does not exist", u"Error", 0)
                return render(request, 'index.html', {'invalid': True})
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


# function to check whether the text is abusive or not by using paralleldots
def is_abusive(caption):
    url = 'http://apis.paralleldots.com/abuse'
    payload = {'apikey': Pdots_apikey, 'text': caption}
    text_type = requests.post(url, payload).json()
    if text_type['sentence_type'] == 'Abusive':
        print text_type['confidence_score']
        return True
    else:
        return False


def post_view(request):
    user = check_validation(request)
    client_id = ''
    client_secret = ''

    if user:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data['image']
                caption = form.cleaned_data['caption']
                if is_abusive(caption):
                    ctypes.windll.user32.MessageBoxW(0, u"Your caption contain Abusive content", u"Warning", 0)
                    return redirect('/post/')
                else:
                    post = PostModel(user=user, image=image, caption=caption)
                    path = BASE_DIR + "\\" + str(post.image.url)
                    client = ImgurClient(client_id, client_secret)
                    post.image_url = client.upload_from_path(path, anon=True)['link']
                    # using clarifai api
                    app = ClarifaiApp(api_key='')
                    model = app.models.get('nsfw-v1.0')
                    img_type = model.predict_by_url(post.image_url)

                    if img_type['outputs'][0]['data']['concepts'][0]['name'] == 'nsfw':
                        if img_type['outputs'][0]['data']['concepts'][0]['value'] > img_type['outputs'][0]['data']['concepts'][1]['value']:
                            post.delete()
                        else:
                            post.save()
                    else:
                        if img_type['outputs'][0]['data']['concepts'][0]['value'] < img_type['outputs'][0]['data']['concepts'][1]['value']:
                            post.delete()
                        else:
                            post.save()
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
            for comment in post.comments:
                up_voted = UpVoteModel.objects.filter(comment=comment, user=user).first()
                if up_voted:
                    comment.has_up_voted = True
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
                like = LikeModel.objects.create(post_id=post_id, user=user)
                email = like.post.user.email
                subject = "Like on your post"
                body = "Someone just liked your post"
                send_mail(email, subject, body)
                ctypes.windll.user32.MessageBoxW(0, u"Liked successfully", u"SUCCESS", 0)
            else:
                existing_like.delete()
                ctypes.windll.user32.MessageBoxW(0, u"Unlike successfully", u"SUCCESS", 0)
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
            text = form.cleaned_data['comment_text']
            if is_abusive(text):
                ctypes.windll.user32.MessageBoxW(0, u"Your caption contain Abusive content", u"Warning", 0)
                return redirect('/feed/')
            else:
                email = comment.post.user.email
                subject = "Comment on your post"
                body = "Someone just commented on your post"
                send_mail(email, subject, body)
                comment.save()
                ctypes.windll.user32.MessageBoxW(0, u"Comment posted successfully", u"SUCCESS", 0)
                return redirect('/feed/')
        else:
            return redirect('/feed/')
    else:
        return redirect('/login/')


def up_vote_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = UpVoteForm(request.POST)
        if form.is_valid():
            comment_id = form.cleaned_data.get('comment').id
            up_voted = UpVoteModel.objects.filter(comment_id=comment_id, user=user)
            if not up_voted:
                UpVoteModel.objects.create(comment_id=comment_id, user=user)
            else:
                up_voted.delete()
            return redirect('/feed/')
    else:
        return redirect('/login/')


# def show_fav_user_post():


def logout_view(request):
    if request.COOKIES.get('session_token'):
        session_end = SessionModel.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session_end:
            request.COOKIES.clear()
            session_end.delete()
            user = check_validation(request)
            if user:
                print "nope"
            else:
                return redirect('/login/')


