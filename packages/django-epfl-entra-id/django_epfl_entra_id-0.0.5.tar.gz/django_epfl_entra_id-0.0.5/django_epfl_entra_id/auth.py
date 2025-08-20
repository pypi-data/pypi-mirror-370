import jwt
from django.apps import apps
from django.conf import settings
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

OIDC_USER_MAPPING = (
    ("username", "gaspar"),
    ("email", "email"),
    ("first_name", "given_name"),
    ("last_name", "family_name"),
)


class EPFLOIDCAB(OIDCAuthenticationBackend):
    def filter_users_by_claims(self, claims):
        sciper = claims.get("uniqueid")
        if not sciper:
            return self.UserModel.objects.none()

        is_app_using_profile = hasattr(settings, "AUTH_PROFILE_MODULE")

        if is_app_using_profile:
            user_profile_model = apps.get_model(
                *settings.AUTH_PROFILE_MODULE.split(".")
            )
            try:
                user_profile = user_profile_model.objects.filter(
                    sciper=sciper
                ).latest("id")
                return self.UserModel.objects.filter(id=user_profile.user.id)
            except user_profile_model.DoesNotExist:
                return self.UserModel.objects.none()
        else:
            return self.UserModel.objects.filter(sciper=sciper)

    def __rename_conflicting_user(self, claims):
        """
        Rename any existing user in the database with the same username
        (usually a user who has left), appending '-inactive-<user_id>' to
        avoid username conflicts when creating a new user or updating a user
        """
        username = claims.get("gaspar")
        sciper = claims.get("sciper")
        is_app_using_profile = hasattr(settings, "AUTH_PROFILE_MODULE")

        try:
            existing_user = self.UserModel.objects.get(username=username)

            if is_app_using_profile:
                user_profile_model = apps.get_model(
                    *settings.AUTH_PROFILE_MODULE.split(".")
                )
                existing_user_profile = user_profile_model.objects.get(
                    user=existing_user
                )
                existing_user_sciper = getattr(
                    existing_user_profile, "sciper", None
                )
            else:
                existing_user_sciper = getattr(existing_user, "sciper", None)

            if existing_user_sciper != sciper:
                existing_user.username = (
                    f"{existing_user.username}-inactive-{existing_user.id}"
                )
                existing_user.save()
        except self.UserModel.DoesNotExist:
            pass

    def create_user(self, claims):
        self.__rename_conflicting_user(claims)

        is_app_using_profile = hasattr(settings, "AUTH_PROFILE_MODULE")

        if is_app_using_profile:
            user = self.UserModel.objects.create_user(
                username=claims.get("gaspar"),
                email=claims.get("email"),
                first_name=claims.get("given_name"),
                last_name=claims.get("family_name"),
            )
            user_profile_model = apps.get_model(
                *settings.AUTH_PROFILE_MODULE.split(".")
            )
            profile, _ = user_profile_model.objects.get_or_create(user=user)
            profile.sciper = claims.get("uniqueid")
            profile.save()
        else:
            user = self.UserModel.objects.create_user(
                username=claims.get("gaspar"),
                email=claims.get("email"),
                first_name=claims.get("given_name"),
                last_name=claims.get("family_name"),
                sciper=claims.get("uniqueid"),
            )

        return user

    def update_user(self, user, claims):
        self.__rename_conflicting_user(claims)

        for model_field, oidc_field in OIDC_USER_MAPPING:
            if claims.get(oidc_field):
                setattr(user, model_field, claims.get(oidc_field))

        user.save()
        return user

    def get_userinfo(self, access_token, id_token, payload):
        """
        Get user info from both user info endpoint (default) and
        merge with ID token information.
        """
        userinfo = super(EPFLOIDCAB, self).get_userinfo(
            access_token, id_token, payload
        )

        id_token_decoded: str = jwt.decode(
            id_token, options={"verify_signature": False}
        )

        userinfo.update(id_token_decoded)

        return userinfo
