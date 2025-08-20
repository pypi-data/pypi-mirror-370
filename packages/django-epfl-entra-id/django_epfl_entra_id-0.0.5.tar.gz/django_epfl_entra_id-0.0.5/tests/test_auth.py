from django.test import TestCase, override_settings

from django_epfl_entra_id.auth import EPFLOIDCAB


class EPFLOIDCABTestCase(TestCase):
    """Authentication tests."""

    @override_settings(OIDC_OP_TOKEN_ENDPOINT="https://server.epfl.ch/token")
    @override_settings(OIDC_OP_USER_ENDPOINT="https://server.epfl.ch/user")
    @override_settings(OIDC_RP_CLIENT_ID="example_id")
    @override_settings(OIDC_RP_CLIENT_SECRET="client_secret")
    def setUp(self):
        self.backend = EPFLOIDCAB()

    def test_missing_request_arg(self):
        self.assertIsNone(self.backend.authenticate(request=None))
