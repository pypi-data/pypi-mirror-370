.. MacSyLib - python library that provide functions for
    detection of macromolecular systems in protein datasets
    using systems modelling and similarity search.
    Authors: Sophie Abby, Bertrand Néron
    Copyright © 2014-2025 Institut Pasteur (Paris) and CNRS.
    See the COPYRIGHT file for details
    MacsyLib is distributed under the terms of the GNU General Public License (GPLv3).
    See the COPYING file for details.

.. _database:

********
database
********

The "database" object handles the indexes of the sequence dataset in fasta format,
and other useful information on the input dataset.

MacSyLib needs to have the length of each sequence and its position in the database
to compute some statistics on Hmmer hits.
Additionally, for ordered datasets ( db_type = 'gembase' or 'ordered_replicon' ),
MacSyLib builds an internal "database" from these indexes to store information about replicons,
their begin and end positions, and their topology.

The begin and end positions of each replicon are computed from the sequence file,
and the topology from the parsing of the topology file (see :ref:`topology-files`).

Thus it also builds an index (with *.idx* suffix) that is stored in the same directory as the sequence dataset.
If this file is found in the same folder than the input dataset, MacSyLib will use it. Otherwise, it will build it.


.. _database_api:

database API reference
======================

Indexes
=======
.. autoclass:: macsylib.database.Indexes
   :members:
   :private-members:
   :special-members:


RepliconInfo
============
.. automodule:: macsylib.database
   :members: RepliconInfo


RepliconDB
==========
.. autoclass:: macsylib.database.RepliconDB
   :members:
   :private-members:
   :special-members:


fasta_iter
==========
.. autofunction:: macsylib.database.fasta_iter
