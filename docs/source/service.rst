acs service create
==================

The `service create` command will ask you for some details about your
cluster. If you already have a cluster created be careful to provide
the exact information for that cluster. Otherwise provide new values
and a new cluster will be created for you. If you don’t have an SSH
key in ~/.ssh then one will be created for you.

This command will create a configuration file in ~/.acs/default.ini,
you can edit this if you make a mistake connecting to an existing
cluster or if you want to use an ssh key other than `id_rsa`.
