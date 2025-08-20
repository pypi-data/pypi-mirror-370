.. MacSyLib - python library that provide functions for
    detection of macromolecular systems in protein datasets
    using systems modelling and similarity search.
    Authors: Sophie Abby, Bertrand Néron
    Copyright © 2014-2025 Institut Pasteur (Paris) and CNRS.
    See the COPYRIGHT file for details
    MacsyLib is distributed under the terms of the GNU General Public License (GPLv3).
    See the COPYING file for details.


.. _new:

**********************
What's new in MacSyLib
**********************

V 1.0.3
=======

Fix bug in `msl_data cite`


V 1.0.2
=======

Fix bug in `msl_data` when library used by third partite as `MacSyFinder`.


V 1.0.1
=======

| Now MacSyFinder and MacSyLib are two separated packages.
| MacSyFinder is build on top of MacSyLib.
| This new architecture allow to create new tool on the top of MacSyLib.

provide 2 scripts

- ``msl_data`` formerly `macsydata`
- ``msl_profile`` formerly `macsyprofile`

features
--------

* add new subcommand to msl_data ``msl_data show`` to show the structure of an installed package model :ref:`msl_data`


For older changelog see `https://macsyfinder.readthedocs.io/en/latest/ <macsyfinder documentation>`_.
