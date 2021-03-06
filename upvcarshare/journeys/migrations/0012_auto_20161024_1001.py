# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-24 10:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import recurrence.fields


class Migration(migrations.Migration):

    dependencies = [
        ('journeys', '0011_journey_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journey',
            name='arrival',
            field=models.DateTimeField(blank=True, null=True, verbose_name='fecha y hora de llegada estimada*'),
        ),
        migrations.AlterField(
            model_name='journey',
            name='departure',
            field=models.DateTimeField(verbose_name='fecha y hora de salida*'),
        ),
        migrations.AlterField(
            model_name='journey',
            name='kind',
            field=models.PositiveIntegerField(choices=[(0, 'ida'), (1, 'vuelta')], verbose_name='tipo de viaje'),
        ),
        migrations.AlterField(
            model_name='journey',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='journeys.Journey'),
        ),
        migrations.AlterField(
            model_name='journey',
            name='recurrence',
            field=recurrence.fields.RecurrenceField(blank=True, null=True, verbose_name='¿Vas a realizar este viaje más de una vez?'),
        ),
        migrations.AlterField(
            model_name='journey',
            name='time_window',
            field=models.PositiveIntegerField(blank=True, default=30, help_text='Se buscaran por los viajes que salgan hasta con estos minutos de antelación', verbose_name='ventana de tiempo'),
        ),
        migrations.AlterField(
            model_name='residence',
            name='address',
            field=models.TextField(help_text='La dirección del lugar, según quieras que la vean los demás.', verbose_name='dirección'),
        ),
    ]
