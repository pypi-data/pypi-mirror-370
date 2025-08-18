==========
Contributing
==========

We welcome contributions to dj-flexi-tag! Here's how you can help:

Setting Up for Development
========================

1. Fork the repository on Bitbucket
2. Clone your fork locally:

   .. code-block:: bash

       git clone https://bitbucket.org/your-username/dj-flexi-tag.git
       cd dj-flexi-tag

3. Create a virtual environment and install development dependencies:

   .. code-block:: bash

       python -m venv venv
       source venv/bin/activate  # On Windows: venv\Scripts\activate
       pip install -e ".[dev,test,docs]"

4. Set up pre-commit hooks:

   .. code-block:: bash

       pre-commit install

Running Tests
==========

We use tox to run tests across different Python and Django versions:

.. code-block:: bash

    tox

To run tests for a specific environment:

.. code-block:: bash

    tox -e py39-django32

Or to run tests with your current Python version:

.. code-block:: bash

    python runtests.py

Code Style
=========

We follow PEP 8 and use Black for code formatting. Run Black before submitting:

.. code-block:: bash

    black flexi_tag

We also use ruff for linting:

.. code-block:: bash

    ruff flexi_tag

Documentation
===========

To build the documentation locally:

.. code-block:: bash

    cd docs
    make html

The documentation will be available in `_build/html/`.

Pull Request Process
=================

1. Create a new branch for your feature or bugfix: `git checkout -b feature/your-feature-name`
2. Make your changes and add tests
3. Ensure all tests pass: `tox`
4. Update documentation if needed
5. Push your branch: `git push origin feature/your-feature-name`
6. Submit a pull request to the main repository

We aim to review and respond to pull requests within a few days.

Reporting Issues
==============

When reporting issues, please include:

* A clear description of the problem
* Steps to reproduce
* Expected vs. actual behavior
* Django and Python versions
* Any relevant logs or error messages

Feature Requests
=============

Feature requests are welcome! Please provide:

* A clear description of the feature
* Any relevant use cases
* How the feature would benefit the project

Release Process
============

For maintainers, the release process is:

1. Update version in setup.py
2. Update CHANGELOG.md
3. Create a new tag: `git tag vX.Y.Z`
4. Push the tag: `git push origin vX.Y.Z`
5. The CI/CD pipeline will build and publish to PyPI

Code of Conduct
============

We expect all contributors to be respectful and considerate of others. Any form of harassment or discriminatory behavior will not be tolerated.
