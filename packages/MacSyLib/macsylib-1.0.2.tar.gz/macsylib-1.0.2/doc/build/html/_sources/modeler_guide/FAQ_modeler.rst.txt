.. MacSyLib - python library that provide functions for
   detection of macromolecular systems in protein datasets
   using systems modelling and similarity search.
   Authors: Sophie Abby, Bertrand Néron
   Copyright © 2014-2025 Institut Pasteur (Paris) and CNRS.
   See the COPYRIGHT file for details
   MacSyLib is distributed under the terms of the GNU General Public License (GPLv3).
   See the COPYING file for details.

.. _FAQ_model:


**************************
Frequently Asked Questions
**************************

How to report an issue?
-----------------------

If you encounter a problem while running MacSyLibr, please submit an issue on the dedicated page of the `GitHub project <https://github.com/gem-pasteur/macsylib/issues>`_

To ensure we have all elements to help, please provide:

- a concise description of the issue
- the expected behavior VS observed one
- the exact command-line used
- the version of MacSyLib used
- the exact error message, and if applicable, the `macsylib.log` and `macsylib.conf` files
- if applicable, an archive (or link to it) with the output files obtained
- if possible, the smallest dataset there is to reproduce the issue
- if applicable, this would also include the macsy-models (XML models plus HMM profiles) used
  (or precise version of the models if there are publicly available).
  Same as above, if possible, please provide the smallest set possible of models and HMM profiles.

All these will definitely help us to help you! ;-)


How to list several components or HMM profiles for a given function in the model?
---------------------------------------------------------------------------------

MacSyLib provides a framework to associate a component/function in the model of a system with the mean to search for it - a HMM profile.

In some cases, it is needed to list several possible components (i.e. HMM profiles) to assume a given function for the system to model.
There can be several reasons for that:

 - a biological reason (e.g., two components from two different gene families can assume a same role in the system)
 - a methodological reason (it is not possible or difficult to provide a single HMM profile
   that covers the diversity of the components' sequences to be retrieved).

It is possible to list several possible components for a same role within the system's model using the `exchangeables` keyword.

See :ref:`here<exchangeables_label>` for more details and examples.
