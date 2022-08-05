# Blueprint API

## Local Development Setup

For with access to our current pipeline repository, please visit the infrastructure repo for setting up a local development environment at <https://github.com/CMSgov/blueprint_infra> For others, please follow the steps bellow

This repository is built along with <https://github.com/CMSgov/blueprint_ui> as the backend. They both utilize docker containers, so you will need to have it installed and running to continue.

Follow the UI repository README.md for setting up the local environments first, then you can comback here and run the following commands to start filling out the DB.

The following commands can be run to set up your local envionment
1) Make a new directory called blueprint
`mkdir blueprint`
2) Change directory to blueprint
`cd blueprint`
3) Clone the UI and API repositories into the blueprint directory
`git clone git@github.com:CMSgov/blueprint_ui.git`
`git clone git@github.com:CMSgov/blueprint_api.git`
4) Copy the sample docker-compose.yml file into this directory (you might want to edit the file afterwards to use values specific to your system)
`cp blueprint_api/docker-compose.yml.sample ../docker-compose.yml`
5) Docker setup
`docker-compose build`
`docker-compose run ui npm install`
`docker-compose up`

6) With the docker container running, change directory to API `cd blueprint_api`
7) Bash into the repo's docker container (e.g. `docker exec -it blueprint_api_1 bash`) to run the following commands.
8) Run the current migrations
`python3 manage.py migrate`
9) Setup an admin user
`python3 manage.py createsuperuser`

10) You will next need to add a catalog, sample one can be found at <https://github.com/CMSgov/ars-machine-readable/blob/main/3.1/oscal/json/CMS_ARS_3_1_catalog.json>
Once you have a catalog, you can utilize the admin panel <http://localhost:8000/admin/> and add a catalog
Name: ARS 3.1
File: the above json file

11) Once you have reached this point, you should be able to start adding components.
Components can currently found in <https://github.com/CMSgov/component-library> with your components, you can utilize the admin panel <http://localhost:8000/admin/> and add a component.
Title: OCISO
File: <https://github.com/CMSgov/component-library/blob/main/ociso/oscal/ociso.json>

At this point, your environment should be setup to start using the UI and creating projects.

12) Before making commits, make sure to run `brew install pre-commit` from inside the blueprint_api directory

## Contributing

### Poetry

Blueprint API uses [Poetry](https://python-poetry.org/) for dependency management.

**Optional:** If you want to install Poetry locally follow [these instructions](https://python-poetry.org/docs/#installation).

#### Usage

Enter the docker container (e.g. `docker exec -it blueprint_api_1 bash`) to run the following commands:

```bash
# To add a dependency run
poetry add [PACKAGE]

# To view the dependency tree run:
poetry show --tree

# To update dependencies run:
poetry update
```

Once you've added a dependency you will need to rebuild your container using:

```bash
docker-compose build
```

### Pre-commit

Ensure that you have installed [pre-commit](https://pre-commit.com/#install) on your machine and that you have instantiated pre-commit in the **Blueprint API** repository by running `pre-commit install` in the root of your local copy of the repo.

Once you have _pre-commit_ installed _pre-commit hooks_ will run each time that you do a git commit. _Pre-commit_ will try to resolve many issues, but you will be required to resolve those that it cannot before pushing your code.

### Testing

To run test automated tests, bash into the repo's docker container (e.g. `docker exec -it blueprint_api_1 bash`) to run the following commands:

```bash
# To run all the tests
python3 manage.py test

# To run a specific test(s), add the name of the directory path or the specific test within the directory path and file.
# Examples:
python3 manage.py test directory
python3 manage.py test directory.filename
python3 manage.py test directory.filename.TestClassName
```

### SwaggerUI
Go to http://localhost:8000/doc/ to see the SwaggerUI
Go to http://localhost:8000/doc.json or http://localhost:8000/doc.yaml to see the unformatted spec