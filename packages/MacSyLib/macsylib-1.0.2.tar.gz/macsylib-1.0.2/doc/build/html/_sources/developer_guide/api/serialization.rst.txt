.. MacSyLib - python library that provide functions for
    detection of macromolecular systems in protein datasets
    using systems modelling and similarity search.
    Authors: Sophie Abby, Bertrand Néron
    Copyright © 2014-2025 Institut Pasteur (Paris) and CNRS.
    See the COPYRIGHT file for details
    MacsyLib is distributed under the terms of the GNU General Public License (GPLv3).
    See the COPYING file for details.
.. _serialization:

*************
serialization
*************

This module is a technical module where we can find the different way
to serialize the results:

   * the Systems found
   * The best solutions (best combination of systems)
   * The rejected candidates


.. _serialization_api:

SystemSerializer
================
.. autoclass:: macsylib.serialization.SystemSerializer
   :members:
   :private-members:
   :special-members:


TsvSystemSerializer
===================
.. autoclass:: macsylib.serialization.TsvSystemSerializer
   :members:
   :private-members:
   :special-members:


TsvSolutionSerializer
=====================
.. autoclass:: macsylib.serialization.TsvSolutionSerializer
   :members:
   :private-members:
   :special-members:


TsvLikelySystemSerializer
=========================
.. autoclass:: macsylib.serialization.TsvLikelySystemSerializer
   :members:
   :private-members:
   :special-members:


TsvRejectedCandidatesSerializer
===============================
.. autoclass:: macsylib.serialization.TsvRejectedCandidatesSerializer
   :members:
   :private-members:
   :special-members:


TsvSpecialHitSerializer
=======================
.. autoclass:: macsylib.serialization.TsvSpecialHitSerializer
   :members:
   :private-members:
   :special-members:


TxtSystemSerializer
===================
.. autoclass:: macsylib.serialization.TxtSystemSerializer
   :members:
   :private-members:
   :special-members:


TxtLikelySystemSerializer
=========================
.. autoclass:: macsylib.serialization.TxtLikelySystemSerializer
   :members:
   :private-members:
   :special-members:


TxtUnikelySystemSerializer
==========================
.. autoclass:: macsylib.serialization.TxtUnikelySystemSerializer
   :members:
   :private-members:
   :special-members:
