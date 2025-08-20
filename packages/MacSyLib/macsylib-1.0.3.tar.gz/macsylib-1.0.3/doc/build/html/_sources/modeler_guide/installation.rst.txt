.. MacSyLib - python library that provide functions for
   detection of macromolecular systems in protein datasets
   using systems modelling and similarity search.
   Authors: Sophie Abby, Bertrand Néron
   Copyright © 2014-2025 Institut Pasteur (Paris) and CNRS.
   See the COPYRIGHT file for details
   MacSyLib is distributed under the terms of the GNU General Public License (GPLv3).
   See the COPYING file for details.


.. _modeler_installation:

************
Installation
************

MacSyLib works with models for macromolecular systems that are not shipped with it,
you have to install them separately. See the :ref:`msl_data section <modeler_msl_data>` below.


===============================
MacSyLib Installation procedure
===============================

To develop new models and share them, MacSyLib requires *git* and the python library *GitPython*

Below the procedure to install *MacSyLib* in *modeler* mode in a virtualenv

.. code-block:: bash

    python3 -m venv macsylib
    cd macsylib
    source bin/activate
    python3 -m pip install macsylib[model]


*GitPython* dependency will be automatically retrieved and installed when using `pip` for installation (see below).

.. warning::

    But you have to install *git* by yourself (using your preferred package manager)


From Conda/Mamba
================

MacSylib is packaged for Conda/Mamba.
The Conda/Mamba package include modeler dependencies


From container
==============

From version 2.0 and above, a docker image is available. This image allow you to develop models.


.. _modeler_msl_data:

====================================
Models installation with `msl_data`
====================================

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

To install it in your home (*./<macsylib>/data*)::

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

To create a git repository with a skeleton for your own model package::

    msl_data init --pack-name <MY_PACK_NAME> --maintainer <"mantainer name"> --email <maintainer email> --authors <"author1, author2, ..">

above msl_data with required options. Below I add optional but recommended options. ::

    msl_data init --pack-name <MY_PACK_NAME> --maintainer <"mantainer name"> --email <maintainer email> --authors <"author1, author2, .."> \
    --license cc-by-nc-sa --holders <"the copyright holders"> --desc <"one line package description">

To list all `msl_data` subcommands::

    msl_data --help

To list all available options for a subcommand::

    msl_data <subcommand> --help

For models not stored in *macsy-models* the commands *available*, *search*,
*installation* from remote or *upgrade* from remote are **NOT** available.

For models **NOT** stored in *macsy-models*, you have to manage them semi-manually.
Download the archive (do not unarchive it), then use *msl_data* to install the archive.
