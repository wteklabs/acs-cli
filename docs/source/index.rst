Welcome to Azure Container Service Tools documentation!
=======================================================

Installation
------------

The ACS CLI is a Python application, as such you should be able to run
it on any platform that has Python 3 installed. Alternatively you can
use it via a Docker container. See the appropriate section for your
preference below. Once you have installed the CLI code there are a few
configuration steps you need to take, see the next section for
details.

Python
======

NOTE: at the time of writing we recommend you use one of the other two
methods that use the source code version of the ACS CLI as we have yet
to make a stable release of the Python packages. However, if you want
to try this method we look forward to you feedback via the 
`GitHub repository`_.

Install the `Azure CLI`_.

Install Python 3.

::

  pip install cli

.. _Azure CLI: https://azure.microsoft.com/en-us/documentation/articles/xplat-cli-install/

Now proceed to the 'Preparation' secion.

Docker
======

Clone the source from the `GitHub repository`_.

If you know Docker already this is the easiest way to run the
ACS CLI. The supplied Dockerfile installs all the necessary
compontents for using the CLI. First build the acs container::

  docker build -t acs .

Then run it with the following command::

  ./scripts/run-docker.sh

This command will first look to see if you have an existing container
available and connect to it if you do. If there is no existing
container then a new one is started which maps the current directory
into the container. Thus you can perform actions such as the
preparation steps below and have them persist over time.

Now proceed to the 'Preparation' secion.

Python (from source)
====================

Clone the source from the `GitHub repository`_.

See the README.md file in the root of the project directory for
instructions on running from source.


Preparation
-----------

Create a `service principle`_ that allows the applciation to manage
your subscription.

.. _Service Principle: http://rgardler.github.io/2016/02/10/create_keys_for_an_application_to_manage_azure

Cluster Configuration
=====================

Create a config.ini by copying config.ini.tmpl and editing it accoringly.


Azure Login
===========

Login to Azure with the azure cli and ensure it is operating in ARM
mode by executing the following commands::

  azure login
  azure config mode arm

Create a new Docker container
=============================

If you are using the Docker container you might want to commit these
changes to ensure that you don't need to do these steps every time you
start the container. To do this `exit` the container and run the
following commands::

  docker commit acs acs

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

.. _GitHub repository: https://github.com/rgardler/acs-cli
