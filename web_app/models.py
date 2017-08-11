# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from reusable_models.models import DateTimeModel
from uuid import uuid4

# Create your models here.


class SignUpModel(DateTimeModel):
    name = models.CharField(max_length=120, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    username = models.CharField(max_length=120, unique=True, null=False, blank=False)
    password = models.TextField(max_length=40, null=False, blank=False)


class SessionModel(DateTimeModel):
    user = models.ForeignKey(SignUpModel)
    session_token = models.CharField(max_length=255)
    is_valid = models.BooleanField(default=True)

    def create_token(self):
        self.session_token = uuid4()


class PostModel(DateTimeModel):
    user = models.ForeignKey(SignUpModel)
    image = models.FileField(upload_to='user_images/')
    image_url = models.CharField(max_length=255)
    caption = models.CharField(max_length=240)
    has_liked = False

    @property
    def like_count(self):
        return len(LikeModel.objects.filter(post=self))

    @property
    def comments(self):
        return CommentModel.objects.filter(post=self).order_by('created_on')


class LikeModel(DateTimeModel):
    user = models.ForeignKey(SignUpModel)
    post = models.ForeignKey(PostModel)


class CommentModel(DateTimeModel):
    user = models.ForeignKey(SignUpModel)
    post = models.ForeignKey(PostModel)
    comment_text = models.TextField(max_length=512)

