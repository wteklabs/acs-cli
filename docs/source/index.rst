Welcome to Azure Container Service Tools documentation!
=======================================================

Preparation
-----------

Create a config.ini by copying config.ini.tmpl and editing accoringly.

Create a `service principle`_ for the application and add the details
to your config.ini.

.. _Service Principle: http://rgardler.github.io/2016/02/10/create_keys_for_an_application_to_manage_azure

Basic Use
---------

The basic structure of an acs command is::

  acs <command> <args>

By default the config file `cluster.ini` will be used, if you want to
use a different config file use the `--config-file=FILE` option.

To get help for the CLI use::

  acs --help

Working with ACS Service
------------------------

The `service` commands provide convenience methods for managing an
instance of the Azure Container Service. Run `acs service help` for
more details.::

  acs service create

Once you have created your service you will likely want to open a
connection to it::

  acs service openTunnel

Now you can run commands against you Azure Container Service using any
tooling compatible with your chose orchestrator, such as the Docker
CLI for the Docker Swarm version of ACS and the DC/OS cli for the
DC/OS version.


.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

