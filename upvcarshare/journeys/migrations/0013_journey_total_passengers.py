# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-30 11:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journeys', '0012_auto_20161024_1001'),
    ]

    operations = [
        migrations.AddField(
            model_name='journey',
            name='total_passengers',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='total pasajeros'),
        ),
    ]
