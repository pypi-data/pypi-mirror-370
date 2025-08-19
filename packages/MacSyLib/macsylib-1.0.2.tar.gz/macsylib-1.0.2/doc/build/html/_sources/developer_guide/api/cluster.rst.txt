.. MacSyLib - python library that provide functions for
   detection of macromolecular systems in protein datasets
   using systems modelling and similarity search.
   Authors: Sophie Abby, Bertrand Néron
   Copyright © 2014-2025 Institut Pasteur (Paris) and CNRS.
   See the COPYRIGHT file for details
   MacsyLib is distributed under the terms of the GNU General Public License (GPLv3).
   See the COPYING file for details.


.. _cluster:

*******
cluster
*******

A cluster is an ordered set of hits related to a model which satisfy the model distance constraints.

.. _cluster_api:

cluster API reference
=====================

Class Cluster
=============
.. autoclass:: macsylib.cluster.Cluster
   :members:
   :private-members:
   :special-members:


cluster functions
=================

Functions that help to build :class:`macsylib.cluster.Cluster` object.

.. automodule:: macsylib.cluster
   :members:
   :exclude-members: macsylib.custer.Cluster
