# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-23 18:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journeys', '0003_auto_20160523_1636'),
    ]

    operations = [
        migrations.AddField(
            model_name='journey',
            name='time_window',
            field=models.PositiveIntegerField(blank=True, default=30, help_text='Se buscaran por los trayectos que salgan hasta con estos minutos de antelación', verbose_name='ventana de tiempo'),
        ),
    ]