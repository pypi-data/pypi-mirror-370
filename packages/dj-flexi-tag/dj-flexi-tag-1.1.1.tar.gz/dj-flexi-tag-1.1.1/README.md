# Django Flexi Tag

[![Build status](https://img.shields.io/bitbucket/pipelines/akinonteam/dj-flexi-tag)](https://bitbucket.org/akinonteam/dj-flexi-tag/addon/pipelines/home)
[![Documentation status](https://readthedocs.org/projects/dj-flexi-tag/badge/?version=latest)](https://dj-flexi-tag.readthedocs.io/en/latest/?badge=latest)
![PyPI](https://img.shields.io/pypi/v/dj-flexi-tag)
![PyPI - Django version](https://img.shields.io/pypi/djversions/dj-flexi-tag)
![PyPI - Python version](https://img.shields.io/pypi/pyversions/dj-flexi-tag)
![PyPI - License](https://img.shields.io/badge/License-MIT-green.svg)

A flexible and efficient tagging system for Django models that allows you to add, remove, and manage tags on any Django model with minimal configuration.

## Features

- **Easy Integration**: Works seamlessly with Django REST Framework ViewSets
- **Flexible Tag Storage**: Uses PostgreSQL JSONField for efficient and flexible tag storage
- **Automatic Model Generation**: Generates auxiliary Tag models for your existing models
- **Bulk Operations**: Support for bulk tag operations on multiple objects
- **Django Compatibility**: Works across multiple Django versions (1.10 to 5.0)
- **Python Compatibility**: Supports Python 2.7 and Python 3.4+

## Installation

Installation using pip:

```
pip install dj-flexi-tag
```

For development and testing:

```
pip install dj-flexi-tag[dev,test]
```

For documentation development:

```
pip install dj-flexi-tag[docs]
```

For all dependencies:

```
pip install dj-flexi-tag[dev,test,docs]
```

Add `flexi_tag` to your `INSTALLED_APPS` and run migrations:

```python
INSTALLED_APPS = (
    # other apps here...
    'flexi_tag',
)
```

## Testing

Run the tests with:

```
python runtests.py
```

Use the `--verbose` flag for more detailed output:

```
python runtests.py --verbose
```

Use the `--interactive` flag for interactive mode:

```
python runtests.py --interactive
```

## Basic Usage

### 1. Define Your Models with FlexiTagMixin

```python
from flexi_tag.utils.models import FlexiTagMixin

class YourModel(FlexiTagMixin):
    name = models.CharField(max_length=100)
    # other fields...
```

### 2. Generate Tag Models

Run the management command:

```
python manage.py generate_tag_models
```

This will create a `flexi_generated_model.py` file in the same directory as your model, which contains a `YourModelTag` model. The command will also automatically add the appropriate import statement to your models.py file and run `makemigrations` to generate migration files for the new models.

```python
from .flexi_generated_model import YourModelTag  # noqa
```

If multiple tag models are generated, they will be imported in a single line:

```python
from .flexi_generated_model import FirstModelTag, SecondModelTag  # noqa
```

### 3. Apply Migrations

After the tag models have been generated and migrations created, apply them with:

```
python manage.py migrate
```

### 4. Add Tagging to Your ViewSet

```python
from rest_framework import viewsets
from flexi_tag.utils.views import TaggableViewSetMixin
from .models import YourModel

class YourModelViewSet(viewsets.ModelViewSet, TaggableViewSetMixin):
    queryset = YourModel.objects.all()
    serializer_class = YourModelSerializer
```

### 5. Use the Tagging API

Add a tag:
```
POST /your-model/1/add_tag/
{"key": "important"}
```

Add multiple tags:
```
POST /your-model/1/bulk_add_tag/
{"keys": ["important", "urgent"]}
```

Remove a tag:
```
POST /your-model/1/remove_tag/
{"key": "important"}
```

## Advanced Usage

For more advanced usage, including programmatic tag management, custom tag validation, and more detailed configuration options, please refer to the [documentation](https://dj-flexi-tag.readthedocs.io).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
