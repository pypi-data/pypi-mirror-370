.. MacSyLib - python library that provide functions for
    detection of macromolecular systems in protein datasets
    using systems modelling and similarity search.
    Authors: Sophie Abby, Bertrand Néron
    Copyright © 2014-2025 Institut Pasteur (Paris) and CNRS.
    See the COPYRIGHT file for details
    MacsyLib is distributed under the terms of the GNU General Public License (GPLv3).
    See the COPYING file for details.

.. _configuration:

*************
configuration
*************

Options to run MacSyLib can be specified in a :ref:`Configuration file <config-definition-label>`.
The API described below handles all configuration options for MacSylib.

The :class:`macsypy.config.MacsyDefaults` hold the default values for `macsylib` whereas
the :class:`macsypy.config.Config` hold the values for a `macsylib` run.

.. _config_api:

configuration API reference
===========================

MacsyDefaults
=============

Hold the default values for `macsylib`

.. autoclass:: macsylib.config.MacsyDefaults
   :members:
   :private-members:
   :special-members:


Config
======

Hold the values for this `macsylib` run

.. autoclass:: macsylib.config.Config
   :members:
   :private-members:
   :special-members:


NoneConfig
==========

Minimalist Config object just use in some special case where config is required by api
but not used for instance in :class:`macsylib.package.Package`

.. autoclass:: macsylib.config.NoneConfig
   :members:
   :private-members:
   :special-members:
