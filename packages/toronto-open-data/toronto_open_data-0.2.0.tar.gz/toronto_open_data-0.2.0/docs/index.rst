Welcome to Toronto Open Data's documentation!
==============================================

The ``TorontoOpenData`` package provides a Python interface to interact with the Toronto Open Data portal. It allows users to list, search, and download datasets, as well as load specific resources.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   api
   examples
   contributing

Features
--------

* **Easy Dataset Access**: List and search all available datasets
* **Smart File Loading**: Automatically detect and load various file formats
* **Datastore API**: Query data directly with SQL-like syntax
* **Caching**: Intelligent caching to avoid re-downloading files
* **Type Safety**: Proper data type enforcement for datastore queries

Quick Start
-----------

.. code-block:: python

   from toronto_open_data import TorontoOpenData

   # Initialize the client
   tod = TorontoOpenData()

   # List all datasets
   datasets = tod.list_all_datasets()

   # Search for specific datasets
   parks_data = tod.search_datasets('parks')

   # Load a dataset directly
   data = tod.load('dataset-name', 'file.csv')

   # Use the datastore API for real-time data
   live_data = tod.datastore_search('resource-id', limit=100)

Installation
-----------

.. code-block:: bash

   pip install toronto-open-data

For development:

.. code-block:: bash

   pip install toronto-open-data[dev]

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
