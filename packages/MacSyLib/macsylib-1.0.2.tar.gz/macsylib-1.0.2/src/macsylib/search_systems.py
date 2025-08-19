#########################################################################
# MacSyLib - Python library to detect macromolecular systems            #
#            in prokaryotes protein dataset using systems modelling     #
#            and similarity search.                                     #
#                                                                       #
# Authors: Sophie Abby, Bertrand Neron                                  #
# Copyright (c) 2014-2025  Institut Pasteur (Paris) and CNRS.           #
# See the COPYRIGHT file for details                                    #
#                                                                       #
# This file is part of MacSyLib package.                                #
#                                                                       #
# MacSyLib is free software: you can redistribute it and/or modify      #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 3 of the License, or     #
# (at your option) any later version.                                   #
#                                                                       #
# MacSyLib is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          #
# GNU General Public License for more details .                         #
#                                                                       #
# You should have received a copy of the GNU General Public License     #
# along with MacSyLib (COPYING).                                        #
# If not, see <https://www.gnu.org/licenses/>.                          #
#########################################################################

"""
MacSyLib high level functions search systems in ordered and non-ordered replicons
"""
import os
import logging
from collections import defaultdict

from operator import attrgetter  # To be used with "sorted"
import colorlog

import macsylib
from macsylib.config import Config
from macsylib.cluster import Cluster
from macsylib.registries import ModelRegistry, DefinitionLocation
from macsylib.definition_parser import DefinitionParser
from macsylib.search_genes import search_genes
from macsylib.database import Indexes, RepliconDB
from macsylib import cluster
from macsylib.hit import get_best_hits, HitWeight, MultiSystem, LonerMultiSystem, \
    sort_model_hits, compute_best_MSHit
from macsylib.system import OrderedMatchMaker, UnorderedMatchMaker, System, LikelySystem, UnlikelySystem, RejectedCandidate
from macsylib.profile import ProfileFactory
from macsylib.model import ModelBank
from macsylib.gene import GeneBank
from macsylib.solution import combine_clusters, combine_multisystems


_log = colorlog.getLogger(__name__)


def search_systems(config: Config,
                   model_registry: ModelRegistry,
                   models_def_to_detect: list[DefinitionLocation],
                   logger: logging.Logger) -> tuple[list[System], list[RejectedCandidate]] | tuple[list[LikelySystem], list[UnlikelySystem]]:
    """
    Do the job, this function is the orchestrator of all the macromolecular mechanics
    at the end several files are produced containing the results

      - <macsylib>.conf: The set of variables used to runt this job
      - <macsylib>.systems: The list of the potential systems
      - <macsylib>.rejected_cluster: The list of all clusters and clusters combination
                                      which has been rejected and the reason
      - <macsylib>.log: the copy of the standard output

    <macsylib> can be replaced by the program name when the macsylib is used by a higher python scripts
    (for instance macsyfinder). The program name can be set in :class:`macsylib.config.MacSyDefaults`

    :param config: The MacSyLib Configuration
    :type config: :class:`macsylib.config.Config` object
    :param model_registry: the registry of all models
    :type model_registry: :class:`macsylib.registries.ModelRegistry` object
    :param models_def_to_detect: the definitions to detect
    :type models_def_to_detect: list of :class:`macsylib.registries.DefinitionLocation` objects
    :param logger: The logger use to display information to the user.
                   It must be initialized. see :func:`macsylib.init_logger`
    :type logger: :class:`colorlog.Logger` object
    :return: the systems and rejected clusters found
    :rtype: ([:class:`macsylib.system.System`, ...], [:class:`macsylib.cluster.RejectedCandidate`, ...])
    """
    working_dir = config.working_dir()
    config.save(path_or_buf=os.path.join(working_dir, config.cfg_name))

    # build indexes
    idx = Indexes(config)
    idx.build(force=config.idx())

    # create models
    model_bank = ModelBank()
    gene_bank = GeneBank()
    profile_factory = ProfileFactory(config)

    parser = DefinitionParser(config, model_bank, gene_bank, model_registry, profile_factory)
    parser.parse(models_def_to_detect)

    logger.info(f"{config.tool_name() }'s results will be stored in working_dir{working_dir}")
    logger.info(f"Analysis launched on {config.sequence_db()} for model(s):")

    for model in models_def_to_detect:
        logger.info(f"\t- {model.fqn}")

    models_to_detect = [model_bank[model_loc.fqn] for model_loc in models_def_to_detect]
    all_genes = []
    for model in models_to_detect:
        genes = model.mandatory_genes + model.accessory_genes + model.neutral_genes + model.forbidden_genes
        # Exchangeable (formerly homologs/analogs) are also added because they can "replace" an important gene...
        ex_genes = []
        for m_gene in genes:
            ex_genes += m_gene.exchangeables
        all_genes += (genes + ex_genes)
    #############################################
    # this part of code is executed in parallel
    #############################################
    try:
        all_reports = search_genes(all_genes, config)
    except Exception as err:
        raise err
    #############################################
    # end of parallel code
    #############################################
    all_hits = [hit for subl in [report.hits for report in all_reports] for hit in subl]

    if len(all_hits) > 0:
        # It's important to keep this sorting to have in last all_hits version
        # the hits with the same replicon_name and position sorted by score
        # the best score in first
        hits_by_replicon = defaultdict(list)
        for hit in all_hits:
            hits_by_replicon[hit.replicon_name].append(hit)

        for rep_name in hits_by_replicon:
            hits_by_replicon[rep_name] = get_best_hits(hits_by_replicon[rep_name], key='score')
            hits_by_replicon[rep_name].sort(key=attrgetter('position'))

        models_to_detect = sorted(models_to_detect, key=attrgetter('name'))
        db_type = config.db_type()
        if db_type in ('ordered_replicon', 'gembase'):
            systems, rejected_candidates = search_in_ordered_replicon(hits_by_replicon, models_to_detect,
                                                                                       config, logger)
            return systems, rejected_candidates
        elif db_type == "unordered":
            likely_systems, unlikely_systems = search_in_unordered_replicon(hits_by_replicon, models_to_detect,
                                                                            logger)
            return likely_systems, unlikely_systems
        else:
            assert False, f"dbtype have an invalid value {db_type}"
    else:
        # No hits detected
        return [], []


