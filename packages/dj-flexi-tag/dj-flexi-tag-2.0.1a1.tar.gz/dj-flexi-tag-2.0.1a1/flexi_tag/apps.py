from django.apps import AppConfig


class FlexiTagConfig(AppConfig):
    """
    Django application configuration for Flexi Tag.

    Flexi Tag provides a flexible, service-only tagging system for Django
    that avoids manager conflicts and provides powerful QuerySet composition.
    """

    name = "flexi_tag"
    verbose_name = "Flexi Tag"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """
        Application initialization.

        The service-only architecture requires no special initialization
        as it doesn't rely on model metaclasses or custom managers.
        """
        pass
