from django.urls import path, re_path
from django.views.generic import RedirectView

urlpatterns = [
    # These URLs shadow django-allauth URLs to shut them down:
    path('signup/', RedirectView.as_view(url='/')),
    path('login/', RedirectView.as_view(url='/')),
    path('password/change/', RedirectView.as_view(url='/')),
    path('password/set/', RedirectView.as_view(url='/')),
    path('password/reset/', RedirectView.as_view(url='/')),
    path('password/reset/done/', RedirectView.as_view(url='/')),
    re_path('^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$',
            RedirectView.as_view(url='/')),
    path('password/reset/key/done/', RedirectView.as_view(url='/')),
    path('email/', RedirectView.as_view(url='/')),
    path('confirm-email/', RedirectView.as_view(url='/')),
    re_path('^confirm-email/(?P<key>[-:\\w]+)/$',
            RedirectView.as_view(url='/')),
]