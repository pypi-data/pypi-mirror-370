# poetry-plugin-ivcap

A custom Poetry plugin that adds a `poetry ivcap` command for local and Docker-based deployments.

## Example Configuration

Add to your `pyproject.toml`:

```toml
[tool.poetry-plugin-ivcap]
service-file = "service.py"
service-id = "urn:ivcap:service:ac158a1f-dfb4-5dac-bf2e-9bf15e0f2cc7"
port = 8077
# docker
# docker-run-opts = { port = 8079 }```

## Installation

```bash
poetry self add poetry-plugin-ivcap
```

## Usage

```bash
poetry ivcap run
poetry ivcap docker-build
poetry ivcap docker-run
poetry ivcap docker-publish
poetry ivcap service-register
poetry ivcap create-service-idget
poetry ivcap tool-register
```

To get help on the currently installed version
```
% poetry ivcap

IVCAP plugin

Supporting the development of services and tools for the IVCAP platform

Available subcommands:
    run                 Run the service locally
    docker-build        Build the docker image for this service
    docker-run          Run the service's docker image locally
    docker-publish      Publish the service's docker image to IVCAP
    service-register    Register the service with IVCAP
    create-service-id   Create a unique service ID for the service
    tool-register       Register the service as an AI Tool with IVCAP

Example:
  poetry ivcap run

Configurable optiosn in pyproject.toml:

  [tool.poetry-plugin-ivcap]
  service-file = "service.py"  # The Python file that implements the service
  service-file = "service.py"
  service-id = "urn:ivcap:service:ac158a1f-dfb4-5dac-bf2e-9bf15e0f2cc7" # A unique identifier for the service

  docker-build-template = "docker buildx build -t #DOCKER_NAME#  ."
  docker-run-template = "docker run -rm -p #PORT#:#PORT#"
```

## Development

### Build the Plugin Package

```bash
poetry build
```

This creates .whl and .tar.gz files in the dist/ directory.

### Publish to PyPI

Create an account at https://pypi.org/account/register/

Add your credentials:
```bash
poetry config pypi-token.pypi <your-token>
```

Publish:
```bash
poetry publish --build
```

### Optional: Test on TestPyPI First

To verify your setup without publishing to the real PyPI:

```bash
poetry config repositories.test-pypi https://test.pypi.org/legacy/
poetry publish -r test-pypi --build
```

Then test installing via:

```bash
poetry self add --source test-pypi poetry-plugin-deploy
```
