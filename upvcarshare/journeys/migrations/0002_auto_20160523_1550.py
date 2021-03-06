# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-23 15:50
from __future__ import unicode_literals

from django.contrib.gis.geos import Point
from django.db import migrations

from journeys import DEFAULT_PROJECTED_SRID


def load_campuses(apps, schema_editor):
    Campus = apps.get_model("journeys", "Campus")
    Campus.update_modified = True
    campuses_data = [
        {
            "name": "Campus de Vera",
            "distance": 1000,
            "position": Point(887345.91, 547986.83, srid=DEFAULT_PROJECTED_SRID)
        },
        {
            "name": "Campus de Alcoy",
            "distance": 1000,
            "position": Point(879122.88, 460282.27, srid=DEFAULT_PROJECTED_SRID)
        },
        {
            "name": "Campus de Gandia",
            "distance": 1000,
            "position": Point(904722.54, 494751.81, srid=DEFAULT_PROJECTED_SRID)
        },
    ]
    for data in campuses_data:
        if not Campus.objects.filter(name=data["name"]).exists():
            Campus.objects.create(**data)


class Migration(migrations.Migration):

    dependencies = [
        ('journeys', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_campuses),
    ]
