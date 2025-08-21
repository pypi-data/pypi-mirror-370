=============
Introduction
=============

Django Flexi Tag is a flexible and customizable tagging solution for Django projects. It provides a seamless way to add tagging functionality to any Django model using a service-only architecture for maximum compatibility, and integrates with Django REST Framework to provide a rich API for tag management.

Problem Statement
----------------

In many web applications, there's a need to "tag" or "mark" objects with simple identifiers for various purposes:

* Marking items for follow-up actions
* Categorizing content
* Creating custom workflows
* Applying status indicators
* Implementing feature flags

Traditional tagging solutions often require creating many-to-many relationships between models, which can become complex and inefficient as the number of tags and tagged objects grows.

Solution
--------

Django Flexi Tag takes a different approach:

1. It uses PostgreSQL's JSONField for efficient tag storage
2. It automatically generates auxiliary tag models for your existing models
3. It provides a comprehensive API for managing tags
4. It integrates with Django REST Framework for easy API access

Key Concepts
-----------

* **FlexiTagMixin**: A simple abstract mixin class that marks your model as "taggable"
* **TaggableService**: A service class that provides instance methods for managing tags and filtering QuerySets
* **Tag Model Generation**: A management command that generates the auxiliary models needed for tagging
* **TaggableViewSetMixin**: A mixin for ViewSets that provides API endpoints for tag management
* **Custom Exceptions**: Configurable exception classes that can inherit from your project's base exception

Architecture Benefits
-------------------

* **Service-Only Approach**: Clean architecture that works with any existing Django setup
* **QuerySet Composition**: Easily combine tag filtering with existing model filters
* **Maximum Compatibility**: Works with existing Django patterns, third-party packages, and complex inheritance
* **Custom Exception Integration**: Seamlessly integrates with your project's exception handling

With Django Flexi Tag, you can quickly add powerful tagging functionality to your Django application with minimal configuration and maximum flexibility.
