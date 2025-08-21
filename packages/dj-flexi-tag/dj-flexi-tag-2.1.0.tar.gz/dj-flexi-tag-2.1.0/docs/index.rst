=============
dj-flexi-tag
=============

A flexible and efficient tagging system for Django models with service-only architecture.

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

Django Flexi Tag is a powerful tagging solution for Django projects built with a **service-only architecture** for maximum compatibility and composability. Unlike traditional tagging libraries that rely on complex many-to-many relationships, dj-flexi-tag uses PostgreSQL's native JSON capabilities and a clean service layer for efficient and flexible tag management.

Key Features
===========

* **🚀 Service-Only Architecture**: Clean and composable design with full QuerySet compatibility
* **🔄 Composable Filtering**: Preserves existing QuerySet filters when adding tag filtering
* **⚡ Easy Integration**: Works seamlessly with Django REST Framework ViewSets
* **📦 Flexible Tag Storage**: Uses PostgreSQL JSONField for efficient and flexible tag storage
* **🤖 Automatic Model Generation**: Generates auxiliary Tag models for your existing models
* **📊 Bulk Operations**: Support for bulk tag operations on multiple objects
* **🎯 Custom Exception Integration**: Configurable base exception classes for seamless project integration
* **🌐 Django Compatibility**: Works across multiple Django versions (1.11 to 5.0)
* **🐍 Python Compatibility**: Supports Python 3.5+

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

6. Use the service to add tags:

.. code-block:: python

    from flexi_tag.utils.service import TaggableService

    # Add tags to instances
    service = TaggableService()
    service.add_tag(product, 'featured')
    service.bulk_add_tags(product, ['sale', 'new-arrival'])

    # Filter QuerySets by tags - preserves existing filters!
    featured_products = service.filter_by_tag(Product.objects.filter(is_active=True), 'featured')

7. Add tagging to your ViewSet (optional for REST API):

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
