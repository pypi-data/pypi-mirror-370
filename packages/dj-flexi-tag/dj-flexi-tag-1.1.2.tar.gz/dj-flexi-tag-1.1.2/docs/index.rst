=============
dj-flexi-tag
=============

A flexible and efficient tagging system for Django models.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction
   installation
   quickstart
   advanced
   api
   contributing

Overview
===========

Django Flexi Tag is a powerful tagging solution for Django projects that makes it easy to add tagging functionality to any model. Unlike traditional tagging libraries that use many-to-many relationships, dj-flexi-tag uses PostgreSQL's native JSON capabilities for efficient and flexible tag storage.

Key Features
===========

* **Automatic Model Generation**: Automatically creates tag models for your existing models
* **REST API Integration**: Includes ViewSet mixins for complete API support
* **Efficient Storage**: Uses JSONField for optimal tag storage and querying
* **Bulk Operations**: Support for adding/removing tags in bulk operations
* **Flexible Implementation**: Works with any Django model
* **Django Compatibility**: Works with Django 1.10 to 5.0
* **Python Compatibility**: Supports Python 2.7 and 3.4+

Quick Start
==========

1. Install the package:

.. code-block:: bash

    pip install dj-flexi-tag

2. Add to your INSTALLED_APPS:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'flexi_tag',
        # ...
    ]

3. Make your model taggable:

.. code-block:: python

    from flexi_tag.utils.models import FlexiTagMixin
    
    class Product(FlexiTagMixin):
        name = models.CharField(max_length=100)
        # other fields...

4. Generate tag models:

.. code-block:: bash

    python manage.py generate_tag_models

5. Create and apply migrations:

.. code-block:: bash

    python manage.py makemigrations
    python manage.py migrate

6. Add tagging to your ViewSet:

.. code-block:: python

    from rest_framework import viewsets
    from flexi_tag.utils.views import TaggableViewSetMixin
    
    class ProductViewSet(viewsets.ModelViewSet, TaggableViewSetMixin):
        queryset = Product.objects.all()
        serializer_class = ProductSerializer

Now you can use the tagging API to add, remove, and manage tags on your models!

API Usage Example
===============

Add a tag to an object:

.. code-block:: http

    POST /api/products/1/add_tag/
    {"key": "featured"}

Add multiple tags:

.. code-block:: http

    POST /api/products/1/bulk_add_tag/
    {"keys": ["sale", "new-arrival"]}

Remove a tag:

.. code-block:: http

    POST /api/products/1/remove_tag/
    {"key": "featured"}
