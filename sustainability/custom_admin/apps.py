from django.contrib.admin.apps import AdminConfig as BaseAdminConfig


class CustomAdminConfig(BaseAdminConfig):
    default_site = "sustainability.custom_admin.sites.AdminSite"
