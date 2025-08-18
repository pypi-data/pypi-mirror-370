from django.apps import apps

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
        tag_model = TaggableService.__get_tag_model_class(instance)
        tag_instance, created = tag_model.objects.get_or_create(instance=instance)

        tags = tag_instance.tags
        if not created and key in tags:
            raise TagValidationException(name=key)

        tags.append(key)

        tag_instance.tags = tags
        tag_instance.save(update_fields=["tags"])

        return instance

    def bulk_add_tags(self, instance, keys):
        tag_model = TaggableService.__get_tag_model_class(instance)
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
        tag_model = TaggableService.__get_tag_model_class(instances[0])
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
    def filter_by_tag(queryset, key):
        return queryset.filter_tag(key)

    @staticmethod
    def exclude_by_tag(queryset, key):
        return queryset.exclude_tag(key)

    @staticmethod
    def get_with_tags(queryset):
        return queryset.with_tags()
