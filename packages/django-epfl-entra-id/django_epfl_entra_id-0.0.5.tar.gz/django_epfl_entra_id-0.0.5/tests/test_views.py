from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from django_epfl_entra_id import views


class EPFLEntraIdLoginTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(
        OIDC_OP_AUTHORIZATION_ENDPOINT="https://server.example.com/auth"
    )
    @override_settings(OIDC_RP_CLIENT_ID="example_id")
    def test_next_url(self):
        url = reverse("epfl_entra_id_init")
        request = self.factory.get(
            "{url}?{params}".format(url=url, params="next=/foo")
        )
        request.session = dict()
        login_view = views.EPFLEntraIdLogin.as_view()
        login_view(request)
        self.assertEqual(request.method, "GET")
        self.assertEqual(request.path, "/admin/login/")
        self.assertEqual(request.get_full_path(), "/admin/login/?next=/foo")

    @override_settings(
        OIDC_OP_AUTHORIZATION_ENDPOINT="https://server.example.com/auth"
    )
    @override_settings(OIDC_RP_CLIENT_ID="example_id")
    def test_missing_next_url(self):
        url = reverse("epfl_entra_id_init")
        request = self.factory.get(url)
        request.session = dict()
        login_view = views.EPFLEntraIdLogin.as_view()
        login_view(request)
        self.assertEqual(request.method, "GET")
        self.assertEqual(request.path, "/admin/login/")
        self.assertEqual(request.get_full_path(), "/admin/login/")
