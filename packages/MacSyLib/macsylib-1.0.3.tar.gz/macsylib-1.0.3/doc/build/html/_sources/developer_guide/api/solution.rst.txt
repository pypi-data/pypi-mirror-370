.. MacSyLib - python library that provide functions for
    detection of macromolecular systems in protein datasets
    using systems modelling and similarity search.
    Authors: Sophie Abby, Bertrand Néron
    Copyright © 2014-2025 Institut Pasteur (Paris) and CNRS.
    See the COPYRIGHT file for details
    MacsyLib is distributed under the terms of the GNU General Public License (GPLv3).
    See the COPYING file for details.

.. _solution:

********
solution
********

MacSyLib find lot of potential systems for the same model,
all these systems are saved in "all_systems.xxx" files.
This module allow to explore among of all systems which combination seems to be more probable.


.. _solution_api:

solution API reference
======================

Solution
========
.. autoclass:: macsylib.solution.Solution
   :members:
   :private-members:
   :special-members:

combine_clusters
================
.. autofunction:: macsylib.solution.combine_clusters

combine_multisystems
====================
.. autofunction:: macsylib.solution.combine_multisystems

find_best_solutions
===================
.. autofunction:: macsylib.solution.find_best_solutions
