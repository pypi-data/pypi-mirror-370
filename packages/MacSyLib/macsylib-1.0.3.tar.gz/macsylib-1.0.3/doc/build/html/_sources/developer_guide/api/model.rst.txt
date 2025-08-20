.. MacSyLib - python library that provide functions for
    detection of macromolecular systems in protein datasets
    using systems modelling and similarity search.
    Authors: Sophie Abby, Bertrand Néron
    Copyright © 2014-2025 Institut Pasteur (Paris) and CNRS.
    See the COPYRIGHT file for details
    MacsyLib is distributed under the terms of the GNU General Public License (GPLv3).
    See the COPYING file for details.

.. _model:


*****
model
*****

The model is a formal representation of system.
The model is describe in terms of components.
There are 4 component classes:

    * genes which are mandatory
    * genes which are accessory
    * genes which are neutral
    * genes which are forbidden

Each genes can have Exchangeable.
An exchangeable is another gene which can paly the same role in the system. Usually an analog or homolog.
The models describe also distance constraints between genes:

    * inter_gene_max_space
    * loner
    * multi_loci

and quorum constraints

    * min_mandatory_genes_required
    * min_genes_required

and if a gene can be shared by several systems (several occurrences of the same model)

    * multisystem

.. _model_api:

model API reference
===================

ModelBank
=========
 .. autoclass:: macsylib.model.ModelBank
   :members:
   :private-members:
   :special-members:


Model
=====

.. autoclass:: macsylib.model.Model
   :members:
   :private-members:
   :special-members:
