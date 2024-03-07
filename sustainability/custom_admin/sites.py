from django.urls import path, reverse
from django.contrib import admin
from django.contrib.auth import REDIRECT_FIELD_NAME

from sustainability.Views import AdminSetupTwoFactorAuthView, AdminConfirmTwoFactorAuthView
from sustainability.models import AdminTwoFactorAuthData


class AdminSite(admin.AdminSite):  # defining the new admin site
    def get_urls(self):
        base_urlpatterns = super().get_urls()  # bringing in the default urls from the admin pageadmin

        extra_urlpatterns = [ # defining new urls for the admin page
            path(
                "setup-2fa/",
                self.admin_view(AdminSetupTwoFactorAuthView.as_view()),
                name="setup-2fa"
            ),
            path(
                "confirm-2fa/",
                self.admin_view(AdminConfirmTwoFactorAuthView.as_view()),
                name="confirm-2fa"
            )
        ]

        return extra_urlpatterns + base_urlpatterns

    def login(self, request, *args, **kwargs): # overriding the login function
        if request.method != 'POST':
            return super().login(request, *args, **kwargs)

        username = request.POST.get('username')

        two_factor_auth_data = AdminTwoFactorAuthData.objects.filter( # querying for the user
            user__email=username
        ).first()

        request.POST._mutable = True
        request.POST[REDIRECT_FIELD_NAME] = reverse('admin:confirm-2fa') # if the user has 2fa setup display the confirm page

        if two_factor_auth_data is None:
            request.POST[REDIRECT_FIELD_NAME] = reverse("admin:setup-2fa") # if the user doesnt have 2fa setup display the setup page

        request.POST._mutable = False

        return super().login(request, *args, **kwargs)

    def has_permission(self, request): # overriding the permissions function
        has_perm = super().has_permission(request)

        if not has_perm:
            return has_perm

        two_factor_auth_data = AdminTwoFactorAuthData.objects.filter( # checking for the user
            user=request.user
        ).first()

        allowed_paths = [
            reverse("admin:confirm-2fa"),
            reverse("admin:setup-2fa")
        ]

        if request.path in allowed_paths:
            return True

        if two_factor_auth_data is not None:
            two_factor_auth_token = request.session.get("2fa_token") # ensure the user has the 2fa token before allowing access

            return str(two_factor_auth_data.session_identifier) == two_factor_auth_token

        return False