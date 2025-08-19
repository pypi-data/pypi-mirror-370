.. MacSyLib - python library that provide functions for
   detection of macromolecular systems in protein datasets
   using systems modelling and similarity search.
   Authors: Sophie Abby, Bertrand Néron
   Copyright © 2014-2025 Institut Pasteur (Paris) and CNRS.
   See the COPYRIGHT file for details
   MacSyLib is distributed under the terms of the GNU General Public License (GPLv3).
   See the COPYING file for details.


.. _quickstart:


MacSyLib Quick Start
====================
..
    This block is commented (does not appear in compile version)
    .. only:: html

        .. figure:: ../_static/under_construction.gif

            This page is still under construction

    .. only:: latex

        .. figure:: ../_static/under_construction.jpeg

            This page is still under construction


1. We recommend to install MacSylib using `pip` in a virtual environment (for further details see :ref:`user_installation`).

   .. code-block:: bash

        python3 -m venv MacSyLib
        cd MacSyLib
        source bin/activate
        pip install macsylib

   .. warning::

        `hmmsearch` from the HMMER package (http://hmmer.org/) must be installed.

2. Prepare your data. You need a file containing all protein sequences of your genome of interest in a FASTA file
   (for further details see :ref:`input-dataset-label`). In the best case scenario, they would be ordered as the
   corresponding genes are ordered along the replicons.

3. You need to install, or make available to MacSyLib the models to search in your input genome data.
   Please refer to :ref:`model_definition` to create your own package of models.
   Otherwise, macsy-models contributed by the community are available here: https://github.com/macsy-models
   and can be retrieved and installed using the :ref:`msl_data <msl_data>` command, installed as part of the MacSylib suite.

4. Install the macsy-models of interest from the `Macsy Models repository <https://github.com/macsy-models>`_:

      :code:`msl_data available`

      :code:`msl_data install some-public-models`

5. Use MacSylib :ref:`python-example`