def search_in_ordered_replicon(hits_by_replicon: dict[str: list[macsylib.hit.CoreHit]],
                                models_to_detect: list[macsylib.model.Model],
                                config: Config,
                                logger: logging.Logger) -> tuple[list[System], list[RejectedCandidate]]:
    """

    :param hits_by_replicon: the hits sort by replicon and position
    :param models_to_detect: the models to search
    :param config: MSF configuration
    :param logger: the logger
    """
    all_systems = []
    all_rejected_candidates = []
    rep_db = RepliconDB(config)

    for rep_name in hits_by_replicon:
        logger.info(f"\n{f' Hits analysis for replicon {rep_name} ':#^60}")
        rep_info = rep_db[rep_name]
        for model in models_to_detect:
            one_model_systems = []
            one_model_rejected_candidates = []
            logger.info(f"Check model {model.fqn}")
            # model.filter filter hit but also cast them in ModelHit
            mhits_related_one_model = model.filter(hits_by_replicon[rep_name])
            logger.debug(f"{f' hits related to {model.name} ':#^80}")
            hit_header_str = "id\trep_name\tpos\tseq_len\tgene_name\ti_eval\tscore\tprofile_cov\tseq_cov\tbeg_match\tend_match"
            hits_str = "".join([str(h) for h in mhits_related_one_model])
            logger.debug(f"\n{hit_header_str}\n{hits_str}")
            logger.debug("#" * 80)
            logger.info("Building clusters")
            hit_weights = HitWeight(**config.hit_weights())
            true_clusters, true_loners = cluster.build_clusters(mhits_related_one_model, rep_info, model, hit_weights)
            logger.debug(f"{' CLUSTERS ':#^80}")
            logger.debug("\n" + "\n".join([str(c) for c in true_clusters]))
            logger.debug(f"{' LONERS ':=^50}")
            logger.debug("\n" + "\n".join([str(c) for c in true_loners.values() if c.loner]))
            # logger.debug("{:=^50}".format(" MULTI-SYSTEMS hits "))
            # logger.debug("\n" + "\n".join([str(c.hits[0]) for c in special_clusters.values() if c.multi_system]))
            logger.debug("#" * 80)
            logger.info("Searching systems")
            clusters_combination = combine_clusters(true_clusters, true_loners, multi_loci=model.multi_loci)
            for one_clust_combination in clusters_combination:
                ordered_matcher = OrderedMatchMaker(model, redundancy_penalty=config.redundancy_penalty())
                res = ordered_matcher.match(one_clust_combination)
                if isinstance(res, System):
                    one_model_systems.append(res)
                else:
                    one_model_rejected_candidates.append(res)

            ###############################
            # MultiSystem Hits Management #
            ###############################
            # get multi systems from existing systems #
            hit_encondig_multisystems = set()  # for the same model (in the loop)
            for one_sys in one_model_systems:
                hit_encondig_multisystems.update(one_sys.get_hits_encoding_multisystem())

            logger.debug(f"{' MultiSystems ':#^80}")
            logger.debug("\n" + "\n".join([str(c) for c in true_clusters]))
            # Cast these hits in MultiSystem/LonerMultiSystem
            multi_systems_hits = []
            for hit in hit_encondig_multisystems:
                if not hit.loner:
                    multi_systems_hits.append(MultiSystem(hit))
                else:
                    multi_systems_hits.append(LonerMultiSystem(hit))
            # choose the best one
            ms_per_function = sort_model_hits(multi_systems_hits)
            best_ms = compute_best_MSHit(ms_per_function)
            # check if among rejected clusters with the MS, they can be created a new system
            best_ms = [Cluster([ms], model, hit_weights) for ms in best_ms]
            new_clst_combination = combine_multisystems(one_model_rejected_candidates, best_ms)
            for one_clust_combination in new_clst_combination:
                ordered_matcher = OrderedMatchMaker(model, redundancy_penalty=config.redundancy_penalty())
                res = ordered_matcher.match(one_clust_combination)
                if isinstance(res, System):
                    one_model_systems.append(res)
                else:
                    one_model_rejected_candidates.append(res)
            all_systems.extend(one_model_systems)
            all_rejected_candidates.extend(one_model_rejected_candidates)
    if all_systems:
        all_systems.sort(key=lambda syst: (syst.replicon_name, syst.position[0], syst.model.fqn, - syst.score))

    if not rep_db.guess_if_really_gembase():
        _log.warning(
            f"Most of replicons contains only ONE sequence are you sure that '{config.sequence_db()}' is a 'gembase'.")
    return all_systems, all_rejected_candidates


