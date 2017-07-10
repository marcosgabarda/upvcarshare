# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.views import defaults as default_views
from django.views.i18n import javascript_catalog

from config.router import urlpatterns as api_urlpatterns
from core.views import PartialsTemplateView
from pages.views import HomeView

urlpatterns = [
    url(r"^$", HomeView.as_view(), name="home"),
    url(r"^", include("pages.urls", namespace="pages")),
    url(r"^users/", include("users.urls", namespace="users")),
    url(r"^journeys/", include("journeys.urls", namespace="journeys")),
    url(r"^notifications/", include("notifications.urls", namespace="notifications")),
]

# Partials URLs
urlpatterns += [
    url(r'^partials/(?P<name>.+)\.html', PartialsTemplateView.as_view(), name="partials-template"),
]

# OpenID URLs
urlpatterns += [
    url(r"^accounts/signup/$", default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
    url(r"^accounts/login/$", default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
    url(r"^accounts/logout/$", default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
    url(r'^accounts/', include('allauth.urls')),
]

# Admin URLs
admin.site.site_header = _('UPV Car Share Admin')
urlpatterns += [
    url(r'^admin/', admin.site.urls),
]

# API URLs
# Create a router and register our resources with it.
urlpatterns += [
    url(r'^api/v1/', include(api_urlpatterns, namespace="api_v1")),
]

# JavaScript i18n
js_info_dict = {
    'packages': ('recurrence', ),
}
urlpatterns += [
    url(r'^jsi18n/$', javascript_catalog, js_info_dict),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    # Media URLs on debug
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # If is installed debug_toolbar, add its urls
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]
