from setuptools import setup
import setuptools_scm

# Retrieve the version using setuptools_scm
version = setuptools_scm.get_version(root="../")

setup(
    install_requires=[
        f"contentgrid-hal-client=={version}",
    ],
)