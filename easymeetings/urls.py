from django.conf.urls import patterns, include, url
from django.contrib import admin
from meetingmanagement import urls
from django.conf import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'easymeetings.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('meetingmanagement.urls')),
)

urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )
