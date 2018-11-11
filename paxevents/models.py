# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from evennia.utils.idmapper.models import SharedMemoryModel
from django.db import models

# Create your models here.


class Event(SharedMemoryModel):

    name = models.CharField('Name', max_length=80, help_text='The name of this event.')
    notes = models.TextField('Description', help_text='Description of this event')
    start_time = models.DateTimeField('Starting Time', help_text='The time the event will start')
    end_time = models.DateTimeField('Ending Time', help_text='The time the event ends.', blank=True, null=True)

    organizers = models.ManyToManyField('accounts.AccountDB', related_name='+')
    location = models.ForeignKey('objects.ObjectDB', related_name='+', blank=True, null=True)

    public = models.BooleanField(default=True)
    attendees = models.ManyToManyField('accounts.AccountDB', related_name='+')

    @property
    def organizers_display(self):
        organizer_list = [ ]
        for organizer in self.organizers.all():
            organizer_list.append(organizer.key)
        if len(organizer_list) == 0:
            return "None"
        elif len(organizer_list) == 1:
            return organizer_list[0]
        elif len(organizer_list) == 2:
            return organizer_list[0] + " and " + organizer_list[1]
        else:
            return ", ".join(organizer_list[:-2] + [" and ".join(organizer_list[-2:])])

    @property
    def start_time_display(self):
        from .utils import localize_datetime
        localized = localize_datetime(self.start_time)
        return localized.strftime("%H:%M")

    @property
    def start_datetime_display(self):
        from .utils import localize_datetime
        localized = localize_datetime(self.start_time)
        return localized.strftime("%H:%M %Y-%m-%d")

    @property
    def end_datetime_display(self):
        if self.end_time:
            from .utils import localize_datetime
            localized = localize_datetime(self.end_time)
            return localized.strftime("%H:%M %Y-%m-%d")
        else:
            return None

    @classmethod
    def events_for_day(cls, target_date):
        return Event.objects.filter(start_time__date=target_date)

