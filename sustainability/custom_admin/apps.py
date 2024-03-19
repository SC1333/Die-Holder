from django.contrib.admin.apps import AdminConfig as BaseAdminConfig

"""Written by Thomas Shannon"""

class CustomAdminConfig(BaseAdminConfig):
    default_site = "sustainability.custom_admin.sites.AdminSite"  # defines the default admin site
