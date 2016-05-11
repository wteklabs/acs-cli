NOTE: NOT FOR PRODUCTION USE

Please note these scripts are intended to allow experimentation with
Azure Container Service. They are not intended for production use.

A set of convenience scripts for creating and testing ACS
clusters. These scripts can also be helpful in working out how to use
the REST API interfaces for managing applicaitons on an ACS cluster.

# Usage

See the [documentation](http://rgardler.github.io/acs-cli).

# Development

## Pre-Rquisites

  * Python 3
	* `apt-get install python`
  * [PIP](https://pip.pypa.io/en/stable/installing/)
  * Azure CLI installed and configured to access the test subscription
    * install Node and NPM
    * `sudo npm install azure-cli -g`

## Preparing

To install all libraries and development dependencies:

```
sudo pip install -e .
sudo pip install -e .[test]
```

## Adding a command

To add a top level command representing a new feature follow the
these steps (in this example the new command is called `Foo`:

  * Add the command `foo` and its description to the "Commands" section of the docstring for acs/cli.py
  * Copy `acs/commands/command.tmpl` to `acs/commands/foo.py`
    * Add the subcommands and options to the docstring of the foo.py file
    * Implement each command in a method using the same name as the command
  * Add foo.py import to `acs/commands/__init__.py`
  * Copy `tests/command/test_command.tmpl` to `test/command/test_foo.py`
    * Implement the tests
  * Run the tests with `python setup.py test` and iterate as necessary
  * Install the package with `python setup.py install`
  
## Adding a subcommand

Subcommands are applied to commands, to add a subcommand do the following:

  * Add the subcommand to the docstring of the relevant command class (e.g. foo.bar)
  * Add a method with the same name as the subcommand
  * Add a test
  * Run the tests with `python setup.py test` and iterate as necessary
  * Install the package with `python setup.py install`
  
## Testing

Run tests using [py.test:](http://pytest.org/latest) and [coverage](https://pypi.python.org/pypi/pytest-cov):

```
python setup.py test
```

Note, by default this does not run the slow tests (like creating the
cluster and installing features. You must therefore first have run the full suite of tests at least once. You can do this with:

```
py.test --runslow
```

## Releasing

Cut a release and publish to the [Python Package
Index](https://pypi.python.org/pypi) install install
[twine](http://pypi.python.org/pypi/twine. and then run:

```
python setup.py sdist bdist_wheel
twine upload dist/*
```

This will build both a surce tarball and a wheel build, which will run
on all platforms.

### Updating Documentation

To build and pucblish the documentsation:

```
cd docs
make gh-pages
cd ..
```

---------------------------------------------- 

FIXME: Content below this line was current prior to the move to a
luggable architecture. Ensure it is all updated and moved to above
this line as appropriate.

# Pre-requisites

  * Azure CLI installed and configured to access the test subscription
    * install Node and NPM
    * `sudo npm install azure-cli -g`
  * Install jq
    * `apt-get install jq`
  * Install Python
    * `apt-get install python`
  * Install required Python libraries
    * `pip install -r requirements.txt`
  * Whitelisted for ACS preview

# Command Line

```
$ ./acs.py --help
Usage: acs.py [options] command

Options:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config_file=CONFIG_FILE
                        define the configuration file to use. Default is
                        'cluster.ini'
```

There are a number of accepted commands, as follows

### Update

In order to update a new cluster you will run the deployment using a
`dns_prefix` in CONFIG_FILE that already exists. The cluster will be
modified to match any updated parameters. For example, you can
increase the agent count.

## Execute Docker commands on the agents

You can execute arbitrary docker commands on each agent using the
`doocker` command. This is a pass through of the standard Docker
CLI.

It can be used, for example, to pull a docker container to all nodes
in a cluster. This is not a necessary step, Mesos will pull the
container image automatically for you, however pulling the container
ahead of time makes the first starup on each node faster.

```bash
python acs.py docker "pull CONTAINER_NAME"
```

## addFeature

Adds a feature to the ACS cluster. Possible features are described
below. Features can be added at deployment time by specifiying them in
a comma separated list in the cluster ini file.

```bash
./acs.py addFeature FEATURE_LIST
```

Where FEATURE_LIST is a comma separated list of features required.

### Azure File Service

Azure File Service is a storage driver that enables multiple Docker
containers to read and write to a shared folder. To add this feature
simply run:

```bash
python acs.py addFeature afs
```

This will create a Storage Account on Azure, crate a share and mount
that share on each of the agents in your cluster.

### Operations Management Suite (oms)

Add the
[OMS](https://blogs.technet.microsoft.com/momteam/2015/11/03/announcing-linux-docker-container-management-with-oms/)
monitoring solution to the cluster. You will first need to register
for the OMS service and then complete the OMS section of the
cluster.ini file. Finally, run the following command.

Visit http://mms.microsoft.com and sign up for a free OMS
account. Then click "Settings" and then "Connected Sources". You will
need to copy your Workspace ID and your Workspace Primary Key into
your config file. Finally, run the following command to install OMS on
each of your agents (please note that this command restarts the Docker
Engine and thus any containers on it will be stopped).

```bash
python acs.py addFeature oms
```


#### Known Issues

If an agent is added to the cluster it will not have the Azure File
Service feature added by default.

## delete: Delete a cluster

`delete` will delete the cluster and all associated resource.

```bash
python acs.py delete [-c CONFIG_FILE]
```

## test: Running Tests in Clusters

NOTE: for this command to work you must have opened an SSH Tunnel to
your cluster, or you must run the command from a VM inside the
clusters VNET.

`test` will deploy some test applications and ensure they are started
correctly on the cluster. The tests will be run against a cluster
defined in the cluster.ini file (or the file specified with -c).

```bash
python acs.py test [-c CONFIG_FILE]
```

This command performs various actions, such as deploying a
multi-container application and verifying it is working correctly. The
log outputs of these test scripts detail the commands being run and
can therefore be useful as a learning excercise, as well as testing
whether the cluster is correctly configured.