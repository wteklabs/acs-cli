A set of convenience scripts for creating and testing ACS clusters.

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

We strongly recommend you edit the value of `dns_prefix` as this needs
to be world unique.

# Create or update a cluster

The `deploy` command will start a new deployment. If there is no
current resource group with the name provided in `dns_prefix` in
`config.ini` then a new resource group will be created. If the
resource group already exists then the existing group will be updated.

# Delete a cluster

`delete` will delete the cluster and all associated resource.