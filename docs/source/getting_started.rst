Getting Started
==========================

------------
Requirements
------------

- Python
- Django
- DRF


------------
Installation
------------
DRF Rockstar Extensions can be installed with pip::

  pip install drf_rockstar_extensions


------------
Settings
------------
Some of DRF Rockstar Extensions can be customized through settings variable in settings.py:

.. code-block:: python

    DRF_ROCKSTAR = {
        'DEFAULT_FETCHER_FIELD_AUTH': 'drf_rockstar_extensions.fields.fetcher_field.basic_auth'
    }
