from django.urls import path, reverse
from django.contrib import admin
from django.contrib.auth import REDIRECT_FIELD_NAME

from sustainability.Views import AdminSetupTwoFactorAuthView, AdminConfirmTwoFactorAuthView
from sustainability.models import AdminTwoFactorAuthData


class AdminSite(admin.AdminSite):
    def get_urls(self):
        base_urlpatterns = super().get_urls()

        extra_urlpatterns = [
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

    def login(self, request, *args, **kwargs):
        if request.method != 'POST':
            return super().login(request, *args, **kwargs)

        username = request.POST.get('username')

        # How you query the user depending on the username is up to you
        two_factor_auth_data = AdminTwoFactorAuthData.objects.filter(
            user__email=username
        ).first()

        request.POST._mutable = True
        request.POST[REDIRECT_FIELD_NAME] = reverse('admin:confirm-2fa')

        if two_factor_auth_data is None:
            request.POST[REDIRECT_FIELD_NAME] = reverse("admin:setup-2fa")

        request.POST._mutable = False

        return super().login(request, *args, **kwargs)