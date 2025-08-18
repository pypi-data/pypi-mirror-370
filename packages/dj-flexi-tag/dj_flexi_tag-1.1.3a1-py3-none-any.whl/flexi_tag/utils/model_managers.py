from django.apps import apps
from django.db import models


class TaggableManager(models.Manager):
    @staticmethod
    def __validate_tag_model_class(app_label, tag_model_name):
        try:
            return apps.get_model(app_label, tag_model_name)
        except LookupError:
            raise ValueError(
                "Tag model for {app_label}.{model_name} not found. Did you run 'python manage.py generate_tag_models', generate migration file and apply it?".format(
                    app_label=app_label,
                    model_name=tag_model_name,
                )
            )

    def __get_tag_model_class_name(self, model_class):
        model_name = model_class.__name__
        app_label = model_class._meta.app_label  # noqa
        tag_model_name = "{}Tag".format(model_name)
        self.__validate_tag_model_class(
            app_label=app_label,
            tag_model_name=tag_model_name,
        )

        return tag_model_name

    def filter_tag(self, key):
        model_class = self.model
        tag_model_class_name = self.__get_tag_model_class_name(model_class)

        query_filter = {"{}__tags__contains".format(tag_model_class_name): [key]}
        return self.get_queryset().filter(**query_filter)

    def exclude_tag(self, key):
        model_class = self.model
        tag_model_class_name = self.__get_tag_model_class_name(model_class)

        query_filter = {"{}__tags__contains".format(tag_model_class_name): [key]}
        return self.get_queryset().exclude(**query_filter)

    def with_tags(self):
        model_class = self.model
        tag_model_class_name = self.__get_tag_model_class_name(model_class)

        return self.get_queryset().prefetch_related(tag_model_class_name)
