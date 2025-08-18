=============
Installation
=============

Requirements
===========

Django Flexi Tag has the following requirements:

* Python: 2.7, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12
* Django: 1.10, 1.11, 2.0, 2.1, 2.2, 3.0, 3.1, 3.2, 4.0, 4.1, 4.2, 5.0
* Django REST Framework (for API endpoints)
* PostgreSQL database (required for JSONField and efficient tag queries)

Installation Steps
===============

1. Install the package using pip:

   .. code-block:: bash

       pip install dj-flexi-tag

2. Add 'flexi_tag' to your INSTALLED_APPS in settings.py:

   .. code-block:: python

       INSTALLED_APPS = [
           # ...
           'flexi_tag',
           # ...
       ]

3. Run migrations to create necessary database tables:

   .. code-block:: bash

       python manage.py migrate

Database Configuration
====================

Django Flexi Tag uses PostgreSQL's JSONField and GIN indexes for efficient tag storage and querying. Make sure your database settings in `settings.py` are configured for PostgreSQL:

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'your_db_name',
            'USER': 'your_db_user',
            'PASSWORD': 'your_db_password',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }

Next Steps
=========

After installation, you'll need to:

1. Make your models "taggable" by inheriting from FlexiTagMixin
2. Generate tag models using the management command (which will also automatically create migrations)
3. Apply migrations to create the new tag model tables
4. Add the TaggableViewSetMixin to your ViewSets for API support

See the :doc:`quickstart` guide for detailed instructions on these steps.
