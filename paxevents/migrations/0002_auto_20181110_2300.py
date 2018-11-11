# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-11 07:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('paxevents', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='attendees',
            field=models.ManyToManyField(related_name='_event_attendees_+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='public',
            field=models.BooleanField(default=True),
        ),
    ]