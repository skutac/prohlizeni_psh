import os

from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'prohlizeni_psh.views.home', name='home'),
    # url(r'^prohlizeni_psh/', include('prohlizeni_psh.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    (r'^$', 'views.index'),
    (r'^(?P<subject_id>PSH\d+)$', 'views.get_concept'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(settings.ROOT, 'static')}),
    (r'^suggest$', 'views.suggest'),
)