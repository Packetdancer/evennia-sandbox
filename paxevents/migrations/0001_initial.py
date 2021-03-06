# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-07 03:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('objects', '0009_remove_objectdb_db_player'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of this event.', max_length=80, verbose_name='Name')),
                ('notes', models.TextField(help_text='Description of this event', verbose_name='Description')),
                ('start_time', models.DateTimeField(help_text='The time the event will start', verbose_name='Starting Time')),
                ('end_time', models.DateTimeField(blank=True, help_text='The time the event ends.', null=True, verbose_name='Ending Time')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='objects.ObjectDB')),
                ('organizers', models.ManyToManyField(related_name='_event_organizers_+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
