![Build Status](https://gitlab.cern.ch/cms-dqmdc/libraries/dism-core/badges/develop/pipeline.svg)
![Coverage](https://gitlab.cern.ch/cms-dqmdc/libraries/dism-core/badges/develop/coverage.svg)
![Latest Release](https://gitlab.cern.ch/cms-dqmdc/libraries/dism-core/-/badges/release.svg)

# dism-core

DIALS Inference Service Manager Core or simply `dism-core` is a python package that provides core functionality for validating custom YAML templates used to manage custom `InferenceService` resources in KServe managed by DIALS. It leverages the `pydantic` library to ensure that the YAML templates conform to the required schema.

> [!WARNING]
> This package is not intended to be installed or used directly. Instead, it serves as a foundational library for other packages that require YAML validation for KServe custom `InferenceService` deployments.

## Development

Install the dependencies and the package using `uv`:

```shell
uv sync --all-groups
uv run pre-commit install
uv pip install -e .
```

### Running tests

Run tests with `pytest`:

```shell
uv run pytest tests
```

#### Tox

You may also want to run the tests with `tox` to test against multiple python versions:

```shell
uv run tox
```

**[asdf](https://asdf-vm.com/) users**

tox requires multiple versions of Python to be installed. Using `asdf`, you have multiple versions installed, but they aren’t normally exposed to the current shell. You can use the following command to expose multiple versions of Python in the current directory:

```bash
asdf set python 3.12.9 3.11.10 3.10.13
```

This will use `3.12.9` by default (if you just run `python`), but it will also put `python3.11` and `python3.10` symlinks in your PATH so you can run those too (which is exactly what tox is looking for).

### Releasing the package on PyPI

The package is available in PyPI at [cmsdials](https://pypi.org/project/dism-core/), under the [cmsdqm](https://pypi.org/org/cms-dqm/) organization. You'll need at leat Mantainer rights to be able to push new versions. This package is not meant to be deployed in PyPI, since it is simply a foundational library for `dials-service` and `dism-cli`.

### CI

The GitLab CI is configured to automatically publish the release notes in GitLab whever a tag is pushed to the repo.

> [!NOTE]
> For this to work the CI/CD variables named `UV_PUBLISH_TOKEN` and `GITLAB_TOKEN` should be registered in gitlab. The `GITLAB_TOKEN` is a Project Access Token with api read/write rights, which is needed to read merge requests using the `glab-cli`.
> https://gitlab.cern.ch/cms-dqmdc/libraries/dism-core/-/settings/access_tokens
