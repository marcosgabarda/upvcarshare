# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-26 11:30
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('actor_object_id', models.PositiveIntegerField()),
                ('verb', models.CharField(max_length=255)),
                ('target_object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('action_object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('read', models.BooleanField(default=False)),
                ('action_content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notify_action', to='contenttypes.ContentType')),
                ('actor_content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notify_actor', to='contenttypes.ContentType')),
                ('target_content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notify_target', to='contenttypes.ContentType')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
            },
        ),
    ]