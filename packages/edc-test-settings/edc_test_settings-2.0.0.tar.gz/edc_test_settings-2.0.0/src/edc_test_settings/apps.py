from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_test_settings"
    verbose_name = "Edc Test Settings"
    has_exportable_data = False
    default_auto_field = "django.db.models.BigAutoField"
    include_in_administration_section = False
