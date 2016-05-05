from .ACSLogs import *

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
        self.log = ACSLog("AgentPool")
        defaults = {"orchestratorType": "Mesos"}
        self.config = config

    def getAccessToken(self):
        tenant_id = self.config.get('Subscription', 'tenant_id')
        app_id = self.config.get('Subscription', 'app_id')
        app_secret = self.config.get('Subscription', 'app_secret')
        return azurerm.get_access_token(tenant_id, app_id, app_secret)

    def getPools(self):
        """
        Get a list of all the agent pools in this resource group
        """
        subscription_id = self.config.get('Subscription', 'subscription_id')
        rg_name = self.config.get('Group', 'name')
        access_token = self.getAccessToken()

        # TODO: This assumes only a single VMSS in the resource group, this will not always be the
        # case and will never be the case if when there are multiple Agent Pools
        vmss_list = azurerm.list_vm_scale_sets(access_token, subscription_id, rg_name)['value']
        self.log.debug("List of VMSS: " + json.dumps(vmss_list, indent=True))
        return vmss_list

    def getNICs(self):
        """
        Get a list of NICs attached to an agent pool
        """
        vmss_list = self.getPools()
        vmss_name = vmss_list[0]['name']
        self.log.debug("Looking up VMs in VMSS called " + vmss_name + " (if this is wrong maybe it is because AgentPool.py currently only supports a single VMSS)")

        subscription_id = self.config.get('Subscription', 'subscription_id')
        rg_name = self.config.get('Group', 'name')
        access_token = self.getAccessToken()
        nics = azurerm.get_vmss_nics(access_token, subscription_id, rg_name, vmss_name)
        self.log.debug("List of VMSS NICs: " + json.dumps(nics, indent=True))
        return nics["value"]

    def getAgents(self):
        """
        Get a list of all agents in the Pool.
        """
        vmss_list = self.getPools()
        vmss_name = vmss_list[0]['name']
        self.log.debug("Looking up VMs in VMSS called " + vmss_name + " (if this is wrong maybe it is because AgentPool.py currently only supports a single VMSS)")

        subscription_id = self.config.get('Subscription', 'subscription_id')
        rg_name = self.config.get('Group', 'name')
        access_token = self.getAccessToken()
        vms = azurerm.list_vmss_vms(access_token, subscription_id, rgname, vmss_name)
        return vms['value']

    def scale(self, capacity):
        """
        Scale the agent count up or down to the supplied number.
        """
        tenant_id = self.config.get('Subscription', 'tenant_id')
        app_id = self.config.get('Subscription', 'app_id')
        app_secret = self.config.get('Subscription', 'app_secret')
        subscription_id = self.config.get('Subscription', 'subscription_id')
        rg_name = self.config.get('Group', 'name')
        access_token = azurerm.get_access_token(tenant_id, app_id, app_secret)

        # TODO: This assumes only a single VMSS in the resource group, this will not always be the
        # case and will never be the case if when there are multiple Agent Pools
        vmsslist = azurerm.list_vm_scale_sets(access_token, subscription_id, rg_name)['value']
        # self.log.debug("List of VMSS: " + json.dumps(vmsslist, indent=True))
        vmss_name = vmsslist[0]['name']
        self.log.debug("Scaling " + vmss_name + " to " + capacity + " VMs (if this is the wrong VMSS it is because AgentPool.py currently only supports a single VMSS)")

        size = self.config.get("ACS", "AgentVMSize")
        tier = self.config.get("ACS", "AgentVMSize").split('_')[0]

        scale_result = azurerm.scale_vmss(access_token, subscription_id, rg_name, vmss_name, size, tier, capacity)
        self.log.warning("We scaled the cluster, but note that any of the features added will not be present on new machines.")

