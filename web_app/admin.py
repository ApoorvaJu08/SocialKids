# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import SignUpModel, SessionModel, PostModel, LikeModel, CommentModel

# Register your models here.

admin.site.register(SignUpModel)
admin.site.register(SessionModel)
admin.site.register(PostModel)
admin.site.register(LikeModel)
admin.site.register(CommentModel)

