from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import View


class EPFLEntraIdLogin(View):
    def get(self, request, **kwargs):
        """Redirect admin/login/ to Entra ID."""
        url = reverse("oidc_authentication_init")
        return HttpResponseRedirect(
            url
            + (
                "?next={}".format(request.GET["next"])
                if "next" in request.GET
                else ""
            )
        )
