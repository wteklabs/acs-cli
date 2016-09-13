"""
Storage account management for Azure Container Service.
"""
from .AcsUtils import AcsUtils
import json
import subprocess

class Storage:
    def __init__(self, config):
        self.config = config
        self.utils = AcsUtils()
        self.logger = self.utils.getLogger("Storage")

    def create(self, name, account_sku = "LRS"):
        """
        Create a storage account for this cluster.

        name          - name of the storage account, must be world unique
        account_sku  - storage account SKU (LRS or GRS, DEFAULT to LRS)
        """
        self.logger.debug("Creating Storage Account with name '" + name + "'")

        command = "azure storage account create"
        command = command + " --kind Storage"
        command = command + " --sku-name " + account_sku
        command = command + " --resource-group " + self.config.get('Group', 'name')
        command = command + " --location " + self.config.get('Group', 'region')
        command = command + " " + name
    
        output, errors = self.utils.shell_execute(command)
        if errors:
            self.logger.error("Problem creating storage account: \n" + errors)

        return self.getStorageAccountKey(name)

    def getStorageAccountKey(self, name):
        """Get the storage account key for the storage account in this
        cluster with the given name. 

        """
        command = "azure storage account keys list"
        command = command + " --resource-group " + self.config.get('Group', 'name')
        command = command + " " + name
        command = command + " --json"
        self.logger.debug("Command to get storage keys: " + command)

        output, errors = self.utils.shell_execute(command)
        if errors:
            self.logger.error("Unable to get storage account key: \n" + errors)
            raise RuntimeError(errors)
        else:
            keys = json.loads(output)
            
        return keys[0]['value']
