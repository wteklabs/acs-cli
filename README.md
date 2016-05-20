NOTE: NOT FOR PRODUCTION USE

Please note these scripts are intended to allow experimentation with
Azure Container Service. They are not intended for production use.

A set of convenience scripts for creating and testing ACS
clusters. These scripts can also be helpful in working out how to use
the REST API interfaces for managing applicaitons on an ACS cluster.

# Installation

The easiest way to get started is to use our Docker container,
however, the application is a Python3 application can can be run
anywhere you can find Python 3.

## Using Docker

Assumin you have Docker installed the application will run "out of the
box" with the following command.

```
docker run -it azurecs/acs-cli
```

This will pull the container from Docker Hub and start it in an
interactive shell mode. Here you can start typing commands.

You might want to add some local configuration files into the
container, how and why you might do this is discussed below, but we
provide a convenience script in `scripts/run-docker.sh' which will do
this for you.

## Login to Azure

Before you can run any commands that use the Azure CLI you will need
to login using the follwing command:

```
azure config mode arm
azure login
```

Since this must be done every time you start the container you might
want to create a new image whenever you update the software. This will
prevent you needing to login each time. However, you will need a
private registry to store this container as it will have your SSH keys
and Azure login details stored within it. Docker Hub provides one
private registry per user, so that might be enough for you.

To create a Docker image with your login credentials run the following
commands:

```
docker commit CONTAINER REPOSITORY/acs
docker push
```

Where `CONTAINER`is the name of the container in which you ran the
`azure login` command and `REPOSITORY` is the name of your private
repository.

You may want to create a version of the CLI tools that include SSH
keys and configuration files for your clusters. See below for more
details on how to do this.

# Usage

The tool includes some basic help guidance:

```
acs --help
```

To get help for a specific command use `acs COMMAND --help`, for example:

```
acs service --help
```

FOr more information see the
[documentation](http://rgardler.github.io/acs-cli), sources for which
are located in the `docs/source` folder of our
[GitHub project](http://www.github.com/rgardler/acs-cli)

## Mounting configuration files and SSH keys

The ACS Cli uses configuration files to make it easier to build and
manaage clusters. The can be found in the `/config` directory of the
container. By mounting a volume when starting the container you can
inject configuration files at from the host. Alternatively you can
build your own container with your config files included.

To start the container with your own config directory mounted use:

```
docker run -it -v ./config:/config azurecs-cli
```

THe CLI will also use (and generate) SSH keys. These are stored in the
container in the `/root/.ssh` directory. You may want to mount your
own SSH directory into the container by adding `-v ~/.ssh:/root/.ssh`
to this command line:

```
docker run -it -v ./config:/config -v ~/.ssh:/root/.ssh azurecs-cli
```

# Development

The easiet way to get started with development is to use a Docker
container, but it is not necessary to do so. If you want to use the
non-Docker environment please configure your environment as described
in the next section, otherwise simply start a Docker Python container
and mount this code into it with the following command:

```
docker build -t acs .
docker run -it -v $(pwd):/src acs
```

## Development without Docker

To setup a separate development environment (without Docker) you need
the following setup:

  * Python 3
	* `apt-get install python`
  * [PIP](https://pip.pypa.io/en/stable/installing/)
  * Azure CLI installed and configured to access the test subscription
    * install Node and NPM
    * `sudo npm install azure-cli -g`

To install all libraries and development dependencies:

```
sudo pip install -e .
sudo pip install -e .[test]
```

## Adding a new top level command

To add a top level command representing a new feature follow the
these steps (in this example the new command is called `Foo`:

  * Add the command `foo` and its description to the "Commands" section of the docstring for acs/cli.py
  * Copy `acs/commands/command.tmpl` to `acs/commands/foo.py`
    * Add the subcommands and options to the docstring of the foo.py file
    * Implement each command in a method using the same name as the command
  * Add foo.py import to `acs/commands/__init__.py`
  * Copy `tests/command/test_command.tmpl` to `test/command/test_foo.py`
    * Implement the tests
  * Run the tests with `python setup.py test` and iterate as necessary
  * Install the package with `python setup.py install`
  
## Adding a new subcommand

Subcommands are applied to commands, to add a subcommand do the following:

  * Add the subcommand to the docstring of the relevant command class (e.g. foo.bar)
  * Add a method with the same name as the subcommand
  * Add a test
  * Run the tests with `python setup.py test` and iterate as necessary
  * Install the package with `python setup.py install`
  
## Testing

Run tests using [py.test:](http://pytest.org/latest) and [coverage](https://pypi.python.org/pypi/pytest-cov):

```
python setup.py test
```

Note, by default this does not run the slow tests (like creating the
cluster and installing features. You must therefore first have run the full suite of tests at least once. You can do this with:

```
py.test --runslow
```

## Releasing

Cut a release and publish to the [Python Package
Index](https://pypi.python.org/pypi) install 
[twine](http://pypi.python.org/pypi/twine. and then run:

```
python setup.py sdist bdist_wheel
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

To build and pucblish the documentsation:

```
cd docs
make gh-pages
cd ..
```

