# Installation

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
name = "composition"
description = "Docker-compose package manager"
readme = "README.md"
license = ""
authors = [
    { name = "sam", email = "sam@fake.com" },
]
dependencies = [
    "fire",
]
dynamic = [
    "version",
]

[project.scripts]
composition = "composition.composition:entrypoint"

[project.urls]
Homepage = "http://fake.com"

[tool.hatch.version]
path = "composition/__init__.py"

[tool.hatch.build.targets.sdist]
include = [
    "/composition",
]
```

`sudo hatch build && sudo hatch publish`

# Generating requirements
`pip3 install pip-tools`
`pip-compile requirements.in > requirements.txt`

# To install locally
`pip3 install --upgrade docker-composition`