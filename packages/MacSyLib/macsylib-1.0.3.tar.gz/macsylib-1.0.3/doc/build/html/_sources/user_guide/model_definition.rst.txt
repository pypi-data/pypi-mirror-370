.. MacSyLib - python library that provide functions for
   detection of macromolecular systems in protein datasets
   using systems modelling and similarity search.
   Authors: Sophie Abby, Bertrand Néron
   Copyright © 2014-2025 Institut Pasteur (Paris) and CNRS.
   See the COPYRIGHT file for details
   MacSyLib is distributed under the terms of the GNU General Public License (GPLv3).
   See the COPYING file for details.


.. _model_definition:

*********************
Macromolecular models
*********************


MacSyLib relies on the definition of models of macromolecular systems as a **set of models' components**
to be searched by similarity search, and a **set of rules** regarding their genomic organization and
their requirement level to make a complete system (mandatory, accessory components, number of components required).

See :ref:`below<model-definition-grammar-label>` for more details on MacSyLib's modelling scheme and the section
on :ref:`Functioning <functioning>` for the principles of the MacSyLib's search engine.


A **MacSyLib model** (macsy-model for short) is the association of several elements:

    * a **definition** which describes the system to detect with a specific **XML grammar** that is described :ref:`below<model-definition-grammar-label>`.

    * a set of :ref:`HMM profiles <provide-hmm_label>`  (one per component/gene in the model) to enable the similarity search of the systems' components with the HMMER program.

The models are grouped by *family* possibly gathering *sub-families* (multiple levels allowed), for instance *Secretion*, *Cas-proteins*...
A set of models from a same family (coherent set) of systems to detect is called hereafter a **macsy-model package**.


.. note::
  For details on how to create your own macsy-models, have a look at the :ref:`modeler_guide`.



******************
Installing  models
******************


How to install new models
=========================

MacSyLib does not provide models. You must install models before using it.
The ``msl_data`` utility tool is shipped with `MacSyLib` to deal with macsy-models:


msl_data <subcommand> [options]

The main sub-commands are

* ``msl_data available`` to get the list of macsy-models available
* ``msl_data search`` to search a model given its name or a pattern in its description
* ``msl_data install`` to install a macsy-model package (the installed version can be set see --help)
* ``msl_data cite`` to retrieve information on how to cite the model
* ``msl_data show`` to show the structure of model package
* ``msl_data definition`` to display one or a set of model defintion
* ``msl_data --help`` to get the extended list of available subcommands
* ``msl_data <subcommand> --help`` to get help about the specified subcommand


Where the models are located
============================

MacSyLib looks at several locations to find macsy-models.

system-wide installation
------------------------

By default *msl_data* installs models in a shared location (set by --install-data option) that is
`/usr/share/macsylib/` or `/usr/local/share/macsylib` depending on your Operating System distribution.
If you use a *virtualenv*, the shared resources are located in the `<virtualenv>/share/macsylib` directory.


user-wide installation
----------------------

If you don't own rights to install system-wide, you can install models in the MacSyLib's cache
located in your home: `$HOME/.macsylib/data/`.
*msl_data* installs packages in this location when you use the `--user` option.
The packages installed in user land is added to the system-wide packages.


.. note::

   If two packages have the same name, the package in the user land supersedes the system-wide package.


project-wide installation
-------------------------

If you cannot install macsy-model packages in system or user land locations,
you can install models in specific directory with the `--target` option.::

    msl_data install --target <my_models>

The specify this specific location with the ``--models-dir`` :ref:`command-line option <path-options>`.::

    MacSyLib --db-type ordered_replicon --models-dir=my_models --models TFF-SF all --sequence-db my_genome.fasta

The path must point at a directory that contains macsy-model packages as described :ref:`above <package_structure>`.
