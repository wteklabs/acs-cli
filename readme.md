A set of convenience scripts for creating and testing ACS
clusters. These scripts can also be helpful in working out how to use
the REST API interfaces for managing applicaitons on an ACS cluster.

# Pre-requisites

  * Azure CLI installed and configured to access the test subscription
    * install Node and NPM
    * `sudo npm install azure-cli -g'
  * Install jq
    * `apt-get install jq`
  * Install Python
    * `apt-get install python`
  * Install required Python libraries
    * `pip install -r requirements.txt`
  * Whitelisted for ACS preview

# Preparation

Create a config.ini by copying config.ini.tmpl and editing accoringly.

Create a [service principle for the
application](http://rgardler.github.io/2016/02/10/create_keys_for_an_application_to_manage_azure)
and add the details to your config.ini.

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

## deploy: Create or update a cluster

The `deploy` command will create or update a deployment. 

```bash
python acs.py deploy [-c CONFIG_FILE]
```

### Create

In order to create a new cluster ensure that the `dns_prefix` in
CONFIG_FILE does not already exist.

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

```bash
python acs.py addFeature afs
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