# Description
Still very much in alpha. But a package manager similar to that of helm but for docker-compose applications. <br/>
Handles sub-applications and values.yaml files with templates similar to that used for kubernetes.yaml files. <br/>

To start you need three files (see examples here: https://github.com/sam-technesci/composer/tree/main/examples): <br/>
`app.yaml` <br/>
`template.yaml` <br/>
`values.yaml` <br/>
The templating language used is Jinja2 and you substitute variables from your values.yaml(s) into the template. <br/>
### Quick install
`cd examples/basic_application && composer install` <br/>
See the README.md at `examples/basic_application/README.md` for a walk-through. <br/>
Defaults to using values.yaml in the same directory. <br/>
To view your template before installing it you can do `composer template` or you can save a template with `composer template > docker-compose.yaml` <br/>
For more commands do: `composer --help`
# Installation
## Helper Script
```bash
curl -fsSL https://raw.githubusercontent.com/sam-technesci/composer/installation-helper/install.sh -o get-composer.sh && sudo sh get-composer.sh
```
## Manual 
Install python39 and pip3.
Then do:
`pip3 install --upgrade docker-composition`

# .deb Creation
Install
`sudo apt-get install python3-stdeb`


# Project setup 
Using hatch as a tool to manage package:
https://hatch.pypa.io/latest/intro/

`hatch new composition`

## Publishing

Ensured the `pyproject.toml` looked like this:
```toml
[build-system]
requires = [
    "hatchling>=1.7.0",
]
build-backend = "hatchling.build"

[project]
name = "docker-composition"
description = "Docker-compose package manager"
readme = "README.md"
license = ""
authors = [
    { name = "sam", email = "sam@fake.com" },
]
dependencies = [
    "humanize",
    "petname",
    "PyYAML",
    "Jinja2",
    "click"
]
dynamic = [
    "version",
]

[project.scripts]
composer = "composition.composer:entrypoint"

[project.urls]
Homepage = "https://github.com/sam-technesci/composer"

[tool.hatch.version]
path = "composition/__init__.py"

[tool.hatch.build.targets.sdist]
include = [
    "/composition",
]
```

Note: remember to update `__version__.py` <br/>
Then run: <br/>
`sudo hatch build && sudo hatch publish`

# Generating requirements
`pip3 install pip-tools`
`pip-compile requirements.in > requirements.txt`

# To install locally
`pip3 install --upgrade docker-composition`