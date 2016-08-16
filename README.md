This project provides a convenience CLI for creating, testing and
working with ACS clusters. It's a work in progress and we welcome
contributions via the [project page](https://github.com/rgardler/acs-cli).
 
# Using as a Docker Container

Assuming you have Docker installed the application will run "out of the
box" with the following command:

```
docker run -it rgardler/acs
```

You may also choose to use the latest developer version (which is the default 
branch in github). This versoin will likely have features and fixes that are 
still being tested. Simply use the ':dev' tag:

```
docker run -it rgardler/acs:dev
```

Although not required, it is preferable to mount your ssh and acs
configuration files into the running container. This way you can use
the same files across multiple versions of the cli container. To do
this use the following mounts:

```
docker run -it -v ~/.ssh:/root/.ssh -v ~/.acs:/root/.acs rgardler/acs
```

NOTE 1: the first time you run this you may need to create the `~/.ssh`
and `~/.acs` directories.

NOTE 2: we provide a
[convenience script](https://github.com/rgardler/acs-cli/blob/master/scripts/run-docker.sh) for doing this (and more, see below).

NOTE 3: If you want to work with the latest development version (may
have more features, but may also have more bugs) replace
`rgardler/acs` with `rgardler/acs:dev` in the above commands.

At this point you are ready to start using the CLI.

NOTE: the run-docker.sh script linked above will always attempt to
restart a previously run container. This has the advantage of
maintaining your Azure login credentials.

# Usage

The CLI includes some basic help guidance:

``` bash
acs --help
```

To get help for a specific command use `acs COMMAND --help`, for example:

``` bash
acs service --help
```

For more information see the
[documentation](http://rgardler.github.io/acs-cli), sources for which
are located in the `docs/source` folder of our
[GitHub project](http://www.github.com/rgardler/acs-cli).

## Create a Cluster

Since the first thing most users will want to do is create a cluster
we are documenting this command here. Please see `acs --help` for a
list of all available commands.

``` bash
acs service create
```

Unless otherwise specified the cluster configuration is defined in
`~/.acs/default.ini` within the container. If you mapped a local
directory to this location then it will be persisted on your
client. If this file does not exists you will be asked to answer some
questions about your desired configuration and the file will be
created for you.

You can override the location of the configuration file with the
option `--config-file=PATH_TO_FILE`, if the file exists it will be
used, if not you will be asked the same questions and the file will be
created.

## Connecting to your cluster

It is necessary to open an SSH tunnel to you cluster. By default the
acs cli will use the keys in `~/.ssh/id_rsa` (this can be configured
in the `ini` file in `~/.acs/`. If the identified keys don't exist
when you run the `acs service create` command they will be created for
you.

To easily create a tunnel to your cluster run:

``` bash
acs service connect
```

Take a note of the pid file this command outputs as you may want to kill this tunnel at a later time with:

``` bash
kill $PID
```

## Working with DCOS

If your cluster is using DC/OS as the orchestrator and you created it
using this set of tools then the DC/OS CLI will have been installed
for you when you created the cluster. If, however, you deployed the
cluster using a different method you can install the DC/OS cli with
the following commands.

``` bash
acs service install_dcos_cli
. /src/bin/env-setup
```

Once installed you can run DCOS command directly with `dcos COMMAND`
(you must first have connected to the cluster with `acs service
connect`).

# Development

Contributions (bug reports, feature requests, docs, patches etc.) are
welcome via the
[project page](https://hub.docker.com/r/rgardler/acs/).

The easiest way to get started is to develop using the Docker
container, however, the application is a Python3 application can can
be run anywhere you can find Python 3. First you need to clone the dev
branch of the code:

``` bash
git clone https://github.com/rgardler/acs-cli/tree/dev acs-cli

```

Once you have the source code, you can build a development container
with:

``` bash
./scripts/build-docker.sh
```

To run your container with local files mapped into it:

``` bash
./scripts/dev-docker.sh
```

Now you can edit the files using your favorite editor and test the
application from within the container. Note that when you have made
changes to your source files you should run the following in your
container:

``` bash
python setup.py install
```

## Development without Docker

If you would prefer to work outside of a container then consult the
Dockerfile in the project root for details of how to set up your
development environment.

## Testing

Run tests using [py.test:](http://pytest.org/latest) and
[coverage](https://pypi.python.org/pypi/pytest-cov):

``` bash
sudo pip install -e .[test]
python setup.py test 
```

Note, by default this does not run the slow tests (like creating the
cluster and installing features. You must therefore first have run the
full suite of tests at least once. You can do this with:

``` bash
py.test --runslow 
```

## Adding a new top level command

To add a top level command representing a new feature follow the
these steps (in this example the new command is called `Foo`:

  * Add the command `foo` and its description to the "Commands" section of the docstring for acs/cli.py
  * Copy `acs/commands/command.tmpl` to `acs/commands/foo.py`
    * Add the subcommands and options to the docstring of the foo.py file
    * Implement each command in a method using the same name as the command
  * Add foo.py import to `acs/commands/__init__.py`
  * Add instantiation of foo.py to tests/conftest.py
  * Copy `tests/command/test_command.tmpl` to `test/command/test_foo.py`
    * Implement the tests
  * Run the tests with `python setup.py test` and iterate as necessary
  * Install the package with `python setup.py install`
  * Add the command to the documentation in docs/*
  
## Adding a new subcommand

Subcommands are applied to commands, to add a subcommand do the following:

  * Add the subcommand to the docstring of the relevant command class (e.g. foo.bar)
  * Add a method with the same name as the subcommand
  * Add a test
  * Run the tests with `python setup.py test` and iterate as necessary
  * Install the package with `python setup.py install`
  
## Releasing

This section describes how to create a release of the acs-cli.

### Verify the code is ready for release

Ensure all local edits have been pushed to the dev branch:

``` bash
git status
[git add <as necessary>]
git push
```

Ensure we have all the latest changes in the dev branch:

``` bash
git checkout dev
git pull origin master
git merge master
```

Build the container.

``` bash
./scripts/build-docker.sh
```

Ensure all tests pass:

``` bash
docker run -it acs
python setup.py test
exit
```

If all tests pass then merge dev into master:

``` bash
git checkout master
git merge dev
git push
```

Create a tag in git:

``` bash
git tag x.y.z
git push --tags
```

There is no need to manual build and push the new Docker container as
this will be done by Docker Hub.

Update the version numbers in `acs/__init__.py`:

``` python
__version__ - 'x.y.z'
```

Commit to dev in order to start the next development cycle:

``` bash
git checkout dev
git add as/__init__.py
git push
```


### Updating Documentation

To build and publish the documentsation you need Sphinx installed:

``` bash
sudo pip install -U Sphinx
```

Then you can build and deploy the docs with:

``` bash
cd docs
make gh-pages
cd ..
```

