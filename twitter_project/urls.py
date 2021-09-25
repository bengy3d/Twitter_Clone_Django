from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf.urls.static import static

import notifications.urls

urlpatterns = [
    path('this-is-not-admin/', admin.site.urls),
    # User manager
    path('accounts/', include('users.urls')),
    path('accounts/', include('allauth.urls')),
    # Notifications
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    # Local apps
    path('', include('pages.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
