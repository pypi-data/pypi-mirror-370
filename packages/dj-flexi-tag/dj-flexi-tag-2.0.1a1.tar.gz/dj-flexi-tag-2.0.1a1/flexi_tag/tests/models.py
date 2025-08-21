from django.db import models

from flexi_tag.utils.compat import JSONField
from flexi_tag.utils.models import FlexiTagMixin


# Custom manager for testing
class CustomManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)

    def inactive(self):
        return self.filter(is_active=False)


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


# Test model with custom manager (to test manager preservation)
class CustomManagerTestModel(FlexiTagMixin):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    # Custom manager should be preserved
    objects = CustomManager()

    class Meta:
        app_label = "tests"


# Test model with no explicit manager (should get default objects + tag_objects)
class DefaultManagerTestModel(FlexiTagMixin):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "tests"


class ServiceTestModelTag(models.Model):
    instance = models.OneToOneField(
        "tests.ServiceTestModel",
        on_delete=models.CASCADE,
        primary_key=True,
    )
    tags = JSONField(default=list)

    class Meta:
        app_label = "tests"
