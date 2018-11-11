# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import Http404
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from .models import Event
import calendar
import datetime
from utils import EventHTMLCalendar

# Create your views here.


def calendar_view(request):
    after_day = request.GET.get('day__gte', None)
    extra_context = {}

    if not after_day:
        d = datetime.date.today()
    else:
        try:
            split_after_day = after_day.split('-')
            d = datetime.date(year=int(split_after_day[0]), month=int(split_after_day[1]), day=1)
        except:
            d = datetime.date.today()

    previous_month = datetime.date(year=d.year, month=d.month, day=1)  # find first day of current month
    previous_month = previous_month - datetime.timedelta(days=1)  # backs up a single day
    previous_month = datetime.date(year=previous_month.year, month=previous_month.month,
                                   day=1)  # find first day of previous month

    last_day = calendar.monthrange(d.year, d.month)
    next_month = datetime.date(year=d.year, month=d.month, day=last_day[1])  # find last day of current month
    next_month = next_month + datetime.timedelta(days=1)  # forward a single day
    next_month = datetime.date(year=next_month.year, month=next_month.month,
                               day=1)  # find first day of next month

    extra_context['previous_month'] = reverse('events:calendar') + '?day__gte=' + previous_month.strftime("%Y-%m-%d")
    extra_context['next_month'] = reverse('events:calendar') + '?day__gte=' + next_month.strftime("%Y-%m-%d")

    if request.user.is_authenticated and not request.user.is_staff:
        events = Event.objects.filter(Q(public=True) | Q(attendees__contains=request.user))
    elif not request.user.is_authenticated:
        events = Event.objects.filter(public=True)
    else:
        events = Event.objects.all()

    cal = EventHTMLCalendar(events)
    html_calendar = cal.formatmonth(d.year, d.month, withyear=True)
    html_calendar = html_calendar.replace('<td ', '<td  width="150" height="150"')
    extra_context['calendar'] = mark_safe(html_calendar)
    extra_context['page_title'] = "Events Calendar"

    return render(request, 'paxevents/calendar.html', extra_context)


def day_view(request):
    day = request.GET.get('day', None)
    extra_context = {}

    if not day:
        d = datetime.date.today()
    else:
        try:
            split_day = day.split('-')
            d = datetime.date(year=int(split_day[0]), month=int(split_day[1]), day=int(split_day[2]))
        except:
            d = datetime.date.today()

    events = Event.objects.filter(start_time__year=d.year,
                                  start_time__month=d.month,
                                  start_time__day=d.day)

    if request.user.is_authenticated and not request.user.is_staff:
        events = events.filter(Q(public=True) | Q(attendees__contains=request.user))
    elif not request.user.is_authenticated:
        events = events.filter(public=True)

    extra_context = {'page_title': 'Events',
                     'events': events,
                     'day': day}
    return render(request, 'paxevents/day.html', extra_context)


def event_view(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist, Event.ReturnedMultipleObjects:
        raise Http404

    if not event.public and request.user not in event.attendees:
        raise Http404

    extra_context = {'page_title': 'Event - ' + event.name,
                     'event': event}
    return render(request, 'paxevents/event.html', extra_context)
