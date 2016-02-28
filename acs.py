#!/usr/bin/python

from acs.acs_utils import *
from acs.test.MesosTest import *
from acs.test.SwarmTest import *

import optparse
import sys
         
def main():
    """ACS command line tool"""

    usage = "usage: %prog [options] command\n\n"
    usage = usage + "Commands:\n\n"
    usage = usage + "deploy: deploy a cluster\n\n"
    usage = usage + "delete: delete a cluster\n\n"
    usage = usage + "test [mesos|swarm]: test a mesos or swarm cluster\n\n"
    usage = usage + "addFeature FEATURES: add one or mroe features to a cluster\n"
    usage = usage + "\tFEATURES is a comma separated list of features to add.\n\n"
    usage = usage + "env: display some useful information about the ACS environment currently configured"

    p = optparse.OptionParser(usage=usage, version="%prog 0.1")
    p.add_option('--config_file', '-c', default="cluster.ini",
                 help="define the configuration file to use. Default is 'cluster.ini'")
    options, arguments = p.parse_args()
 
    acs = ACSUtils(options.config_file)
    log = ACSLog()

    cmd = arguments[0]
    log.debug("Command: " + str(cmd))

    if cmd == "delete":
        acs.deleteResourceGroup()
    elif cmd == "deploy":
        acs.createDeployment()
        acs.addFeatures()
        print(acs.getEnvironmentSettings)
    elif cmd == "scale":
        acs.scale(arguments[1])
    elif cmd == "test":
        mode = acs.getMode()
        if mode == "mesos":
            log.debug("Test Mesos mode")
            test = MesosTest(acs)
            test.test_all()
        elif mode == "swarm":
            log.debug("Test Swarm mode")
            test = SwarmTest(acs)
            test.testAll()
        else:
            log.error("Don't know how to test mode " + mode)
    elif cmd == "addFeature":
        featureList = arguments[1]
        log.debug("Features: " + featureList)
        acs.addFeatures(featureList)
    elif cmd == "env":
        print(json.dumps(acs.getEnvironmentSettings(), indent=4))
    elif cmd == "docker":
        # Deprecated
        acs.agentDockerCommand(arguments[1])
    else:
        log.error("Unkown command: " + cmd)

if __name__ == '__main__':
    main()
