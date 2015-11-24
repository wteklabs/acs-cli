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

The `deploy` command will start a new deployment. If there is no
current resource group with the name provided in `dns_prefix` in
`config.ini` then a new resource group will be created. If the
resource group already exists then the existing group will be updated.

# Delete a cluster

`delete` will delete the cluster and all associated resource.

# Running Example Framework Scripts

There two scripts that container examples, `marathon` and
`swarm`. These are primarily useful in testing a cluster once it has
been created. They are not intended to be adapted for real-life
use. However, they may be useful in learning the API for each
framework.