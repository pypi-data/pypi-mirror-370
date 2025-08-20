# django-epfl-entra-id

[![Test Status][github-actions-image]][github-actions-url]
[![Coverage Status][codecov-image]][codecov-url]
[![PyPI version][pypi-image]][pypi-url]

Custom [Microsoft Entra ID][entra-id] Authentication Backend for Django.

## Requirements

- Python 3.6 or later
- Django 1.11, 2.2, 3.2, 4.2 or 5.2

## Installation

```bash
pip install django-epfl-entra-id
```

## Documentation

### Settings

Add `mozilla_django_oidc` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
  ...
  "django.contrib.auth",
  "mozilla_django_oidc",  # Load after auth
  ...
]
```

Add `django_epfl_entra_id` authentication backend:

```python
AUTHENTICATION_BACKENDS = ("django_epfl_entra_id.auth.EPFLOIDCAB",)
```

Register your application in the [App Portal][app-portal] and add the OIDC
configuration:

```python
TENANT_ID = os.environ["TENANT_ID"]

OIDC_RP_CLIENT_ID = os.environ["OIDC_RP_CLIENT_ID"]
OIDC_RP_CLIENT_SECRET = os.environ["OIDC_RP_CLIENT_SECRET"]

AUTH_DOMAIN = f"https://login.microsoftonline.com/{TENANT_ID}"
OIDC_OP_AUTHORIZATION_ENDPOINT = f"{AUTH_DOMAIN}/oauth2/v2.0/authorize"
OIDC_OP_TOKEN_ENDPOINT = f"{AUTH_DOMAIN}/oauth2/v2.0/token"
OIDC_OP_JWKS_ENDPOINT = f"{AUTH_DOMAIN}/discovery/v2.0/keys"
OIDC_OP_USER_ENDPOINT = "https://graph.microsoft.com/oidc/userinfo"
OIDC_RP_SIGN_ALGO = "RS256"

LOGIN_URL = "/auth/authenticate"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
```

### Routing

Edit your `urls.py` and add the following:

```python
urlpatterns = [
  ...
  path("", include("django_epfl_entra_id.urls")),
  path("auth/", include("mozilla_django_oidc.urls")),
  ...
]
```

Example template:

```htmldjango
{% if user.is_authenticated %}
  <p>Current user: {{ user.username }}</p>
  <form action="{% url 'oidc_logout' %}" method="post">
    {% csrf_token %}
    <input type="submit" value="logout">
  </form>
{% else %}
  <a href="{% url 'oidc_authentication_init' %}?next={{ request.path }}">
    Login
  </a>
{% endif %}
```

### Optional configuration

```python
AUTH_PROFILE_MODULE = "userprofile.UserProfile"
```

[github-actions-image]: https://github.com/epfl-si/django-epfl-entra-id/actions/workflows/test.yml/badge.svg?branch=main
[github-actions-url]: https://github.com/epfl-si/django-epfl-entra-id/actions/workflows/test.yml

[codecov-image]: https://codecov.io/gh/epfl-si/django-epfl-entra-id/graph/badge.svg
[codecov-url]: https://codecov.io/gh/epfl-si/django-epfl-entra-id

[entra-id]: https://inside.epfl.ch/identite-numerique/en/digital-identity-protection/
[app-portal]: https://app-portal.epfl.ch/

[pypi-image]: https://img.shields.io/pypi/v/django-epfl-entra-id
[pypi-url]: https://pypi.org/project/django-epfl-entra-id/
