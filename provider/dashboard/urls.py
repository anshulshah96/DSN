"""provider URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from dashboard.views import *
urlpatterns = [
    url(r'^$', index),
    url(r'^upload/$', upload_file),
    url(r'^challenge/$', challenge),
    url(r'^download/(?P<client>[a-zA-Z0-9]*)/(?P<service_num>.*)/$', download),
    url(r'^status/$', status),
    url(r'^generate_data/(?P<address>.*)/$', generate_data),
    url(r'^get_status/(?P<address>.*)/$', get_status)
]
