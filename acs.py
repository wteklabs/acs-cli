#!/usr/bin/python

from acs.acs_utils import *
from acs.test.MesosTest import *
from acs.test.SwarmTest import *

import optparse
import sys
         
def main():
    """ACS command line tool"""

    usage = "usage: %prog [options] command"
    p = optparse.OptionParser(usage=usage)
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
    elif cmd == "test":
        mode = acs.getMode()
        if mode == "mesos":
            log.debug("Test Mesos mode")
            test = MesosTest(acs)
            test.testAll()
        elif mode == "swarm":
            log.debug("Test Swarm mode")
            test = SwarmTest(acs)
            test.testAll()
        else:
            log.error("Don't know how to test mode " + mode)
    elif cmd == "addFeature":
        featureList = arguments[1]
        log.debug("Features: " + featureList)
        addFeatures(feature)
    else:
        log.error("Unkown command: " + cmd)

if __name__ == '__main__':
    main()
