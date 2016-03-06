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
agents. To do this you need to build the command and then pass it to
the management nodes for execution on the agents (the agents are not
publicly accessible). Here we will look at how to add a feature called
Foo.

Feature Foo is just an example, it doesn't actually do anything
useful, but it serves as a good example. The feature simply touches a
couple of files on the agents. This demonstrates how to run a command
on agents. All you need to do to add your feature is run each command
required.

The example below is not exhaustive, if you need further assistance
raise an [issue](https://github.com/rgardler/acs-scripts/issues) and
ask for help.

```
agents = self.getAgentHostNames()
for agent in agents:
  self.log.debug("Installing foo on: " + host)

  cmd = "touch fooVisted" + host
  acs.executeOnAgent(cmd)

  cmd = "touch fooLeftAPresent"
  acs.executeOnAgent(cmd)
```

