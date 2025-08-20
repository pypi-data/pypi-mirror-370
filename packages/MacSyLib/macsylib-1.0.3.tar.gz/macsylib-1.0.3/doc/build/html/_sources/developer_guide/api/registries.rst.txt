.. MacSyLib - python library that provide functions for
    detection of macromolecular systems in protein datasets
    using systems modelling and similarity search.
    Authors: Sophie Abby, Bertrand Néron
    Copyright © 2014-2025 Institut Pasteur (Paris) and CNRS.
    See the COPYRIGHT file for details
    MacsyLib is distributed under the terms of the GNU General Public License (GPLv3).
    See the COPYING file for details.

.. _registries:


**********
registries
**********

The registry manage the different location where `macsylib` can find models definitions and their associated profiles.

.. _registries_api:

registries API reference
========================

ModelRegistry
=============
.. autoclass:: macsylib.registries.ModelRegistry
   :members:
   :private-members:
   :special-members:


ModelLocation
=============
.. autoclass:: macsylib.registries.ModelLocation
   :members:
   :private-members:
   :special-members:


MetaDefLoc
==========
.. autoclass:: macsylib.registries.MetaDefLoc
   :members:
   :private-members:
   :special-members:


DefinitionLocation
==================
.. autoclass:: macsylib.registries.DefinitionLocation
   :members:
   :private-members:
   :special-members:


split_def_name
===================
.. autofunction:: macsylib.registries.split_def_name


join_def_path
===================
.. autofunction:: macsylib.registries.join_def_path


scan_models_dir
===============
.. autofunction:: macsylib.registries.scan_models_dir
