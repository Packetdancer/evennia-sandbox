import calendar
from .models import Event
import pytz
from django.utils.timezone import get_default_timezone
from django.core.urlresolvers import reverse


def localize_datetime(timestamp, tz=None):
    if tz is not None and isinstance(tz, basestring):
        tz = pytz.timezone(tz)

    if not tz:
        tz = get_default_timezone()

    localized = timestamp.astimezone(tz)

    return localized


class EventHTMLCalendar(calendar.HTMLCalendar):

    def __init__(self, events):
        super(EventHTMLCalendar, self).__init__()
        self.year = None
        self.month = None
        self.visible_events = events

    def formatday(self, day, weekday, events):
        """
        Return a day as a table cell.
        """
        events_from_day = events.filter(start_time__day=day)
        events_html = "<span style='font-size: 8pt'>"
        for event in events_from_day:
            localized = localize_datetime(event.start_time)
            event_time = localized.strftime("%H:%M")
            event_link = reverse("paxevents:event_view", kwargs={'event_id': event.id})
            events_html += "<li><a href='" + event_link + "'>" + event_time + ": " + event.name + "</a></li>"
        events_html += "</span>"

        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        else:
            if self.year is not None and self.month is not None:
                day_url = reverse("paxevents:day_view") + "?day=" + str(self.year) + "-" + str(self.month) + "-" + str(day)
                return '<td class="%s" valign="top"><a href="%s">%d</a>%s</td>' % (self.cssclasses[weekday], day_url, day, events_html)
            else:
                return '<td class="%s" valign="top">%d%s</td>' % (self.cssclasses[weekday], day, events_html)

    def formatweek(self, theweek, events):
        """
        Return a complete week as a table row.
        """
        s = ''.join(self.formatday(d, wd, events) for (d, wd) in theweek)
        return '<tr>%s</tr>' % s

    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """

        events = self.visible_events.filter(start_time__month=themonth,
                                            start_time__year=theyear)

        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        self.year = theyear
        self.month = themonth
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week, events))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)
