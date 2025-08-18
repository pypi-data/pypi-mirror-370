
.. image:: https://readthedocs.org/projects/configcraft/badge/?version=latest
    :target: https://configcraft.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/configcraft-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/configcraft-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/configcraft-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/configcraft-project

.. image:: https://img.shields.io/pypi/v/configcraft.svg
    :target: https://pypi.python.org/pypi/configcraft

.. image:: https://img.shields.io/pypi/l/configcraft.svg
    :target: https://pypi.python.org/pypi/configcraft

.. image:: https://img.shields.io/pypi/pyversions/configcraft.svg
    :target: https://pypi.python.org/pypi/configcraft

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/configcraft-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/configcraft-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://configcraft.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/configcraft-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/configcraft-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/configcraft-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/configcraft#files


Welcome to ``configcraft`` Documentation
==============================================================================
.. image:: https://configcraft.readthedocs.io/en/latest/_static/configcraft-logo.png
    :target: https://configcraft.readthedocs.io/en/latest/

A Python library for DRY (Do not repeat yourself) configuration management with inheritance patterns and secure configuration merging.

📚 Full documentation is available at `HERE <https://configcraft.readthedocs.io/en/latest/>`_

**Key Features:**

- **🔄 Configuration Inheritance**: Use ``_shared`` sections to eliminate duplication across environments
- **🔒 Secure Config Merging**: Safely combine non-sensitive config with secrets without exposing credentials
- **🎯 JSON Path Patterns**: Apply defaults with flexible ``*.field`` and ``env.field`` patterns
- **📋 List Merging**: Intelligently merge lists by position to maintain data relationships
- **🛡️ Type Safety**: Structure-aware merging with validation and clear error messages


Quick Example
------------------------------------------------------------------------------
**Configuration Inheritance:**

.. code-block:: python

    from configcraft.api import apply_inheritance

    config = {
        "_shared": {
            "*.port": 8080,
            "*.timeout": 30
        },
        "dev": {
            "host": "localhost"
        },
        "prod": {
            "host": "api.company.com", 
            "port": 443
        }
    }

    apply_inheritance(config)
    # Result:
    # {
    #     "dev": {
    #         "host": "localhost", 
    #         "port": 8080, 
    #         "timeout": 30
    #     },
    #     "prod": {
    #         "host": "api.company.com", 
    #         "port": 443, 
    #         "timeout": 30
    #     }
    # }

**Secure Configuration Merging:**

.. code-block:: python

    from configcraft.api import deep_merge

    # config.json (safe to commit)
    base_config = {
        "database": {
            "host": "prod-db.com", 
            "port": 5432
        }
    }

    # secrets.json (never commit)
    secrets = {
        "database": {
            "password": "secret123"
        }
    }

    final_config = deep_merge(base_config, secrets)
    # Result:
    # {
    #     "database": {
    #         "host": "prod-db.com", 
    #         "port": 5432,
    #         "password": "secret123"
    #     }
    # }


.. _install:

Install
------------------------------------------------------------------------------

``configcraft`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install configcraft

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade configcraft
