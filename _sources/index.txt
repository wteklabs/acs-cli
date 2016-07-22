Welcome to Azure Container Service Tools documentation!
=======================================================

Installation
------------

The ACS CLI is a Python application, as such you should be able to run
it on any platform that has Python 3 installed. Alternatively you can
use it via a Docker container. You also have the choice of running
from or from a relase. If in doubt we recommend running from a
release.

See the appropriate section for your preference below. Once you have
installed the CLI code wkip ahead to the 'Preparation' section..

Docker (from release)
=====================

To run the latest version of the cli::
   docker run -it rgardler/acs

Now proceed to the 'Preparation' secion.
   
Docker (from source)
====================

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

Python (from release)
=====================

NOTE: at the time of writing we recommend you use one of the other two
methods that use the source code version of the ACS CLI as we have yet
to make a stable release of the Python packages. 

Install the `Azure CLI`_.

Install Python 3.

Install the cli with::

  pip install cli

.. _Azure CLI: https://azure.microsoft.com/en-us/documentation/articles/xplat-cli-install/

Now proceed to the 'Preparation' section.

Python (from source)
====================

Clone the source from the `GitHub repository`_.

See the README.md file in the root of the project directory for
instructions on running from source.


Preparation
-----------

REQUIRED: Azure Login
======================

Login to Azure with the azure cli and ensure it is operating in ARM
mode by executing the following commands::

  azure login
  azure config mode arm

OPTIONAL: Cluster Configuration
===============================

By default the cluster is defined in a config file
`/config/cluster.ini`. If you want to use a different config file use
the `--config-file=FILE` option.

If the specified file does not exist you will enter an interactive
mode in which you can define your cluster. Note, however, that there
are likely to be more options available in the INI file than in the
interactive command line interface.

To create a conmfiguration file you can start by copying
`config/cluster.ini.tmpl` and editing it accordingly, for example::

  cp /config/cluster.ini.tmpl /config/cluster.ini
  nano /config/cluster.ini

Basic Useage
------------

The basic structure of an acs command is::

  acs <command> <args>

By default the config file `/config/cluster.ini` will be used, if you
want to use a different config file use the `--config-file=FILE`
option.

To get help for the CLI use::

  acs --help

Working with ACS Service
------------------------

The `service` commands provide convenience methods for managing an
instance of the Azure Container Service. Run `acs service help` for
more details about the available commands. Some common once are
provided below.

To examine the current configuation of the cluster run::

  acs service show

To create a cluster::

  acs service create

Once you have created your service you will likely want to open a
connection to it::

  acs service openTunnel

Now you can run commands against you Azure Container Service using any
tooling compatible with your chose orchestrator, such as the Docker
CLI for the Docker Swarm version of ACS and the DC/OS cli for the
DC/OS version.

.. _GitHub repository: https://github.com/rgardler/acs-cli
