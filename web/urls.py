"""
Url definition file to redistribute incoming URL requests to django
views. Search the Django documentation for "URL dispatcher" for more
help.

"""
from django.conf.urls import url, include

# default evennia patterns
from evennia.web.urls import urlpatterns
import formtest.urls

# eventual custom patterns
custom_patterns = [
    url(r'^formtest/', include(formtest.urls, namespace='formtest', app_name='formtest'))
]

# this is required by Django.
urlpatterns = custom_patterns + urlpatterns
