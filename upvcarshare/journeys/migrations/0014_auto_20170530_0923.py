# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-05-30 09:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journeys', '0013_journey_total_passengers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journey',
            name='time_window',
            field=models.PositiveIntegerField(blank=True, default=30, help_text='Se buscarán por los viajes que salgan hasta con estos minutos de antelación', verbose_name='ventana de tiempo'),
        ),
    ]