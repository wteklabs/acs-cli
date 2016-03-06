from acs_utils import *

import os
import paramiko
from paramiko import SSHClient
from scp import SCPClient
import subprocess

def addTo(acs):
    """
    Add the AFS feature to the ACS cluster provided.
    """
    driver_version = "0.2"
    mount = acs.config.get("Storage", "mount")

    url = acs.getManagementEndpoint()
    package = "cifs-utils"
    
    scriptpath = "/tmp/afs_scripts/"
    if os.path.isdir(scriptpath):
        pass
    else:
        os.mkdir(scriptpath)

    scriptname = "installAFS.sh"
    f = open(scriptpath + scriptname, "w")
    f.write("wget https://github.com/Azure/azurefile-dockervolumedriver/releases/download/" + driver_version + "/azurefile-dockervolumedriver\n")
    f.write("cp azurefile-dockervolumedriver /usr/bin/azurefile-dockervolumedriver\n")
    f.write("chmod +x /usr/bin/azurefile-dockervolumedriver\n")
    f.write("wget https://raw.githubusercontent.com/Azure/azurefile-dockervolumedriver/" + driver_version + "/contrib/init/upstart/azurefile-dockervolumedriver.conf\n")
    f.write("cp azurefile-dockervolumedriver.conf /etc/init/azurefile-dockervolumedriver\n")
    f.write("wget https://raw.githubusercontent.com/Azure/azurefile-dockervolumedriver/" + driver_version + "/contrib/init/upstart/azurefile-dockervolumedriver.default\n")
    f.write("sed -i 's/youraccount/" + acs.config.get("Storage", "name") + "/g' azurefile-dockervolumedriver.default\n")
    f.write("sed -i 's/yourkey/" + acs.getStorageAccountKey() + "/g' azurefile-dockervolumedriver.default\n")
    f.write("cp azurefile-dockervolumedriver.default /etc/default/azurefile-dockervolumedriver\n")
    f.write("initctl reload-configuration\n")
    f.write("initctl start azurefile-dockervolumedriver\n")
    f.close

    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(acs.getManagementEndpoint(), username = acs.config.get('ACS', "username"), port=2200)

    with SCPClient(ssh.get_transport()) as scp:
        scp.put(scriptpath + scriptname, scriptname)

#    url = acs.getManagementEndpoint()
#    conn = "scp -P 2200 -o StrictHostKeyChecking=no"
#    remotefile = acs.config.get('ACS', 'username') + '@' + url + ":~/" + scriptname
#    cmd = conn + " " + scriptpath + scriptname + " " + remotefile
#    acs.log.debug("SCP command to copy install script to master: " + cmd)
#    out = subprocess.check_output(cmd, shell=True)

def hide():

    agents = acs.getAgentHostNames()
    for agent in agents:
        acs.log.debug("Installing AFS on: " + agent)

        conn = "scp -o StrictHostKeyChecking=no"
        remotefile = acs.config.get('ACS', 'username') + '@' + agent + ":~/" + scriptname
        cmd = conn + " " + scriptname + " " + remotefile
        acs.log.debug("SCP command to copy install script to agent: " + cmd)
        acs.executeOnMaster(cmd)

        sshCommand = "chmod +x ~/" + scriptname
        acs.executeOnAgent(sshCommand, agent)

        sshCommand = "sudo ./" + scriptname
        acs.executeOnAgent(sshCommand, agent)

        cmd = "mkdir -p " + mount
        acs.executeOnAgent(cmd, agent)
        
        urn = acs.getShareEndpoint().replace("https:", "") + acs.config.get("Storage", "shareName")
        username = acs.config.get("Storage", "name")
        password = acs.getStorageAccountKey()
        cmd = "sudo mount -t cifs " + urn + " " + mount + " -o uid=1000,gid=1000,vers=2.1,username=" + username + ",password=" + password
        acs.executeOnAgent(cmd, agent)


