from django.conf.urls import url
from . import views
from evennia.web.website import views as website_views


urlpatterns = [
    url(r'^$', views.formtest_request, name="formtest_request"),
]
