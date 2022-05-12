# Blueprint API

Please visit the infrastructure repo for setting up a local development environment at <https://github.com/CMSgov/blueprint_infra>

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
