from django.apps import apps
from django.db.models import Q

from flexi_tag.exceptions import TagNotFoundException, TagValidationException


class TaggableService:
    @staticmethod
    def __get_tag_model_class(instance):
        model_name = instance.__class__.__name__
        app_label = instance._meta.app_label  # noqa

        tag_model = "{}Tag".format(model_name)
        try:
            return apps.get_model(app_label, tag_model)
        except LookupError:
            raise ValueError(
                "Tag model for {app_label}.{model_name} not found. Did you run 'python manage.py generate_tag_models', generate migration file and apply it?".format(
                    app_label=app_label,
                    model_name=model_name,
                )
            )

    @staticmethod
    def __validate_tag_key(key):
        if not isinstance(key, str):
            raise ValueError("Tag key must be a string.")
        return True

    def add_tag(self, instance, key):
        self.__validate_tag_key(key)
        tag_model = self.__get_tag_model_class(instance)
        tag_instance, created = tag_model.objects.get_or_create(instance=instance)

        tags = tag_instance.tags
        if not created and key in tags:
            raise TagValidationException(name=key)

        tags.append(key)

        tag_instance.tags = tags
        tag_instance.save(update_fields=["tags"])

        return instance

    def bulk_add_tags(self, instance, keys):
        tag_model = self.__get_tag_model_class(instance)
        tag_instance, created = tag_model.objects.get_or_create(instance=instance)

        tags = tag_instance.tags
        if not created:
            for key in keys:
                self.__validate_tag_key(key)
                if key in tags:
                    raise TagValidationException(name=key)

        tags.extend(keys)
        tag_instance.tags = tags
        tag_instance.save(update_fields=["tags"])

        return instance

    def bulk_add_tags_with_many_instances(self, instances, keys):
        tag_model = self.__get_tag_model_class(instances[0])
        tags = []

        for instance in instances.iterator():
            tag_instance, created = tag_model.objects.get_or_create(instance=instance)
            if not created:
                for key in keys:
                    self.__validate_tag_key(key)
                    if key in tag_instance.tags:
                        raise TagValidationException(name=key)

            tags.extend(keys)
            tag_instance.tags = tags
            tag_instance.save(update_fields=["tags"])

        return instances

    def remove_tag(self, instance, key):
        tag_model = self.__get_tag_model_class(instance)

        tag_instance = tag_model.objects.filter(instance=instance).first()
        if not tag_instance:
            raise TagNotFoundException(name=key)

        if key in tag_instance.tags:
            tag_instance.tags.remove(key)
            tag_instance.save(update_fields=["tags"])
        else:
            raise TagValidationException(name=key)

        return tag_instance

    def bulk_remove_tags(self, instance, keys):
        tag_model = self.__get_tag_model_class(instance)

        tag_instance = tag_model.objects.filter(instance=instance).first()
        if not tag_instance:
            raise TagNotFoundException(name=keys)

        for key in keys:
            if key in tag_instance.tags:
                tag_instance.tags.remove(key)
            else:
                raise TagValidationException(name=key)

        tag_instance.save(update_fields=["tags"])

        return tag_instance

    def bulk_remove_tags_with_many_instances(
        self,
        instances,
        keys,
    ):
        tag_model = self.__get_tag_model_class(instances[0])

        for instance in instances.iterator():
            tag_instance = tag_model.objects.filter(instance=instance).first()
            if not tag_instance:
                raise TagNotFoundException(name=keys)

            for key in keys:
                if key in tag_instance.tags:
                    tag_instance.tags.remove(key)
                else:
                    raise TagValidationException(name=key)

            tag_instance.save(update_fields=["tags"])

        return instances

    def get_tags(self, instance):
        tag_model = self.__get_tag_model_class(instance)
        tag_instance = tag_model.objects.get(instance=instance)
        if not tag_instance:
            return []

        return tag_instance.tags

    @staticmethod
    def _get_tag_model_class_name(model_class):
        """Helper method to get tag model class name and validate it exists"""
        model_name = model_class.__name__
        app_label = model_class._meta.app_label
        tag_model_name = f"{model_name}Tag"

        # Validate tag model exists
        try:
            apps.get_model(app_label, tag_model_name)
        except LookupError:
            raise ValueError(
                f"Tag model for {app_label}.{model_name} not found. "
                f"Did you run 'python manage.py generate_tag_models', "
                f"generate migration file and apply it?"
            )

        return tag_model_name

    def filter_by_tag(self, queryset, key):
        """Filter queryset by tag key, preserving existing filters"""
        model_class = queryset.model
        tag_model_class_name = self._get_tag_model_class_name(model_class)

        query_filter = {f"{tag_model_class_name.lower()}__tags__contains": [key]}
        return queryset.filter(**query_filter)

    def exclude_by_tag(self, queryset, key):
        """Exclude queryset by tag key, preserving existing filters"""
        model_class = queryset.model
        tag_model_class_name = self._get_tag_model_class_name(model_class)

        query_filter = {f"{tag_model_class_name.lower()}__tags__contains": [key]}
        return queryset.exclude(**query_filter)

    def with_tags(self, queryset):
        """Add prefetch_related for tag objects, preserving existing queryset"""
        model_class = queryset.model
        tag_model_class_name = self._get_tag_model_class_name(model_class)

        return queryset.prefetch_related(tag_model_class_name.lower())

    def filter_by_tags(self, queryset, tags):
        """Filter queryset by multiple tags (AND logic)"""
        if not tags:
            return queryset

        for tag in tags:
            queryset = self.filter_by_tag(queryset, tag)
        return queryset

    def filter_by_any_tag(self, queryset, tags):
        """Filter queryset by any of the tags (OR logic)"""
        if not tags:
            return queryset

        model_class = queryset.model
        tag_model_class_name = self._get_tag_model_class_name(model_class)

        q_objects = Q()
        for tag in tags:
            query_filter = {f"{tag_model_class_name.lower()}__tags__contains": [tag]}
            q_objects |= Q(**query_filter)

        return queryset.filter(q_objects)
