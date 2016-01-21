#!/usr/bin/python

from acs.acs_utils import ACSLog
import requests
import sys
import time

class MesosTest:
    def __init__(self, acs):
        self.acs = acs
        self.log = ACSLog()

    def testAll(self):
        """Run all tests against the supplied ACS"""

        response = self.acs.openMesosTunnel()
        self.log.info(response);

        self.log.info("Start: Check current apps")
        self.log.debug(self.acs.marathonCommand('apps'))
        self.log.info("End")
        
        self.log.info("Deploy a two container app")
        with open ('marathon-app.json', "r") as marathonfile:
            data=marathonfile.read().replace('\n', '').replace("\"", "\\\"")

        self.log.debug(self.acs.marathonCommand('groups', 'POST', data))
        self.log.debug("End")

        self.log.debug("Check the application is running")
        for i in range (0,10):
            self.log.debug("Attempt to access service " + str(i) + " of 10")
            try:
                r = requests.get("http://" + self.acs.getAgentsFQDN(config))
                if r.status_code == 200:
                    self.log.debug("Got a 200 response from the application")
                    break
            except:
                self.log.debug("Attempt failed, sleeping for 5 seconds")
                time.sleep (5)

        if i >= 9: 
            self.log.error("TESTING: Application never responded")
        self.log.info("End")

        self.log.info("Remove the app")
        self.acs.marathonCommand('groups/azure', 'DELETE')
        self.log.info("End")


