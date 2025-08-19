[![PyPI version](https://badge.fury.io/py/easys-ordermanager.svg)](https://badge.fury.io/py/easys-ordermanager)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/Lektor.svg)](https://pypi.org/project/easys-ordermanager/)

# EasyS order manager API

## Compatibility

### Django 4.2

Python 3.11 to 3.12
DRF 3.14 to 3.16

### Django 5.0

Python 3.11 to 3.12
DRF 3.14 to 3.16

### Django 5.1

Python 3.11 to 3.13
DRF 3.14 to 3.16

### Django 5.2

Python 3.11 to 3.13
DRF 3.14 to 3.16

# Making a new release

[bump-my-version](https://github.com/callowayproject/bump-my-version) is used to manage releases.

After reaching a releasable state, run `pipx run bump-my-version bump <patch|minor|major> --message="feat: release x, refs y`

This will update the release version in `.bumpversion.toml` and the CI/CD pipelines do the rest.