def search_in_unordered_replicon(hits_by_replicon: dict[str: list[macsylib.hit.CoreHit]],
                                 models_to_detect: list[macsylib.model.Model],
                                 logger: logging.Logger) -> tuple[list[LikelySystem], list[UnlikelySystem]]:
    """

    :param hits_by_replicon: the hits sort by replicon and position
    :param models_to_detect: the models to search
    :param logger: the logger
    """
    likely_systems = []
    rejected_hits = []
    for rep_name in hits_by_replicon:
        logger.info(f"\n{f' Hits analysis for replicon {rep_name} ':#^60}")
        for model in models_to_detect:
            logger.info(f"Check model {model.fqn}")
            hits_related_one_model = model.filter(hits_by_replicon[rep_name])
            logger.debug("{:#^80}".format(" hits related to {} \n".format(model.name)))
            logger.debug("id\trep_name\tpos\tseq_len\tgene_name\ti_eval\tscore\tprofile_cov\tseq_cov\tbeg_match\tend_match")
            logger.debug("".join([str(h) for h in hits_related_one_model]))
            logger.debug("#" * 80)
            logger.info("Searching systems")
            hits_related_one_model = model.filter(hits_by_replicon[rep_name])
            if hits_related_one_model:
                unordered_matcher = UnorderedMatchMaker(model)
                res = unordered_matcher.match(hits_related_one_model)
                if isinstance(res, LikelySystem):
                    likely_systems.append(res)
                elif isinstance(res, UnlikelySystem):
                    rejected_hits.append(res)
                else:
                    logger.info(f"No hits related to {model.fqn } found.")
            else:
                logger.info(f"No hits found for model {model.fqn}")
    if likely_systems:
        likely_systems.sort(key=lambda syst: (syst.replicon_name, syst.position[0], syst.model.fqn))
    return likely_systems, rejected_hits
