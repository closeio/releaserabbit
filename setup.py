import io
import re

import setuptools

VERSION_FILE = "releaserabbit/__init__.py"
with io.open(VERSION_FILE, "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = ([\'"])(.*?)\1', f.read()).group(2)

setuptools.setup(
    name="releaserabbit",
    version=version,
    author="Vyacheslav Tverskoy",
    author_email="v@close.com",
    description="Bump release versions and make releases quickly",
    url="https://github.com/closeio/releaserabbit",
    packages=setuptools.find_packages(),
    install_requires=['twine'],
    classifiers=[
        'Intended Audience :: Developers',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        'Operating System :: POSIX',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'releaserabbit=releaserabbit:main',
        ],
    },
)
