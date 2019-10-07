# ReleaseRabbit

A little tool to make releasing new versions of open source projects easier.

# Setup

- Add `releaserabbit` script to your `$PATH`.
- Setup your pypi credentials in `~/.pypirc`.
- *`setup.py` must pull version name from a separate version file (see snippet below). `VERSION_FILE` must be a constant in setup.py*
- Make sure you can push commits and tags to master.
- Install github's `hub` and authorize it.

# Pulling version from a separate file

```python
import io, re
VERSION_FILE = "cleancat/__init__.py"
with io.open(VERSION_FILE, "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = ([\'"])(.*?)\1', f.read()).group(2)
```

# Usage

```
$ cd myproject
$ releaserabbit 1.2.3
```
