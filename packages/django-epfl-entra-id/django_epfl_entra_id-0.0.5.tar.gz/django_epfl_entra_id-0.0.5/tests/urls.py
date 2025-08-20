import django

if django.VERSION >= (3, 1, 0):
    from django.urls import include
    from django.urls import re_path as url
else:
    from django.conf.urls import include, url

urlpatterns = [
    url("", include("django_epfl_entra_id.urls")),
    url(r"^auth/", include("mozilla_django_oidc.urls")),
]
