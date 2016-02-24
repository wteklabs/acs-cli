from ACSLogs import *

import azurerm
import ConfigParser
import json

class AgentPool:
    """

    An Agent Pool is a collection of agents available within an ACS
    cluster. Each pool is implemented as a Virtual Machine Scale Set
    (VMSS).

    """
    def __init__(self, config):
        self.log = ACSLog()
        defaults = {"orchestratorType": "Mesos"}
        self.config = config

    def getAgents(self):
        """
        Get a list of all agents in the Pool.
        """
        tenant_id = self.config.get('Subscription', 'tenant_id')
        app_id = self.config.get('Subscription', 'app_id')
        app_secret = self.config.get('Subscription', 'app_secret')
        subscription_id = self.config.get('Subscription', 'subscription_id')
        rgname = self.config.get('Group', 'name')
        access_token = azurerm.get_access_token(tenant_id, app_id, app_secret)

        # TODO: This assumes only a single VMSS in the resource group, this will not always be the
        # case and will never be the case if when there are multiple Agent Pools
        vmsslist = azurerm.list_vm_scale_sets(access_token, subscription_id, rgname)['value']
        # self.log.debug("List of VMSS: " + json.dumps(vmsslist, indent=True))
        vmssname = vmsslist[0]['name']
        self.log.debug("Looking up VMs in VMSS called " + vmssname + " (if this is wrong maybe it is because AgentPool.py currently only supports a single VMSS)")

        vms = azurerm.list_vmss_vms(access_token, subscription_id, rgname, vmssname)
        return vms['value']


