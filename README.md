# ReleaseRabbit

A little tool to make releasing new versions of open source Python projects easier.

In one simple command, ReleaseRabbit bumps version number in your project, pushes a github release, packs and uploads Python package to PyPI.

# Usage

```
$ cd myproject
$ releaserabbit 1.2.3
```

# Setup

1. `pip install releaserabbit`.
1. Setup your pypi credentials in `~/.pypirc`.
1. *`setup.py` must pull version name from a separate version file (see snippet below). `VERSION_FILE` must be a constant in setup.py*
    - Alternative: `VERSION` as a string constant in `setup.py` if you can't (or don't want to) expose `__version__` in your actual production python code.
1. Make sure you can push commits and tags to master.

# Pulling version from a separate file

```python
import io, re
VERSION_FILE = "cleancat/__init__.py"
with io.open(VERSION_FILE, "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = ([\'"])(.*?)\1', f.read()).group(2)
```
