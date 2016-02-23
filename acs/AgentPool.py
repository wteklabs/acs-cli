import azurerm
import ConfigParser

class AgentPool:
    """

    An Agent Pool is a collection of agents available within an ACS
    cluster. Each pool is implemented as a Virtual Machine Scale Set
    (VMSS).

    """
    def __init__(self, configfile = "cluster.ini"):
        defaults = {"orchestratorType": "Mesos"}
        config = ConfigParser.ConfigParser(defaults)
        config.read(configfile)
        config.set('Group', 'name', config.get('ACS', 'dnsPrefix'))
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
        vmssname = 'mesos-agent-52E91123-vmss' # FIXME: need to look up vmssname

        access_token = azurerm.get_access_token(tenant_id, app_id, app_secret)

        print('Virtual machines...')
        vms = azurerm.list_vmss_vms(access_token, subscription_id, rgname, vmssname)
        return vms['value']


