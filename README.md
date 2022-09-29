# Blueprint API
While  ``blueprint api`` can be set up and used independently, it's recommended that setting up the local development 
environment is done via the infrastructure repo: <https://github.com/CMSgov/blueprint_infra>.

If not utilizing the infrastructure repo to set up the project for development locally, the following are required:
- python 3.10
- postgres (or a running instance of postgres using the 
[official docker image](https://github.com/docker-library/docs/tree/master/postgres#how-to-use-this-image))

Create a database and superuser either with [initdb](https://www.postgresql.org/docs/14/app-initdb.html) or by supplying
the necessary environment variables with using the postgres docker image.

## Contributing
While it's recommended that ``blueprint api`` is run via docker, it's not required.
If developing within a docker container, the following bash commands described in subsequent sections can be run within
the container via `docker exec -it blueprint_api_1 bash` for example.

### Poetry
Blueprint API uses [Poetry](https://python-poetry.org/) for dependency management.

**Optional:** If you want to install Poetry locally follow 
[these instructions](https://python-poetry.org/docs/#installation).

#### Usage

```bash
# To add a dependency run
poetry add [PACKAGE]

# To view the dependency tree run:
poetry show --tree

# To update dependencies run:
poetry update
```

If developing within a container, you will need to rebuild after adding any new dependencies.

```bash
docker-compose build
```

### Pre-commit
A pre-commit configuration is included in the repo to assist in the development workflow.
It's not required for development, but can be useful.

To use pre-commit, ensure that you have installed [pre-commit](https://pre-commit.com/#install) on your machine and that
you have instantiated pre-commit in the **Blueprint API** repository by running `pre-commit install` in the root of your
local copy of the repo.

Once you have ``pre-commit`` installed, _pre-commit hooks_ will run each time that you do a git commit. ``pre-commit``
will try to resolve many issues, but you will be required to resolve those that it cannot before pushing your code.

### Create an admin user and using the admin site
When developing locally, it's useful to have an admin user.
To add a super-user to your local database, run:
```bash
python3 manage.py createsuperuser
```
And enter a username and password when prompted. 
This will allow access to access the admin site, http://localhost:8000/admin/ where the database can be interacted with 
directly.

### Migrations
When there are changes to the database models, migrations will need to be executed: 
```bash
python3 manage.py migrate
````

For more information about database migrations, see [this](https://docs.djangoproject.com/en/4.1/topics/migrations/).

### Testing
Run unit tests:
```bash
# To run all the tests
python3 manage.py test

# Or, to run a specific test(s), add the name of the directory path or the specific test within the directory path and 
# file.
# Examples:
python3 manage.py test directory
python3 manage.py test directory.filename
python3 manage.py test directory.filename.TestClassName
```

To run the server (outside the docker container), first set the following environment variables:
- POSTGRES_DB_HOST=localhost
- POSTGRES_DB_NAME
- POSTGRES_PASSWORD
- POSTGRES_USER

Where `POSTGRES_DB_NAME`, `POSTGRES_PASSWORD`, and `POSTGRES_USER` will need to correspond to the database name and 
postgres super-user created during database setup.

Then run the server:
```bash
python3 manage.py runserver
```

### SwaggerUI
Go to http://localhost:8000/doc/ to see the SwaggerUI
Go to http://localhost:8000/doc.json or http://localhost:8000/doc.yaml to see the unformatted spec
<<<<<<< HEAD

### Django REST Framework UI
Go to http://localhost:8000/ to see the index page of the REST framework UI.
Any request defined in for the API can be executed in a browser and viewed via this UI, but actions/data may be 
restricted until a user logs in with appropriate permissions.
=======
>>>>>>> ac6c8a7 (Adding new test for download.)
