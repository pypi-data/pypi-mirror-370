import django

from django_epfl_entra_id import views

if django.VERSION >= (3, 1, 0):
    from django.urls import re_path as url
else:
    from django.conf.urls import url

urlpatterns = [
    url(
        r"admin/login/$",
        views.EPFLEntraIdLogin.as_view(),
        name="epfl_entra_id_init",
    ),
]
