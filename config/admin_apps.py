from django.contrib.admin.apps import AdminConfig


class TransConnectAdminConfig(AdminConfig):
    default_site = 'config.admin_site.TransConnectAdminSite'
