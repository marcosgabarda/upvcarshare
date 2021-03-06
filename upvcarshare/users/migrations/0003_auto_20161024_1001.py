# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-24 10:01
from __future__ import unicode_literals

import core.files
import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20160619_1804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to=core.files.UploadToDir('avatars/', random_name=True)),
        ),
        migrations.AlterField(
            model_name='user',
            name='default_address',
            field=models.TextField(blank=True, help_text='Dirección que por defecto se usará para crear trayectos, y que será la dirección que vean otros usuarios', null=True, verbose_name='dirección por defecto'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username'),
        ),
    ]
