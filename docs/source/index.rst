Welcome to Azure Container Service Tools documentation!
=======================================================

Preparation
-----------

Create a config.ini by copying config.ini.tmpl and editing accoringly.

Create a [service principle for the
application](http://rgardler.github.io/2016/02/10/create_keys_for_an_application_to_manage_azure)
and add the details to your config.ini.

Basic Use
---------

``
acs <command> <args>
``

By defaultthe config file `cluster.ini` will be use3d, if you want to
use a different config file use the `--config-file=FILE` option.

To get help for the CLI use:

`` 
acs --help
``

Service commands
----------------

The `service` commands provide convenience methods for managing an
instance of the Azure Container Service. Run `acs service help` for
more details.

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

