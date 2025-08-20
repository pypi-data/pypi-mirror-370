.. MacSyLib - python library that provide functions for
   detection of macromolecular systems in protein datasets
   using systems modelling and similarity search.
   Authors: Sophie Abby, Bertrand Néron
   Copyright © 2014-2025 Institut Pasteur (Paris) and CNRS.
   See the COPYRIGHT file for details
   MacSyLib is distributed under the terms of the GNU General Public License (GPLv3).
   See the COPYING file for details.

.. _overview:

MacSyLib implementation overview
================================

MacSyLib is implemented with an object-oriented architecture.
Below a short glossary to fix the vocabulary used in MacSylib.

.. glossary::
    :sorted:

    Model family
        A set of models, on the same topic.
        It is composed of several definitions which can be sorted in hierachical structure
        and profiles. A profile is a hmm profile file.

    Model
        Is a formal description of a macromolecular system.
        Is composed of a definition and a list of profiles.
        at each gene of the Model must correspond a profile

    ModelDefinition
        Is a definition of model, it's serialize as a xml file

    Cluster
        Is a "contiguous" set of hits.
        two hits are considered contiguous if the number of genes between the 2 genes matching the 2 hits
        in the replicon is lesser than inter-genes-max-space.

    System
        It's an occurrence of a specific Model on a replicon.
        Basically, it's a cluster or set of clusters which satisfy the Model quorum.

    Solution
        It's a systems combination for one replicon.
        The best solution for a replicon, is the combination of all systems found in this replicon which
        maximize the score.


MacSyLib project structure
-----------------------------

A brief overview of the files and directory constituting the MacSylib project.

