# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Event

# Register your models here.


class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'start_time', 'organizers_display')
    search_fields = ('name', 'desc', 'organizers__key')
    raw_fields = ('location',)


admin.site.register(Event, EventAdmin)