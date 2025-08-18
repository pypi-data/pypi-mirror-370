#!/usr/bin/env python

from setuptools import setup, find_packages
from insight_plugin import VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="insight_plugin",
    version=VERSION,
    description="Plugin tooling for the Rapid7 Insight platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rapid7 Integrations Alliance",
    author_email="integrationalliance@rapid7.com",
    url="https://github.com/rapid7/insight-plugin",
    packages=find_packages(),
    package_data={
        "insight_plugin": [
            "**/*",
            "templates/.dockerignore.jinja",
            "templates/connector/.dockerignore.jinja",
            "templates/*/*",
            "templates/*/*/*",
            "templates/*/*/*/*",
            "black_config.toml"
        ],
    },
    install_requires=[
        "jinja2==3.1.6",
        "pyyaml==6.0.1",
        "jsonschema==2.3.0",
        "mdutils==1.3.1",
        "jq==1.4.0",
        "insightconnect-integrations-validators~=2.47",
        "markupsafe==2.0.1",
        "ruamel.yaml==0.17.21",
        "ruamel.yaml.clib==0.2.7",
        "semver==3.0.4",
        "black==24.10.0",
        "parameterized==0.8.1",
        "prospector==1.14.1",
        "prospector[with_bandit]",
    ],
    entry_points={"console_scripts": ["insight-plugin=insight_plugin.__main__:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Topic :: Software Development :: Build Tools",
    ],
    license="MIT",
)
