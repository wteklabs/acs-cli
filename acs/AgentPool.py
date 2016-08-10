from .ACSLogs import *

import json
import subprocess

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

    def getPools(self):
        """
        Get a list of all the agent pools in this resource group
        """
        rg_name = self.config.get('Group', 'name')
        cmd = "azure vmss list " + rg_name + " --json"
        vmss_list = json.loads(subprocess.check_output(cmd, shell=True).decode("utf-8"))

        self.log.debug("List of VMSS: " + json.dumps(vmss_list, indent=True))
        return vmss_list

    def getNICs(self):
        """
        Get a list of NICs attached to an agent pool
        """
        rg_name = self.config.get('Group', 'name')
        nics = []
        cmd = "azure network nic list " + rg_name + " --json"
        nic_list = json.loads(subprocess.check_output(cmd, shell=True).decode("utf-8"))
            
        for nic in nic_list:
            if "agent" in nic["name"]:
                self.log.debug("Adding NIC to list of Agent NICs:\n" + json.dumps(nic, indent=True))
                nics.append(nic)
            
        return nics

    def getAgents(self):
        """
        Get a list of all agents in the Pool.
        """
        rg_name = self.config.get('Group', 'name')
        vms = []
        vmss_list = self.getPools()
        for vmss in vmss_list:
            vmss_name = vmss['name']
            self.log.debug("Looking up VMs in VMSS called " + vmss_name)

            cmd = "azure vmssvm list " + rg_name + " " + vmss_name + " --json"
            vmssvms = json.loads(subprocess.check_output(cmd, shell=True).decode("utf-8"))
            for vm in vmssvms:
                vms.append(vm)

        return vms

    def getAgentCount(self):
        """ get a count of the agents in the public pool """
        cmd = "azure vmss list " + self.config.get("Group", "name") + " --json"
        vmss_list = json.loads(subprocess.check_output(cmd, shell=True).decode("utf-8"))
        count = 0
        for vmss in vmss_list:
            count = count + int(vmss["sku"]["capacity"])
        return count
