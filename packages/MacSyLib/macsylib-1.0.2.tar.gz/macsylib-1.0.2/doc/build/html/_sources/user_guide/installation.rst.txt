.. MacSyLib - python library that provide functions for
   detection of macromolecular systems in protein datasets
   using systems modelling and similarity search.
   Authors: Sophie Abby, Bertrand Néron
   Copyright © 2014-2025 Institut Pasteur (Paris) and CNRS.
   See the COPYRIGHT file for details
   MacSyLib is distributed under the terms of the GNU General Public License (GPLv3).
   See the COPYING file for details.



.. _user_installation:

************
Installation
************

MacSyLib works with models for macromolecular systems that are not shipped with it,
you have to install them separately. See the :ref:`msl_data section <msl_data>` below.

.. _user_dependencies:

=====================
MacSyLib dependencies
=====================
**Python version >=3.10** is required to run MacSyLib: https://docs.python.org/3.10/index.html

MacSyLib has one program dependency:

 - the *Hmmer* program, version 3.1 or greater (http://hmmer.org/).

The *hmmsearch* program should be installed (*e.g.*, in the PATH) in order to use MacSyLib.
Otherwise, the paths to this executable must be specified in the command-line:
see the :ref:`command-line options <hmmer-options>`.


MacSyLib also relies on six Python library dependencies:

 - colorlog
 - colorama
 - pyyaml
 - packaging
 - networkx
 - pandas

These dependencies will be automatically retrieved and installed when using `pip` for installation (see below).

.. note::
    If you intend to build and distribute new models you will need some other dependencies see modeler guide for installation.

.. note::
    If you want to contribute to the *MacSyLib* code, check the guide lines (`CONTRIBUTING <https://github.com/gem-pasteur/macsylib/blob/master/CONTRIBUTING.md>`_)
    and specific procedure for :ref:`developer installation <dev_installation>`.


==================================
MacSyLib Installation procedure
==================================

It is recommended to use `pip` to install the MacSyLib package.

Archive overview
================

* **doc** => The documentation in html and pdf
* **test** => All what is needed for unitary tests
* **src/macsylib** => The macsylib python library
* **setup.py** => The installation script (to include documentation)
* **pyproject.toml** => The project installation build tool
* **COPYING** => The licensing
* **COPYRIGHT** => The copyright
* **README.md** => Very brief MacSyLib overview
* **CONTRIBUTORS** => List of people who contributed to the code
* **CONTRIBUTING** => The guide lines to contribute to the code


Installation steps:
===================

Make sure every required dependency/software is present.
--------------------------------------------------------

By default MacSyLib will try to use `hmmsearch` in your PATH. If `hmmsearch` is not in the PATH,
you have to set the absolute path to `hmmsearch` in a :ref:`configuration file <config-definition-label>`
or in the :ref:`command-line <hmmer-options>` upon execution.
If the tools are not in the path, some test will be skipped and a warning will be raised.


Perform the installation.
-------------------------

.. code-block:: bash

    python3 -m pip install macsylib


If you do not have the privileges to perform a system-wide installation,
you can either install it in your home directory or
use a `virtual environment <https://virtualenv.pypa.io/en/stable/>`_.

installation in your home directory
"""""""""""""""""""""""""""""""""""

.. code-block:: bash

    python3 -m pip install --user macsylib


installation in a virtualenv
""""""""""""""""""""""""""""

.. code-block:: bash

    python3 -m venv macsylib
    cd macsylib
    source bin/activate
    python3 -m pip install macsylib

To exit the virtualenv just execute the `deactivate` command.
To use `macsylib`, you need to activate the virtualenv:

.. code-block:: bash

    source macsylib/bin/activate

Then use `macsylib` as python library or the `msl_data` command line tool.


.. note::
  Super-user privileges (*i.e.*, ``sudo``) are necessary if you want to install the program in the general file architecture.


.. note::
  If you do not have the privileges, or if you do not want to install MacSyLib in the Python libraries of your system,
  you can install MacSyLib in a virtual environment (http://www.virtualenv.org/).

.. warning::
  When installing a new version of MacSyLib, do not forget to uninstall the previous version installed !


Uninstalling MacSyLib
========================

To uninstall MacSyLib (the last version installed), run

.. code-block:: bash

  (sudo) pip uninstall macsylib

If you have installed it in a virtualenv, just delete the virtual environment.
For instance if you create a virtualenv name *macsylib*

.. code-block:: bash

    python3 -m venv macsylib

To delete it, remove the directory

.. code-block:: bash

    rm -R macsylib

From Conda/Mamba
================

From version 1.0, MacSyLib is packaged for Conda/Mamba
.. code-block:: text

    mamba install -c macsylib=x.x

Where `x.x` is the macsylib version you want to install


.. _msl_data:

===================================
Models installation with `msl_data`
===================================

Once MacSyLib is installed you have access to an utility program to manage the models: `msl_data`

This script allows to search, download, install and get information from MacSyLib models stored on
github (https://github.com/macsy-models) or locally installed. The general syntax for `msl_data` is::

    msl_data <general options> <subcommand> <sub command options> <arguments>


To list all models available on *macsy-models*::

    msl_data available

To search for models on *macsy-models*::

    msl_data search TXSS

you can also search in models description::

    msl_data search -S secretion

To install a model package::

    msl_data install <model name>

To install a model when you have not the right to install it system-wide

To install it in your home (*./macsylib/data*)::

    msl_data install --user <model name>

To install it in any directory::

    msl_data install --target <model dir> <model_name>

To know how to cite a model package::

    msl_data cite <model name>

To show the name of the models and the structure of installed model package::

   msl_data show <model package name>

for instance :code:`msl_data show TXSScan`

.. code-block:: text

   TXSScan
       ├-archaea
       │   └-Archaeal-T4P
       └-bacteria
            ├-diderm
            │   ├-Flagellum
            │   ├-MSH
            │   ├-T1SS
            │   ├-T2SS
            │   ├-T3SS
            │   ├-T4aP
            │   ├-T4bP
            │   ├-T5aSS
            │   ├-T5bSS
            │   ├-T5cSS
            │   ├-T6SSi
            │   ├-T6SSii
            │   ├-T6SSiii
            │   ├-T9SS
            │   ├-Tad
            │   ├-pT4SSi
            │   └-pT4SSt
            └-monoderm
                 └-ComM

   TXSScan (1.1.3) : 19 models

To show the model definition::

    msl_data definition <package or subpackage> model1 [model2, ...]

for instance to show model definitions T6SSii and T6SSiii in TXSS+/bacterial subpackage::

    msl_data definition TXSS+/bacterial T6SSii T6SSiii

To show all models definitions in TXSS+/bacterial subpackage::

    msl_data definition TXSS+/bacterial

To create a skeleton for your own model package (to access init subcommand check :ref:`modeler instaltion <modeler_installation>`)::

    msl_data init --pack-name <MY_PACK_NAME> --maintainer <"mantainer name"> --email <maintainer email> --authors <"author1, author2, ..">

above msl_data with required options. Below I add option but recommended options. ::

    msl_data init --pack-name <MY_PACK_NAME> --maintainer <mantainer name> --email <maintainer email> --authors <"author1, author2, .."> \
    --license cc-by-nc-sa --holders <"the copyright holders"> --desc <"one line package description">

To list all `msl_data` subcommands::

    msl_data --help

To list all available options for a subcommand::

    msl_data <subcommand> --help

For models not stored in *macsy-models* the commands *available*, *search*,
*installation* from remote or *upgrade* from remote are **NOT** available.

For models **NOT** stored in *macsy-models*, you have to manage them semi-manually.
Download the archive (do not unarchive it), then use *msl_data* to install the archive.
