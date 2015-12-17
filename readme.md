A set of convenience scripts for creating and testing ACS
clusters. These scripts can also be helpful in working out how to use
the REST API interfaces for managing applicaitons on an ACS cluster.

# Pre-requisites

  * Azure CLI installed and configured to access the test subscription
    * install Node and NPM
    * `sudo npm install azure-cli -g'
  * Install jq
    * apt-get install jq
  * Install Python
    * apt-get install python
  * Whitelisted for ACS preview

# Preparation

Create a config.ini by copying config.ini.tmpl and editing accoringly.

You will need to edit (at least) the value of `dnsPrefix` as this needs
to be world unique.

# Create or update a cluster

The `deploy` command will create or update a deployment. 

```
$ ./deploy --help
Usage: deploy [options]

Options:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config_file=CONFIG_FILE
                        Define the configuration file to use.
```

## Create

In order to create a new cluster ensure that the `dns_prefix` in
CONFIG_FILE  does not already exist.

## Update

In order to update a new cluster you will run the deployment using a
`dns_prefix` in CONFIG_FILE that already exists. The cluster will be
modified to match any updated parameters. For example, you can
increase the agent count.

# Delete a cluster

`delete` will delete the cluster and all associated resource.

```
$ ./delete --help
Usage: delete [options]

Options:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config_file=CONFIG_FILE
                        define the configuration file to use. Default is
                        'cluster.ini'
```

# Running Example Framework Scripts

There two scripts that provide various examples of using ACS.
`mesos` and `swarm`. These are primarily useful in testing a
cluster once it has been created. They are not intended to be adapted
for real-life use. However, they may be useful in learning the API for
each framework.

## Mesos Examples

The `mesos` script uses `mesos_cluster.ini` to define the cluser to
use. This cluster must first be created using:

```
deploy -c mesos_cluster.ini
```

Once created you can run the mesos tests with `./mesos`. This will
perform the following actions:

  * Lists the apps currently managed by Marathon
  * Deploy a simple 2 container application using Marathon
  * Verify the application is running correctly
  * Delete the application

### Examples to add

  * Deploy a script on Chronos that runs a container when resources are available
  * Rolling upgrades of an application

## Swarm Examples

The `swarm` script uses `swarm_cluster.ini` to define the cluser to
use. This cluster must first be created using:

```
deploy -c swarm_cluster.ini
```

Once created you can run the mesos tests with `./mesos`. This will
perform the following actions:

  * Lists the containers currently deployed
  * Deploy a two container application using Docker Compose
  * List the containers currently running

### Examples to add

  * Verify the application is running
  * Remove the application using Docker Compose
  * Scale the application using Docker Compose