.. glossary::

    doc
        The project is documented using sphinx.
        All sources files needed to generate this documentation is in the directory *doc*

    macsylib
        This the MacSyLib python library
        Inside macsypy there is a subdirectory *scripts* which are the entry points for
        `macsyprofile` (tool to help modeler to analyse *hmmsearch* output) and `macsydata` (tool to install models)

    tests
        The code is tested using `unittests`.
        In *tests* the directory *data* contains all data needed to perform the tests.

    CONTRIBUTORS
        A file containing the list of code contributors.

    CONTRIBUTING
        A guide on how to contribute to the project.

    COPYRIGHT
        The MacSyLib copyrights.

    COPYING
        The licencing.
        MacSyLib is released under GPLv3.

    README.md
        Brief information about the project.

    setup.py
        The installation recipe.

    pyproject.toml
        The project information and installation recipe.

    codemeta.json
         metadata on this project. (https://codemeta.github.io/)



MacSyLib architecture overview
---------------------------------

An overview of the main classes.


.. figure:: ../_static/macsylib_classes.*

    The MacSyLib classes diagram.
    The classes are not details. only the main attributes allowing us to understand the interaction are mentioned.

    * in green the modules
    * in orange, the concrete class
    * in red the abstract classes
    * in blue the enumeration
    * in purple the dataclass
    * in purple/pink functions

.. note::
    use *view image* of your browser to  zoom in the diagram



search_system functioning overview
-----------------------------------
In this section I'll give you an idea of the :func:`macsylib.search_systems.search_systems` functioning
at very high grain coarse.

The higher level function is :func:`macsylib.search_systems.search_systems`.
But to call this function you have to create a :class:`macsylib.config.Config` object (:ref:`configuration`)
and also initialize the logger.

The first `search_systems` task is to create models asked by the user.
So a :class:`macsylib.definition_parser.DefinitionParser` is instantiated and the :class:`macsylib.model.ModelBank`
and :class:`macsylib.gene.GeneBank` are populated.

Once all models are created, we gather all genes and search them in the replicons.
This step is done in parallel.
The search is done by profile object associated to each gene and rely on the external software *hmmsearch*.
The parallelization is ensure by search_genes function
The results of this step is a list of hits.

This list is sorted by position and score.
this list is filtered to keep only one hit for each position,
the one with the best score (position is a gene product in a replicon)

For each model asked by the user, we filter the hits list to keep only those related to the model.
Those which are link to `mandatory`, `accessory`, `neutral` or `forbidden` genes included the exchangeables.

This hits are clustered based on distance constraints describe in the models:

    * **inter_gene_max_space** : the maximum genes allowed between to genes of a system.
    * **loner** : allow a gene to participate to system even if it does not clusterize with some other genes.

Then we check if each cluster satisfy the quorum described in the model.

    * **min_mandatory_genes** : the minimum of mandatory genes requisite to have a system.
    * **min_genes_required** : the minimum of genes (mandatory + accessory) requisite to have a system.
    * **forbidden_genes** : no forbidden genes may appear in the cluster.

If the model is *multi_loci* we generate a combination of the clusters and check the quorum for each combination.
If the cluster or combination satisfy the quorum a :class:`macsypy.systems.System` is created otherwise a
:class:`macsypy.cluster.RejectedCandidate`.

The Systems from the same replicon are sort against their position, score.

.. note::
    The *neutral* genes are used to build clusters. But not to fulfill the quorum.

Among all this potential systems, MSL (MacSyLib' compute the best combination. :func:`macsylib.solution.find_best_solutions`.
The best combination is the set of compatible systems (do not share common hits) which maximize the score.
It's possible to have several equivalent "best solutions".
The results of this step is reported in the `best_systems.tsv` file.


.. _system-implementation:

****************
The Model object
****************

The :ref:`Model object <model>` represents a macromolecular model to detect.
It is defined *via* a definition file in XML stored in a dedicated location that can be specified *via*
the :class:`macsylib.config.Config` object.
See :ref:`model-definition-grammar-label` for more details on the XML grammar.

An object :ref:`ModelDefinitionParser <definition_parser>` is used to build a model object from its XML definition file.

A model is named after the file tree name of its XML definition.
A model has an attribute `inter_gene_max_space` which is an integer,
and four kind of components are listed in function of their presence in the system:

* The genes that must be present in the genome to define this model ("mandatory").
* The genes that can be present, but do not have to be found in every case ("accessory").
* The genes that are used to build clusters, but not take in account to check the quorum
  (``min-genes-required`` and ``min-mandatory-genes-required``) are described as "neutral".
* The genes that must not be present in the system ("forbidden").

.. note::

    A complete description of macromolecular models modelling is available in the section :ref:`model_definition`


.. _gene-implementation:

***************
The Gene object
***************

The :ref:`Gene object <gene>` represents genes encoding the protein components of a Model.
There is 2 kind of gene The ``CoreGene`` (:class:`macsylib.gene.CoreGene`) which must be unique given a name.
A ``CoreGene`` must have a corresponding HMM protein profile.
These profiles are represented by Profile objects (:class:`macsylib.profile.Profile`),
and must be named after the gene name. For instance, the gene *gspD* will correspond to the "gspD.hmm" profile file.
See :ref:`profile-implementation`). After *hmmsearch* step the hits are link the them.
The :class:`macsylib.gene.CoreGene` objects must be created by using the :class:`macsylib.gene.GeneBank` factory.


A ``ModelGene`` (:class:`macsylib.gene.ModelGene`) which encapsulate a CoreGene and is linked to a Model.
Instead ``CoreGene``, several ``ModelGene`` with the same name may coexists in one macsylib run,
in different Models and hold different values for attributes as *inter_gene_max_space*, ...
Each ModelGene points out its Model of origin (:class:`macsylib.model.Model`).
A Gene has several properties described in the :ref:`Gene API <gene>`.

A ModelGene may be functionally replaced by an other (usually Homologs or Analogs).
In this case these genes are described as exchangeables.
Exchangeable object encapsulates a ModelGene and has a reference to the ModelGene it is exchangeable to.
See the :ref:`Exchangeable API <exchangeable_api>` for more details.

.. warning::
    To optimize computation and to avoid concurrency problems when we search several Models,
    each CoreGene must be instantiated only once, and stored in a *"gene_bank"*.
    gene_bank is a :class:`macsylib.gene.GeneBank` object.
    The *gene_bank* and *model_bank* are filled by the *system_parser* (:class:`macsylib.definition_parser.ModelDefinitionParser`)


.. _profile-implementation:

******************
The Profile object
******************

Each *"CoreGene"* component corresponds to a *"Profile"*.
The :class:`macsylib.profile.Profile` object is used for the search of the gene with *Hmmer*.
Thus, a *"Profile"* must match a HMM file, which name is based on the profile name.
For instance, the *gspG* gene has the corresponding "gspG.hmm" profile file provided at a dedicated location.


.. _report-implementation:

******************************
Reporting Hmmer search results
******************************

A *"HMMReport"* (:class:`macsylib.report.HMMReport`) object represents the results of a Hmmer program search on
the input dataset with a hidden Markov model protein profile.
This object has methods to extract and build *"Hits"* that are then analyzed for systems assessment.

It analyses Hmmer raw outputs, and applies filters on the matches (according to :ref:`Hmmer options<hmmer-options>`).
See :ref:`hmmer-outputs-label` for details on the resulting output files.
For profile matches selected with the filtering parameters, *"Hit"* objects are built (see :ref:`the Hit API <hit>`).

.. only:: html

    tests coverage
    --------------

    `macsylib coverage <http://gem.pages.pasteur.fr/macsylib/coverage>`_
