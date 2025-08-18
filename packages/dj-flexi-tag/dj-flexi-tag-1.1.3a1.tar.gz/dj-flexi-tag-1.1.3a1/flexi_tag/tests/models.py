from django.db import models

from flexi_tag.utils.compat import JSONField
from flexi_tag.utils.models import FlexiTagMixin


# Models from test_model_managers.py
class TaggableManagerTestModel(FlexiTagMixin):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = (
            "tests"  # Keeping this as 'tests' for compatibility with existing tests
        )


# Model from test_service.py
class ServiceTestModel(FlexiTagMixin):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = (
            "tests"  # Keeping this as 'tests' for compatibility with existing tests
        )


class ServiceTestModelTag(models.Model):
    instance = models.OneToOneField(
        "tests.ServiceTestModel",
        on_delete=models.CASCADE,
        primary_key=True,
    )
    tags = JSONField(default=list)

    class Meta:
        app_label = "tests"
