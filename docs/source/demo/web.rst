How to Create a Web Server in Azure Container Service
=====================================================

In this tuturial we will show how to use the CLI to create a simple,
load balanced, static web server using the Azure Container
Service CLI

If you simply want to show a load balanced web application working
then you can do everything you need, including deploying an instance
of Azure Container Service, using a single command::

  acs demo lbweb

If you want to demonstrate the steps involved then this command can be
expanded out to individual steps, as decribed below.
  
ACS powered by DC/OS
--------------------

First we need to create our cluster and open the tunnel::

  acs login
  acs service create
  acs service connect

Install the DC/OS command line::

  acs dcos install
  . /src/bin/env-setup
  
Next we will deploy our load balancer::

  dcos package install marathon-lb
  
Next we will deploy our web server using the demo marathon
configuration file provided by the CLI::

  acs app deploy --app-config=config/demo/web/simple-web.json

Note that the previous command simply delegates to the DC/OS cli after
replacing the `$AGENT_FQDN` token in the `simple-web` JSON file. This
makes it possible for a single configuration file to be used in
multiple different ACS clusters. However, you may prefer to manually
create the JSON file and call the DC/OS CLI directly (or use the API
directly). To do this use the following command::

  dcos marathon app add my-marathon.json
