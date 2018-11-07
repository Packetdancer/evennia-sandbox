# URL patterns for the paxevents app

from django.conf.urls import url
from paxevents.views import calendar_view, day_view, event_view

urlpatterns = [
    url(r'^$', calendar_view, name="calendar"),
    url(r'day/$', day_view, name="day_view"),
    url(r'(?P<event_id>\d+)/$', event_view, name="event_view"),
]
