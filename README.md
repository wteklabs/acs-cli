This project provides a convenience CLI for creating, testing and
working with ACS clusters. It's a work in progress and we weclome
contributions via the
[project page](https://hub.docker.com/r/rgardler/acs/).
 
# Using as a Docker Container

Assuming you have Docker installed the application will run "out of the
box" with the following command.

```
docker run -it rgardler/acs
```

Although not required, it is preferable to mount your ssh and acs
configuration files into the running container. This way you can use
the same files across multiple versions of the cli container. To do
this use the following mounts:

```
docker run -it -v ~/.ssh:/root/.ssh -v ~/.acs:/root/.acs rgardler/acs
```

NOTE: the first time you run this you may need to create the `~/.ssh`
and `~/.acs` directories.

NOTE: we provide a
[convenience script](https://github.com/rgardler/acs-cli/blob/master/scripts/run-docker.sh)
for doing this (and more, see below).

Once you have run one of the commands above you should log into your
Azure subscription:

```
azure config mode arm
azure login
```

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

# Development

Contributios to this CLI are welcome, via the
[project page](https://hub.docker.com/r/rgardler/acs/).

The easiest way to get started is to develop using the Docker
container, however, the application is a Python3 application can can
be run anywhere you can find Python 3.

The easiet way to get started with development is to use a Docker
container, but it is not necessary to do so. If you want to use the
non-Docker environment please configure your environment as described
in the next section, otherwise simply start a Docker Python container
and mount this code into it with the following command:

Note that we provide a convenience script in `scripts/run-docker.sh'
which will run the container and mount the source code directory.

Now you can edit the files using your favorite editor and test the
application from within the container. Note that when you have made
changes to your source files you should run the following in your
container:

``` bash
python setup.py install
```

If you would prefer to work outside of a contaienr then consult the
Dockerfile in the project root for details of how to set up your
development environment.

If you would prefer to work outside of a contaienr then consult the
Dockerfile in the project root for details of how to set up your
development environment.

## Development without Docker

To setup a separate development environment (without Docker) you need
the following setup.

### Python 3.5 and Pip

``` bash
apt-get install python3.5
wget https://bootstrap.pypa.io/get-pip.py
python3.5 get-pip.py
```

### Azure CLI

``` bash
sudo apt-get update
sudo curl -sL https://deb.nodesource.com/setup_4.x | sudo bash -
sudo apt-get install -qqy nodejs
sudo apt-get install -qqy build-essential
sudo npm install azure-cli -g 
```

### Docker

If you want to be able to build the Docker container then you will
also want to install Docker:

``` bash
sudo curl -sSL https://get.docker.com/ | sudo sh
```

And Docker Compose:

``` bash
sudo curl -L https://github.com/docker/compose/releases/download/1.7.1/docker-compose-`uname -s`-`uname -m` > docker-compose; sudo mv docker-compose /usr/local/bin/docker-compose; sudo chmod +x /usr/local/bin/docker-compose
```

## Testing

Run tests using [py.test:](http://pytest.org/latest) and
[coverage](https://pypi.python.org/pypi/pytest-cov):

``` bash
python setup.py test 
sudo pip install -e .[test]
```

Note, by default this does not run the slow tests (like creating the
cluster and installing features. You must therefore first have run the
full suite of tests at least once. You can do this with:

``` py.test --runslow ```

## Adding a new top level command

To add a top level command representing a new feature follow the
these steps (in this example the new command is called `Foo`:

  * Add the command `foo` and its description to the "Commands" section of the docstring for acs/cli.py
  * Copy `acs/commands/command.tmpl` to `acs/commands/foo.py`
    * Add the subcommands and options to the docstring of the foo.py file
    * Implement each command in a method using the same name as the command
  * Add foo.py import to `acs/commands/__init__.py`
  * Add instantiation of foo.py to conftest.py
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

## Docker Image

Ensure all tests pass (see above).

``` bash
docker build -t rgardler/acs .
docker push rgardler/acs
```

## Python Package

Ensure all tests pass (see above).

Cut a release and publish to the [Python Package
Index](https://pypi.python.org/pypi) install 
[twine](http://pypi.python.org/pypi/twine. and then run:

```
python3.5 setup.py sdist bdist_wheel
twine upload dist/*
```

This will build both a surce tarball and a wheel build, which will run
on all platforms.

Now create a tag in git:

```
git tag x.y.z
git push --tags
```

Finally update the version numbers in `acs/__init__.py`:

```
__version__ - 'x.y.z'
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

