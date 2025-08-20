# -*- coding: utf-8 -*-
from setuptools import setup, find_packages, Command
import os
import sys

from zoho_somconnexio_python_client import __version__


with open("README.md") as f:
    README = f.read()


VERSION = __version__


########
# Copied from https://github.com/kennethreitz/setup.py
here = os.path.abspath(os.path.dirname(__file__))


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(VERSION))
        os.system("git push --tags")

        sys.exit()


########


setup(
    name="zoho-somconnexio-python-client",
    version=VERSION,
    author="SomConnexio",
    author_email="borja.gimeno@somconnexio.coop",
    maintainer="Borja Gimeno",
    url="https://git.coopdevs.org/coopdevs/som-connexio/zoho/zoho-somconnexio-python-client",
    description="Python wrapper for SomConnexio's Zoho (using REST API)",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=("tests", "docs")),
    include_package_data=True,
    zip_safe=False,
    install_requires=["requests"],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX :: Linux",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3.11",
    ],
    # $ setup.py publish support.
    cmdclass={
        "upload": UploadCommand,
    },
)
