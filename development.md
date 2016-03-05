In this document we'll try to outline how to develop the scripts in
this project. 

Please note that this is an open source project and it has been
started by an ex-Java developer trying his hand at Python. What this
means is that it almost certainly doesn't follow Python best practices
and therefore, if you are a Python developer, we welcome improvments
to the codestyle and structure as well as new features. All we ask is
that you keep the PRs focussed. That is codestyle improvements should
not be mixed with nrew features wherever possible.

If you are looking for ways to contribute to this code we recommend
searching for
[TODO](https://github.com/rgardler/acs-scripts/search?utf8=%E2%9C%93&q=TODO)
or
[FIXME](https://github.com/rgardler/acs-scripts/search?utf8=%E2%9C%93&q=FIXME)
labels in the code itself. Items labelled TODO are things that need to
be done to improve functionality, things labelled FIXME are
refactoring tasks that will improve the code but not affect
functionality.

# Adding new features to an ACS cluster

Using the `addFeature` command we can add new features, such as
monitoring solutions or volume drivers to our cluster. In this section
we describe how to add such a feature to the scripts.

## Short Version of Adding a Feature

In this example we will add a feature "foo":

  1. Edit acs_utils.py and find the `addFeature` method.
  2. Locate the `for feature in features` loop
  3. Add an entry into this loop for processing for when `feature == "foo"`
  4. Add a call to a method called `addFoo()`
  5. Write the method `addFoo()` (see below for some hints)

FIXME: we should separate feature code out from the acs_utils.py
code. This means we should really provide separte modules or classes
for each feature.

### Writing the Code to Install Your Feature

In most cases features are likely to need to run commands on the
agents. to do this you need to build the command and then pass it to
the management nodes for execution on the agents (the agents are not
publicly accessible). We have provided a set of helper methods in
`acs_utils.py` to enable this. These are discussed in the next
section, but first let's look at some code tho install feature 'foo'.

Feature Foo is just an example, it doesn't actually do anything
useful, but it serves as a good example. We will create a script and
run it on each of the agents. For this document the script will simply
touch a file on the agents, for your feature the script is where you
do the work to install and configure the necessary software. 

The example below is not exhaustive, if you need further assistance
raise an [issue](https://github.com/rgardler/acs-scripts/issues) and
ask for help.

```
self.configureSSH()

agents = self.getAgentHostNames()
for agent in agents:
  scriptname = "fooScript.sh"
  self.log.debug("Installing foo on: " + host)

  # Write the script we want to execute
  f = open(scriptname, w)
  f.write("touch fooVisited" + agent + ".txt\n")
  f.close

  # Execute the script on the agent
  url = self.getManagementEndpoint()
  conn = "scp -P 2200 -o StrictHostKeyChecking=no"
  remotefile = self.config.get('ACS', 'username') + '@' + url + ":~/" + scriptname
  cmd = conn + " " + sshCommand = "chmod 755 ~/installOMS.sh"
  self.executeOnAgent(sshCommand, host)

  sshCommand = "sudo ./" + scriptname
  self.executeOnAgent(sshCommand, agent)

```

FIXME: we should probably write a helper method with the signature
`executeOnAgent(scriptname, agentname)` to replace the section "#
Execute a script on the agent"

