# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-31 14:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SignUpModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=120)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('username', models.CharField(max_length=120, unique=True)),
                ('password', models.TextField(max_length=40)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
