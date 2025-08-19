aiwb-cli
========

This package provides a unified command line interface to Renesas AI
Workbench Service.

Jump to: - `Getting Start <#installation>`__

Requirements
~~~~~~~~~~~~

The aws-cli package works on Python versions:

-  3.9.x and greater
-  3.10.x and greater
-  3.11.x and greater
-  3.12.x and greater

Installation
------------

For Developers
^^^^^^^^^^^^^^

aiwb-cli’s dependencies use a range of packaging features provided by
``wheel`` and ``setuptools``. To ensure smooth installation, it’s
recommended to use:

Create virtual env

::

   cd aiwb-cli
   python3 -m venv .venv

Install Pre-requisites

::

   .venv/bin/pip3 install build wheel

Building wheel package

::

   .venv/bin/python3 -m build --wheel

Install package

::

   .venv/bin/pip3 install --force-reinstall dist/aiwb-<version>-py3-none-any.whl # add --force-reinstall so as to force re-write the package

For end users
^^^^^^^^^^^^^

End users only need to install the packged aiwb-cli with pip command.

::

   pip3 install <public aiwb package name>

Usage
-----

Configuration
~~~~~~~~~~~~~

For custom AI workbench endpoints, you will need to setup AIWB service
url before using it, otherwise, cli will route to default service url
``ai.aws.renesasworkbench.com``

::

   export AIWB_URL="http://localhost:8080"

Before getting start, you need to login

::

   aiwb login

To check user identity

::

   aiwb whoami

You can revoke the session by logout command

::

   aiwb logout

Basic Commands
~~~~~~~~~~~~~~

An CLI command has the following structure:

::

   aiwb [OPTIONS] COMMAND [ARGS]...

For example, to list workbench, the command would be:

::

   aiwb workbench list

To get the version of the AWS CLI:

::

   aiwb version

To view help documentation, use the following:

::

   aiwb --help