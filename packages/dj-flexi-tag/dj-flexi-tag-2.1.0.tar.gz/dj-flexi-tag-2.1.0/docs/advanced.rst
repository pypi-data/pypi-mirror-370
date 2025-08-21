=============
Advanced Usage
=============

This guide covers advanced usage patterns and configurations for Django Flexi Tag's service-only architecture.

Service-Only Architecture Benefits
---------------------------------

Django Flexi Tag uses a service-only architecture that provides several advantages:

**Clean QuerySet Composition**

.. code-block:: python

    from flexi_tag.utils.service import TaggableService

    service = TaggableService()

    # Start with complex QuerySet
    complex_query = (Product.objects
                     .select_related('category', 'brand')
                     .prefetch_related('reviews')
                     .filter(is_active=True)
                     .filter(created_date__gte=last_month)
                     .annotate(avg_rating=Avg('reviews__rating')))

    # Add tag filtering - all previous filters preserved!
    tagged_products = service.filter_by_tag(complex_query, 'featured')

    # Chain multiple tag operations
    sale_featured = service.filter_by_tag(tagged_products, 'sale')
    not_archived = service.exclude_by_tag(sale_featured, 'archived')

Advanced Tag Operations
---------------------

**Multiple Tag Filtering**

.. code-block:: python

    service = TaggableService()

    # AND logic - must have ALL tags
    priority_items = service.filter_by_tags(
        Product.objects.all(),
        ['featured', 'sale', 'limited_edition']
    )

    # OR logic - must have ANY of these tags
    special_items = service.filter_by_any_tag(
        Product.objects.all(),
        ['featured', 'sale', 'new_arrival']
    )

**Performance Optimization**

.. code-block:: python

    # Use with_tags() to prefetch tag data and avoid N+1 queries
    products = service.with_tags(Product.objects.filter(is_active=True))

    for product in products:
        # No additional database hits here!
        tags = product.producttag.tags if hasattr(product, 'producttag') else []

**Conditional Tag Operations**

.. code-block:: python

    def apply_business_rules(order):
        service = TaggableService()

        # Auto-tag based on business logic
        if order.total_amount > 10000:
            service.add_tag(order, 'high_value')

        if order.customer.is_vip:
            service.add_tag(order, 'vip_customer')

        if order.created_date == timezone.now().date():
            service.add_tag(order, 'today')

        # Remove expired tags
        existing_tags = service.get_tags(order)
        if 'flash_sale' in existing_tags:
            if not order.is_flash_sale_active():
                service.remove_tag(order, 'flash_sale')

Bulk Operations and Performance
-----------------------------

**Efficient Bulk Processing**

.. code-block:: python

    def process_monthly_orders():
        """Process all orders from last month with batch operations"""
        last_month = timezone.now() - timedelta(days=30)
        orders = Order.objects.filter(created_date__gte=last_month)

        service = TaggableService()

        # Batch tag all orders from last month
        service.bulk_add_tags_with_many_instances(orders, ['processed', 'archived'])

        # Remove temporary tags efficiently
        temp_tagged = service.filter_by_tag(orders, 'temporary')
        service.bulk_remove_tags_with_many_instances(temp_tagged, ['temporary'])

Custom Exception Integration
---------------------------

Django Flexi Tag supports configurable base exception classes for seamless integration with your project's exception hierarchy.

**Basic Configuration**

.. code-block:: python

    # settings.py
    FLEXI_TAG_BASE_EXCEPTION_CLASS = 'myproject.exceptions.BaseAPIException'

**Your Custom Base Exception**

.. code-block:: python

    # myproject/exceptions.py
    class BaseAPIException(Exception):
        """Base exception for all API errors"""
        def __init__(self, message, status_code=400, error_code=None, *args, **kwargs):
            super().__init__(message, *args, **kwargs)
            self.status_code = status_code
            self.error_code = error_code

**Enhanced Exception Handling**

.. code-block:: python

    from flexi_tag.exceptions import TagValidationException

    try:
        service.add_tag(product, "duplicate_tag")
    except TagValidationException as e:
        print(e)                    # "tag_100_1:Tag already exists. name: duplicate_tag"
        print(e.status_code)        # 400 (inherited from BaseAPIException)
        print(e.error_code)         # None (inherited from BaseAPIException)

**Django REST Framework Integration**

.. code-block:: python

    # settings.py
    FLEXI_TAG_BASE_EXCEPTION_CLASS = 'rest_framework.exceptions.APIException'

    # Now all flexi-tag exceptions work seamlessly with DRF
    from flexi_tag.exceptions import TagValidationException
    from rest_framework.exceptions import APIException

    def my_view(request):
        try:
            service.add_tag(instance, "invalid_tag")
        except APIException as e:  # Can catch as DRF exception!
            return Response(
                {"error": str(e)},
                status=e.status_code if hasattr(e, 'status_code') else 400
            )

