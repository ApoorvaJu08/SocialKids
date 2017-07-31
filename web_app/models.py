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
    session_token = models.Charfield(max_length=255)
    is_valid = models.BooleanField(default=True)

    def create_token(self):
        self.session_token = uuid4()
