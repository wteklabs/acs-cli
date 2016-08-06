azure lb --help
===============

The Azure lb command is used for managing the load balancer on your
public agent pool. It is expected that in most cases the user will not
need to call this command directly, it will be used by other commands
that will require the creation of a new Load Balancer rule, such as
the deployment of a container.

acs lb
------
		
.. automodule:: acs.commands.lb


Examples
--------

To open a port 8888 using TCP all you need to do is::

  acs lb open --port=8888

This will create a new probe and associated rule in the public agent
load balancer. It will also create an inbound Network Security Group
Rule for the port in question.

