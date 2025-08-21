"""Package Setup."""

import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
version_path = os.path.join(here, "onvif/version.txt")
version = open(version_path).read().strip()

requires = [
    "aiohttp>=3.12.9",
    "httpx>=0.19.0,<1.0.0",
    "zeep[async]>=4.2.1,<5.0.0",
    "ciso8601>=2.1.3",
    "yarl>=1.10.0",
]

CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Customer Service",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Telecommunications Industry",
    "Natural Language :: English",
    "Operating System :: POSIX",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Multimedia :: Sound/Audio",
    "Topic :: Utilities",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]

setup(
    name="onvif-zeep-async",
    version=version,
    description="Async Python Client for ONVIF Camera",
    long_description=open("README.rst").read(),
    author="Cherish Chen",
    author_email="sinchb128@gmail.com",
    maintainer="sinchb",
    maintainer_email="sinchb128@gmail.com",
    license="MIT",
    keywords=["ONVIF", "Camera", "IPC"],
    url="http://github.com/hunterjm/python-onvif-zeep-async",
    zip_safe=False,
    python_requires=">=3.10",
    packages=find_packages(exclude=["docs", "examples", "tests"]),
    install_requires=requires,
    package_data={
        "": ["*.txt", "*.rst"],
        "onvif": ["*.wsdl", "*.xsd", "*xml*", "envelope", "include", "addressing"],
        "onvif.wsdl": ["*.wsdl", "*.xsd", "*xml*", "envelope", "include", "addressing"],
    },
)
