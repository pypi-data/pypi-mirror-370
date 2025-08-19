.. MacSyLib - python library that provide functions for
   detection of macromolecular systems in protein datasets
   using systems modelling and similarity search.
   Authors: Sophie Abby, Bertrand Néron
   Copyright © 2014-2025 Institut Pasteur (Paris) and CNRS.
   See the COPYRIGHT file for details
   MacsyLib is distributed under the terms of the GNU General Public License (GPLv3).
   See the COPYING file for details.

.. _hit:


***
hit
***

This module implements class relative to hit and some functions to do some computation on hit objects.

============================================ =============================================================================
:class:`macsylib.hit.CoreHit`                Modelize a hmm hit on the replicon. There is only one Corehit for a CoreGene.
:class:`macsylib.hit.ModelHit`               Modelize a hit and its relation to the Model.
:class:`macsylib.hit.AbstractCounterpartHit` Parent class of Loner, MultiSystem. It's inherits from ModelHit.
:class:`macsylib.hit.Loner`                  Modelize "true" Loner.
:class:`macsylib.hit.MultiSystem`            Modelize hit which can be used in several Systems (same model)
:class:`macsylib.hit.LonerMultiSystem`       Modelize a hit representing a gene Loner and MultiSystem at same time.
:class:`macsylib.hit.HitWeight`              The weights apply to the hit to compute score
:func:`macsylib.hit.get_best_hit_4_func`     Return the best hit for a given function
:func:`macsylib.hit.sort_model_hits`         Sort hits
:func:`macsylib.hit.compute_best_MSHit`      Choose among svereal multisystem hits the best one
:func:`macsylib.hit.get_best_hits`           If several profile hit the same gene return the best hit
============================================ =============================================================================

A Hit is created when `hmmsearch` find similarities between a profile and protein of the input dataset

Below the ingheritance diagram of Hits

.. inheritance-diagram::
      macsylib.hit.CoreHit
      macsylib.hit.ModelHit
      macsylib.hit.AbstractCounterpartHit
      macsylib.hit.Loner
      macsylib.hit.MultiSystem
      macsylib.hit.LonerMultiSystem
   :parts: 1


And a diagram showing the interaction between CoreGene, ModelGene, Model, Hit, Loner, ... interactions

.. figure:: ../../_static/gene_obj_interaction.*


    The diagram above represents the models, genes and hit generated from the definitions below.

    .. code-block::

        <model name="A" inter_gene_max_space="2">
            <gene name="abc" presence="mandatory"/>
            <gene name="def" presence="accessory"/>
        </model>

        <model name="B" inter_gene_max_space="5">
            <gene name="def" presence="mandatory"/>
                <exchangeables>
                    <gene name="abc"/>
                </exchangeables>
            <gene name="ghj" presence="accessory"
        </model>





.. _hit_api:

hit API reference
=================

CoreHit
=======
.. autoclass:: macsylib.hit.CoreHit
   :members:
   :private-members:
   :special-members:

ModelHit
========
.. autoclass:: macsylib.hit.ModelHit
   :members:
   :private-members:
   :special-members:

AbstractCounterpartHit
======================
.. autoclass:: macsylib.hit.AbstractCounterpartHit
   :members:
   :private-members:
   :special-members:

Loner
=====
.. autoclass:: macsylib.hit.Loner
   :members:
   :private-members:
   :special-members:

MultiSystem
===========
.. autoclass:: macsylib.hit.MultiSystem
   :members:
   :private-members:
   :special-members:

LonerMultiSystem
================
.. autoclass:: macsylib.hit.LonerMultiSystem
   :members:
   :private-members:
   :special-members:

HitWeight
=========
.. autoclass:: macsylib.hit.HitWeight
   :members:
   :private-members:
   :special-members:

get_best_hit_4_func
===================
.. autofunction:: macsylib.hit.get_best_hit_4_func

sort_model_hits
===============
.. autofunction:: macsylib.hit.sort_model_hits

compute_best_MSHit
==================
.. autofunction:: macsylib.hit.compute_best_MSHit

get_best_hits
=============
.. autofunction:: macsylib.hit.get_best_hits
