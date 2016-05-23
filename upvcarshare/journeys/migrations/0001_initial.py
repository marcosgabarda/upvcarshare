# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-23 15:50
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Campus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(blank=True, max_length=64, null=True, verbose_name='nombre')),
                ('position', django.contrib.gis.db.models.fields.PointField(srid=2062, verbose_name='posición en el mapa')),
                ('distance', models.PositiveIntegerField(blank=True, default=500, help_text='Distancia máxima a la que te desplazarías (metros)', verbose_name='distancia')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Journey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('kind', models.PositiveIntegerField(choices=[(0, 'Ida'), (1, 'Vuelta')], verbose_name='tipo de trayecto')),
                ('free_places', models.PositiveIntegerField(default=4, verbose_name='plazas libres')),
                ('departure', models.DateTimeField(verbose_name='fecha y hora de salida')),
                ('disabled', models.BooleanField(default=False, verbose_name='marcar como deshabilitado')),
                ('campus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='journeys', to='journeys.Campus', verbose_name='campus de origen/destino')),
                ('driver', models.ForeignKey(blank=True, help_text='user who drives during the journey', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
        ),
        migrations.CreateModel(
            name='Passenger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('journey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='passengers', to='journeys.Journey')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Residence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(blank=True, max_length=64, null=True, verbose_name='nombre')),
                ('position', django.contrib.gis.db.models.fields.PointField(srid=2062, verbose_name='posición en el mapa')),
                ('distance', models.PositiveIntegerField(blank=True, default=500, help_text='Distancia máxima a la que te desplazarías (metros)', verbose_name='distancia')),
                ('address', models.TextField(verbose_name='dirección')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='residences', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Transport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(blank=True, max_length=64, null=True)),
                ('default_places', models.PositiveIntegerField(default=4)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
        ),
        migrations.AddField(
            model_name='journey',
            name='residence',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='journeys', to='journeys.Residence', verbose_name='lugar de origen/destino'),
        ),
        migrations.AddField(
            model_name='journey',
            name='user',
            field=models.ForeignKey(help_text='user who creates the journey', on_delete=django.db.models.deletion.CASCADE, related_name='journeys', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='passenger',
            unique_together=set([('user', 'journey')]),
        ),
    ]
