# mb-cruise-migration

Migration scripts for migrating multibeam metadata from MB schema to CRUISE schema. 

## Usage: Migration Instructions

1. Create a python file and import the `ci-cmg-mb-cruise-migration` package.
2. Create an instance of the "Migrator" class, passing in the path to your config file as the only parameter.
3. Run the "migrate" method.

* An example run and start_background shell script is provided, which should be used to run the python script in the background.   
* The package and it's dependencies will need to be installed prior to usage. This can be done with `python -m pip install ci-cmg-mb-cruise-migration`. 

NOTE: if enabling pooled connections for cruise db in config, oracle client libraries need to also be installed:
https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html#optionally-install-oracle-client

## Developing Project

### Setup virtual environment

1. setup virtualenv
2. specify python installation for virtualenv to use
3. activate the virtual environment
4. verify python version and virtualenv
5. install required modules
6. verify they were installed with pip list
7. deactivate the virtual environment

```bash
virtualenv migenv

virtualenv --python=</path/to/python> </path/to/new/virtualenv/>

source ./migenv/bin/activate

which python
python -V

python -m pip install --upgrade poetry
poetry install

pip list

deactivate
```


### run tests 

Many (most) tests are integration tests and require either one or both the MB or CRUISE schema docker
containers be running.

#### To start docker containers:

from test dir:
```bash
./start-it.sh
```

#### To run tests (outside env): 

from project root:
```bash
# runs all tests
./run_tests 

# runs a test file
./run_tests <test filename>
```

#### To run tests (inside env):

```bash
cd tests
./start-it.sh
pytest
```

#### To stop docker containers:

from test dir:

```bash
./stop-it.sh
```

### build project

1. Update version in pyproject.toml either before or after release.
2. If not already installed: `python -m pip install --upgrade build`
3. Build distribution: `python -m build`
4. If not already installed: `python -m pip install --upgrade twine`
5. Upload to pypi: `twine upload dist/*`
