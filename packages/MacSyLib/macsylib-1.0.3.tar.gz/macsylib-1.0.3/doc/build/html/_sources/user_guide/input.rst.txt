.. MacSyLib - python library that provide functions for
    detection of macromolecular systems in protein datasets
    using systems modelling and similarity search.
    Authors: Sophie Abby, Bertrand Néron
    Copyright © 2014-2025 Institut Pasteur (Paris) and CNRS.
    See the COPYRIGHT file for details
    MacsyLib is distributed under the terms of the GNU General Public License (GPLv3).
    See the COPYING file for details.


.. _input:

*****************************
Input and Options of MacSyLib
*****************************


.. _input-dataset-label:

Input dataset
=============

The input dataset must be a set of protein sequences in **Fasta format** (see http://en.wikipedia.org/wiki/FASTA_format).
(The fasta file can be compressed in *gzip* format see note below)


The :ref:`base section<config-base-label>` in the configuration file (see :ref:`config-definition-label`)
can be used to specify **the path** and the **type of dataset** to deal with,
as well as the `sequence_db` and `db_type` config options respectively,
described in the :ref:`input_options`.

  Four types of protein datasets are supported:

        * *unordered* : a set of sequences corresponding to a complete genome
          (*e.g.* an unassembled complete genome)
        * *ordered_replicon* : a set of sequences corresponding to an ordered complete replicon
          (*e.g.* an assembled complete genome)
        * *gembase* : a set of multiple ordered replicons, which format follows the convention described
          in :ref:`gembase_convention`.

For "ordered" ("ordered_replicon" or "gembase") datasets only,
MacSyLib can take into account the **shape of the genome**: "linear",
or "circular" for detection. The default is set to "circular".

  This can be set with the `replicon_topology` parameter from :ref:`input_options`
  or in the configuration in the :ref:`base section<config-base-label>`.

  With the "gembase" format, it is possible to specify a topology per replicon with a topology file
  (see :ref:`gembase_convention` and :ref:`topology-files`).

.. note::

    MSL can also read *.gz* compressed files; it will uncompress them on the fly.
    The compressed files must end with the *.gz* extension.
    For the `hmmsearch` step You need to have `gunzip` installed on your system for this to work.


.. _config_object_parameters:

Config object
=============

Config object take 2 parameters:

 1. some default values stored in MacSyDefault (these to class are located in config module)
 2. and a set of parameters store in an :class:`argparse.Namespace` object

for instance to set up macsylib

.. code-block:: python

    from argparse import Namespace
    import macsylib.condig

    defaults = macsylib.config.MacsyDefaults()
    settings = Namespace(
        db_type='ordered_replicon',
        sequence_db='test.fasta',
        models=['TXSScan', 'all'],  # this model must be installed with msl_data scripts
        worker=4,
    )

The config options available are:

.. _input_options:

Input options
-------------

models
    The models to search. A list, where the first element must be the name of family models, followed by the name of the models.
    If the name 'all' is in the list all models from the family will be searched.'

    * :code:`['TXSScan', 'all']` to search all models in TXSScan.
    * :code:`['TXSScan/bacteria', 'all']` or :code:`['TXSScan', 'bacteria/all']` to search all models in bacteria.
    * :code:`['TXSScan/bacteria/diderm', 'T4aP', 'T4bP']` to search only 'T4ap' and 'T4bP' models.

sequence_db
    Path to the sequence dataset in fasta format.

db_type
    The type of dataset to deal with.

        * `"unordered"*` corresponds to a non-assembled genome,
        * `"ordered_replicon"` to an assembled genome, where sequence appear in the file as the same order as in the genome.
          (be careful the *GCF* files from the *NCBI*, most of the time, do not follow the order of the associated *gff*
        * and `"gembase"` to a set of replicons see :ref:`gembase_convention`.

replicon_topology
    `circular` or `linear`
    The topology of the replicons (this option is meaningful only if the db_type is 'ordered_replicon' or 'gembase')

topology_file
    Topology file path. The topology file allows to specify a topology (linear or circular)
    for each replicon (this option is meaningful only if the db_type is 'ordered_replicon' or 'gembase'.
    A topology file is a tabular file with two columns:

    the 1st is the replicon name, and the 2nd the corresponding topology:

    :code:`RepliconA      linear`

idx
    `True` / `False`
    Forces to build the indexes for the sequence dataset even if they were previously computed and present at the dataset location.
    (default: False)

.. _system-detect-options:

Systems detection options
-------------------------

inter_gene_max_space
    Co-localization criterion: maximum number of components non-matched by a profile allowed between two matched components
    for them to be considered contiguous.
    Option only meaningful for 'ordered' datasets.
    This option must be provide as list of tuple.
    The tuple first value must match to a model, the second to a number of components.

    :code:`inter_gene_max_space=[('TXSScan/bacteria/diderm/T2SS', 12), ('TXSScan/bacteria/diderm/Flagellum', 14)],`

min_mandatory_genes_required
    The minimal number of mandatory genes required for model assessment.
    This option must be provide as list of tuple.
    The first value must correspond to a model fully qualified name, the second value to an integer.

min_genes_required
    The minimal number of genes required for model assessment
    (includes both 'mandatory' and 'accessory' components).
    The first value must correspond to a model fully qualified name, the second value to an integer.

:code:`min_genes_required=[('TXSScan/bacteria/diderm/T2SS', 5), ('TXSScan/bacteria/diderm/Flagellum', 4)],`


max-nb-genes
    The maximal number of genes to consider a system as full.
    The first value must correspond to a model name, the second value to an integer.

multi-loci
    Specifies if the system can be detected as a 'scattered' system.
    The models are specified as a comma separated list of fully qualified name
    :code:`['TXSScan/bacteria/diderm/T2SS', ''TXSScan/bacteria/diderm/Flagellum'']`


.. _hmmer-options:

Options for Hmmer execution and hits filtering:
-----------------------------------------------

hmmer
    Path to the hmmsearch program. If it is not specify rely on the PATH. (default: hmmsearch)

e_value_search
    Maximal e-value for hits to be reported during hmmsearch search.
    By default MF set per profile threshold for hmmsearch run (cut_ga option)
    for profiles containing the GA bit score threshold.
    If a profile does not contains the GA bit score the e_value_search (-E in hmmsearch)
    is applied to this profile.
    To applied the e_value_search to all profiles use the no_cut_ga option.
    (default: 0.1)

no_cut_ga
    By default the MSL try to applied a threshold per profile by using the hmmer -cut-ga option.
    This is possible only if the GA bit score is present in the profile otherwise MSL switch to use the
    e_value_search (-E in hmmsearch).
    If this option is set the e_value_search option is used for all profiles regardless the presence of
    the a GA bit score in the profiles.
    (default: False)

cut_ga
    By default the MSL try to applied a threshold per profile by using the hmmer cut_ga option.
    This is possible only if the GA bit score is present in the profile otherwise
    MSF switch to use the --e-value-search (-E in hmmsearch).
    But the modeler can override this default behavior to do not use cut_ga but e_value_search instead (-E in hmmsearch).
    The user can reestablish the general MSL behavior, be sure the profiles contain the GA bit score.
    (default: True)

i_evalue_sel
    Maximal independent e-value for Hmmer hits to be selected for system detection. (default:0.001)

overage_profile
    Minimal profile coverage required in the hit alignment to allow the hit selection for system detection. (default: 0.5)

.. _score-options:

Options for clusters and systems' scoring:
------------------------------------------

mandatory_weight
    the weight (score) of a mandatory component when scoring clusters (default:1.0)

accessory_weight
    the weight (score) of an accessory component when scoring clusters (default:0.5)

exchangeable_weight
    the weight modifier for the score of a component that is exchangeable (default:0.8)

redundancy_penalty
    the weight modifier for the score of a component that is already present in another cluster

loner_multi_system_weight
    the weight modifier for the score of a component that is `loner` and `multi-system` at the same time (default:0.7)

.. _path-options:

Path options:
-------------

models_dir
    specify the path to the models if the models are not installed in the canonical place.
    It gather definitions (xml files) and hmm profiles in a specific
    structure. A directory with the name of the model with at least two directories
    profiles" which contains all hmm profile for gene describe in definitions and
    models" which contains either xml file of definitions or subdirectories
    to organize the model in subsystems.

out_dir
    Path to the directory where to store results. if out-dir is specified res-search-dir will be ignored.
    You have to create it.

force
    force to run even the out dir already exists and is not empty.
    Use this option with caution, MSF will erase everything in out dir before to run. (default= False)

index_dir
    Specifies the path to a directory to store/read the sequence index when the sequence_db dir is not writable.


res_search_suffix
    The suffix to give to Hmmer raw output files. (default: .search_hmm.out)

res_extract_suffix
    The suffix to give to filtered hits output files. (default: .res_hmm_extract)

profile_suffix
    The suffix of profile files. For each 'Gene' element, the corresponding profile is searched in the 'profile_dir',
    in a file which name is based on the Gene name + the profile suffix.
    For instance, if the Gene is named 'gspG' and the suffix is '.hmm3', then the profile should be placed at the specified location
    and be named 'gspG.hmm3' (default: .hmm)

.. _general-options:

General options:
----------------

worker
    Number of workers to be used by MacSylib. In the case the user wants to run MacSyFLib in a multi-thread mode.
    (0 mean all threads available will be used (compliant with use of cluster scheduler)). (default: 1)

verbosity
    Increases the verbosity level. T
    here are 4 levels: Error messages (default), Warning (-v), Info (-vv) and Debug.(-vvv)

mute
    mute the log on stdout.
    (continue to log on macsylib.log)
    (default: False)

cfg_file
    Path to a MacSyLib configuration file to be used.

previous_run
    Path to a previous MacSyLib run directory.
    It allows to skip the Hmmer search step on same dataset,
    as it uses previous run results and thus parameters regarding Hmmer detection.
    The configuration file from this previous run will be used.
    Conflict with options: `config`, `sequence_db`, `profile_suffix`, `res_extract_suffix`, `e_value_res`, `db_type`, `hmmer`

timeout
    In some case msf can take a long time to find the best solution (in 'gembase' and 'ordered_replicon mode').
    The timeout is per replicon. If this step reach the timeout, the replicon is skipped (for gembase mode the analyse of other replicons continue).
    NUMBER[SUFFIX]  NUMBER seconds. SUFFIX may be 's' for seconds (the default), 'm' for minutes, 'h' for hours or 'd' for days
    for instance 1h2m3s means 1 hour 2 min 3 sec. NUMBER must be an integer.

.. _config-definition-label:

Configuration file
==================

Options to run MacSyLib can be specified in a configuration file.

The :ref:`Config object <configuration>` handles all configuration options for MacSylib.
There kind of locations where to put configuration file:

 #. System wide configuration (this configuration is used for all macsylib run)

    * */etc/macsylib/macsylib.conf*
    * or in *${VIRTUAL_ENV}/etc/macsylib.conf* if you installed macsylib in a virtualenv
    * the file pointed by environment variable *MACSY_HOME*

 #. User wide configuration (this configuration is used for all run for a user)

    * *~/.macsylib/macsylib.conf*

 #. Project configuration

    * *macsylib.conf* in the current directory
    * with command line option *--cfg-file*


.. note::
    The precedence rules from the least to the most important priority are:

    System wide configuration < user wide configuration < project configuration < command line option

This means that command-line options will always bypass those from the configuration files. In the same flavor,
options altering the definition of systems found in the command-line or the configuration file will always
overwhelm values from systems' :ref:`XML definition files <model-definition-grammar-label>`.

The configuration files must follow the Python "ini" file syntax.
The :ref:`Config object <configuration>` provides some default values and performs some validations of the values.


In MacSyLib, six sections are defined and stored by default in the configuration file:

 .. _config-base-label:

  * **base** : all information related to the protein dataset under study

    * *sequence_db* : the path to the dataset in Fasta format (*no default value*)
    * *db_type* : the type of dataset to handle, four types are supported:

        * *unordered* : a set of sequences corresponding to a complete replicon
          (*e.g.* an unassembled complete genome)
        * *ordered_replicon* : a set of sequences corresponding to a complete replicon ordered
          (*e.g.* an assembled complete genome)
        * *gembase* : a set of multiple ordered replicons.

      (*no default value*)

    * *replicon_topology* : the topology of the replicon under study.
      Two topologies are supported: 'linear' and 'circular' (*default* = 'circular').
      This option will be ignored if the dataset type is not ordered (*i.e.* "unordered_replicon" or "unordered").

  * **models**
    * list of models to search in replicon

  * **models_opt**

    * *inter_gene_max_space* = list of models' fully qualified names and integer separated by spaces (see example below).
      These values will supersede the values found in the model definition file.
    * *min_mandatory_genes_required* = list of models' fully qualified name and integer separated by spaces.
      These values will supersede the values found in the model definition file.
    * *min_genes_required* = list of models' fully qualified name and integer separated by spaces.
      These values will supersede the values found in the model definition file.
    * *max_nb_genes* = list of models' fully qualified names and integer separated by spaces.
      These values will supersede the values found in the model definition file.

  * **hmmer**

    * *hmmer_exe* (default= *hmmsearch* )
    * *e_value_res* = (default= *1* )
    * *i_evalue_sel* = (default= *0.5* )
    * *coverage_profile* = (default= *0.5* )

  * **score_opt**

    * *mandatory_weight* (default= *1.0*)
    * *accessory_weight* (default= *0.5*)
    * *exchangeable_weight* (default= *0.8*)
    * *redundancy_penalty* (default= *1.5*)
    * *out_of_cluster* (default= *0.7*)


  * **directories**

    * *res_search_dir* = (default= *./datatest/res_search* )
    * *res_search_suffix* = (default= *.search_hmm.out* )
    * *system_models_dir* = (default= *./models* )
    * *res_extract_suffix* = (default= *.res_hmm_extract* )
    * *index_dir* = (default= beside the sequence_db)

  * **general**

    * *log_level*: (default= *debug* ) This corresponds to an integer code:
        ========    ==========
        Level 	    Numeric value
        ========    ==========
        CRITICAL 	50
        ERROR 	    40
        WARNING 	30
        INFO 	    20
        DEBUG 	    10
        NOTSET 	    0
        ========    ==========
    * *log_file* = (default = macsylib.log in directory of the run)

Example of a configuration file

.. code-block:: ini

    [base]
    prefix = /path/to/macsylib/home/
    file = %(prefix)s/data/base/prru_psae.001.c01.fasta
    db_type = gembase
    replicon_topology = circular

    [models]
    models_1 = TFF-SF_final all

    [models_opt]
    inter_gene_max_space = TXSS/T2SS 22 TXSS/Flagellum 44
    min_mandatory_genes_required = TXSS/T2SS 6 TXSS/Flagellum 4
    min_genes_required = TXSS/T2SS 8 TXSS/Flagellum 4
    max_nb_genes = TXSS/T2SS 12 TXSS/Flagellum 8

    [hmmer]
    hmmer = hmmsearch
    e_value_res = 1
    i_evalue_sel = 0.5
    coverage_profile = 0.5

    [score_opt]
    mandatory_weight = 1.0
    accessory_weight = 0.5
    exchangeable_weight = 0.8
    redundancy_penalty = 1.5
    loner_multi_system_weight = 0.7

    [directories]
    prefix = /path/to/macsylib/home/
    data_dir = %(prefix)s/data/
    res_search_dir = %(prefix)s/dataset/res_search/
    res_search_suffix = .raw_hmm
    system_models_dir = %(data_dir)/data/models, ~/.macsylib/data
    profile_suffix = .fasta-aln.hmm
    res_extract_suffix = .res_hmm
    index_dir = path/where/I/store/my_indexes

   [general]
   log_level = debug
   worker = 4

.. note::

    After a run, the corresponding configuration file ("macsylib.conf") is generated as a (re-usable)
    output file that stores every options used in the run.
    It is stored in the results' directory (see :ref:`the output section <outputs>`).

.. warning::

    The configuration variable `models_dir` cannot be set in general configuration file.
    `models_dir`` can be set only in configuration under user control.
    ```$(HOME)/.macsylib/macsylib.conf < macsylib.conf < "command-line" options```
    `models_dir` is a single path to a directory whre masyfinder can find models.

    But the `system_models_dir` can be set in general configuration file

    * /etc/macsylib/macsylib.conf
    * or ${VIRTUAL_ENV}/etc/macsylib/macsylib.conf
    * or anywhere point by $MACSY_CONF environment variable

    `system_models_dir` manage a list of locations where macsylib can find models.
    The order of locations is important, it reflects the precedence rule (The models found in last location
    superseed models found in previous location).
    By default look for following directories: */share/macsylib/models*, or */usr/share/macsylib/models*
    and *$HOME/.macsylib/models* and `system_models_dir` uses these directories if they exists.


In-house input files
====================
.. toctree::
   :maxdepth: 1

   gembase_convention