**Available Exception Types**

All these exceptions support custom base class configuration:

* ``TagValidationException`` - Tag already exists or validation fails
* ``TagNotFoundException`` - Tag not found during removal
* ``TagNotDefinedException`` - Required tag parameter missing
* ``ObjectIDsNotDefinedException`` - Required object IDs missing

**Error Codes**

Each exception has a unique error code:

.. code-block:: python

    from flexi_tag.exceptions import TagValidationException
    from flexi_tag import codes

    exception = TagValidationException(name="test")
    print(exception.code)  # Same as codes.tag_100_1

Custom Tag Model Configuration
----------------------------

The `generate_tag_models` command creates tag models with default settings, but you might want to customize this generation. You can create your own management command that extends the default one:

.. code-block:: python

    from django.core.management.base import BaseCommand
    from flexi_tag.management.commands.generate_tag_models import Command as BaseGenerateTagModelsCommand

    class Command(BaseGenerateTagModelsCommand):
        help = "Generate custom tag models for all models that inherit from FlexiTagMixin"

        def handle(self, *args, **options):
            # Customize the model template
            self.model_template = """
            # Custom model template
            from django.db import models
            from flexi_tag.utils.compat import JSONField

            class {{ model_name }}Tag(models.Model):
                instance = models.OneToOneField(
                    "{{ app_label }}.{{ model_name }}",
                    on_delete=models.CASCADE,
                    primary_key=True,
                )
                tags = JSONField(default=list)
                # Add custom fields here
                last_tagged_at = models.DateTimeField(auto_now=True)

                class Meta:
                    app_label = "{{ app_label }}"
                    db_table = "{{ app_label }}_{{ model_lower_name }}_tag"
            """
            super().handle(*args, **options)

Tag Validation
------------

You can implement custom tag validation by extending the TaggableService class:

.. code-block:: python

    from flexi_tag.utils.service import TaggableService
    from flexi_tag.exceptions import TagValidationException

    class MyTaggableService(TaggableService):
        def __validate_tag_key(self, key: str) -> bool:
            # Call the parent implementation
            super().__validate_tag_key(key)

            # Add custom validation
            if len(key) < 3:
                raise TagValidationException(name=key, message="Tag must be at least 3 characters long")

            # Only allow alphanumeric tags
            if not key.isalnum():
                raise TagValidationException(name=key, message="Tag must be alphanumeric")

            return True

Querying Tagged Objects
--------------------

To efficiently query objects by their tags, you can use PostgreSQL's JSON operators:

.. code-block:: python

    # Find all objects with a specific tag
    objects_with_tag = YourModel.objects.filter(yourmodeltag__tags__contains=["important"])

    # Find objects with any of these tags
    objects_with_any_tag = YourModel.objects.filter(yourmodeltag__tags__overlap=["urgent", "important"])

Using with Non-PostgreSQL Databases
---------------------------------

While Django Flexi Tag is optimized for PostgreSQL using its native JSON support, you can use it with other databases by customizing the tag model generation. For example, to use it with SQLite or MySQL:

1. Create a custom JSONField implementation
2. Update the model template in a custom management command
3. Ensure your database can efficiently query the tag field

Troubleshooting
--------------

Model Detection Issues
~~~~~~~~~~~~~~~~~~~~~

If the ``generate_tag_models`` command doesn't detect your newly added FlexiTagMixin models:

.. code-block:: bash

    # Try force reloading models
    python manage.py generate_tag_models --force-reload

    # Or restart your Django development server and try again
    python manage.py runserver

Common causes:

- Models module hasn't been imported yet
- Django's model cache hasn't been updated
- Circular import issues

Template Engine Issues
~~~~~~~~~~~~~~~~~~~~

If you encounter template engine configuration errors:

.. code-block:: python

    # Ensure your settings.py has proper TEMPLATES configuration
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    # ... your context processors
                ],
            },
        },
    ]

Performance Considerations
-----------------------

For large datasets, consider these performance optimizations:

1. Create database indexes on the tags field
2. Use batch processing for bulk tag operations
3. Consider denormalizing critical tag data for faster queries
4. Use caching for frequently accessed tag information

Security Considerations
--------------------

When implementing tag systems, be aware of these security concerns:

1. Validate tag input to prevent injection attacks
2. Implement permission checks for tag management
3. Consider the visibility of tags in your API responses
4. Audit tag changes for sensitive data
