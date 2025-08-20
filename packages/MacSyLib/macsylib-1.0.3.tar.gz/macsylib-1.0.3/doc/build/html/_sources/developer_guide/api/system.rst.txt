.. MacSyLib - python library that provide functions for
    detection of macromolecular systems in protein datasets
    using systems modelling and similarity search.
    Authors: Sophie Abby, Bertrand Néron
    Copyright © 2014-2025 Institut Pasteur (Paris) and CNRS.
    See the COPYRIGHT file for details
    MacsyLib is distributed under the terms of the GNU General Public License (GPLv3).
    See the COPYING file for details.

.. _system:

******
system
******

This module classes and functions which a given set of hits and a model
compute if this set satisfy the model or not

The object which check the compliance of hits to a model is MatchMaker
which have 2 sub-classes for ordered and unordered replicons

`MatchMaker.match` method link hit to a model (:class:`macsylib.hit.ValidHit`)
and then check if these valid hit satisfy the quorum constraints defined
in the model. According this it instanciate a :class:`macsylib.system.System`
or :class:`macsylib.system.RejectedCandidate` for ordered replicons
or :class:`macsylib.system.LikelySystem` or :class:`macsylib.system.UnlikelySystem`
for unordered replicons

below the inheritance diagram:

.. inheritance-diagram::
      macsylib.system.AbstractSetOfHits
      macsylib.system.AbstractClusterizedHits
      macsylib.system.System
      macsylib.system.RejectedCandidate
      macsylib.system.AbstractUnordered
      macsylib.system.LikelySystem
      macsylib.system.UnlikelySystem
   :parts: 1


.. warning::
   The abstract class :class:`macsylib.system.AbstractSetOfHits` is controlled by the metaclass
   :class:`macsylib.system.MetaSetOfHits` which inject on the fly several private attributes and
   public properties (see more in :class:`macsylib.system.MetaSetOfHits` documentation)


.. inheritance-diagram::
      macsylib.system.MatchMaker
      macsylib.system.OrderedMatchMaker
      macsylib.system.UnorderedMatchMaker
   :parts: 1

.. _system_api:

system reference api
====================

MatchMaker
==========
.. autoclass:: macsylib.system.MatchMaker
   :members:
   :private-members:
   :special-members:

OrderedMatchMaker
=================
.. autoclass:: macsylib.system.OrderedMatchMaker
   :members:
   :private-members:
   :special-members:

UnorderedMatchMaker
===================
.. autoclass:: macsylib.system.UnorderedMatchMaker
   :members:
   :private-members:
   :special-members:

HitSystemTracker
================
.. autoclass:: macsylib.system.HitSystemTracker
   :members:
   :private-members:
   :special-members:

MetaSetOfHits
=============
.. autoclass:: macsylib.system.MetaSetOfHits
   :members:
   :private-members:
   :special-members:

AbstractSetOfHits
=================
.. autoclass:: macsylib.system.AbstractSetOfHits
   :members:
   :private-members:
   :special-members:

AbstractClusterizedHits
=======================
.. autoclass:: macsylib.system.AbstractClusterizedHits
   :members:
   :private-members:
   :special-members:

System
======
.. autoclass:: macsylib.system.System
   :members:
   :private-members:
   :special-members:

RejectedCandidate
=================
.. autoclass:: macsylib.system.RejectedCandidate
   :members:
   :private-members:
   :special-members:

AbstractUnordered
=================
.. autoclass:: macsylib.system.AbstractUnordered
   :members:
   :private-members:
   :special-members:

LikelySystem
============
.. autoclass:: macsylib.system.LikelySystem
   :members:
   :private-members:
   :special-members:

UnlikelySystem
==============
.. autoclass:: macsylib.system.UnlikelySystem
   :members:
   :private-members:
   :special-members:
