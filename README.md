NOTE: NOT FOR PRODUCTION USE

Please note these scripts are intended to allow experimentation with
Azure Container Service. They are not intended for production use.

This project provides a convenience CLI for creating, testing and
working with ACS clusters.

# Installation

The easiest way to get started is to use our Docker container,
however, the application is a Python3 application can can be run
anywhere you can find Python 3. 

Assuming you have Docker installed the application will run "out of the
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

For more information see the
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

The CLI will also use (and generate) SSH keys. These are stored in the
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
docker run -it -v ~/.ssh:/root -v $(pwd)/config:/config -v $(pwd):/src acs
azure login
```

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
docker push
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

