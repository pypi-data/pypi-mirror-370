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
import itertools
import sys
import os
import argparse
from io import StringIO

import macsylib
from macsylib import io
from macsylib.config import MacsyDefaults, Config
from macsylib.io import systems_to_tsv, solutions_to_tsv, rejected_candidates_to_tsv, summary_best_solution, \
    loners_to_tsv, multisystems_to_tsv, rejected_candidates_to_txt, likely_systems_to_txt, likely_systems_to_tsv, \
    unlikely_systems_to_txt, systems_to_txt
from macsylib.profile import ProfileFactory
from macsylib.registries import ModelLocation
from macsylib.gene import CoreGene, ModelGene, Exchangeable, GeneStatus
from macsylib.model import Model
from macsylib.hit import CoreHit, ModelHit, HitWeight, Loner, MultiSystem, LonerMultiSystem
from macsylib.cluster import Cluster
from macsylib.system import System, HitSystemTracker, RejectedCandidate, AbstractUnordered, LikelySystem, UnlikelySystem
from macsylib.solution import Solution

from macsylib.io import loner_warning
from tests import MacsyTest


class IoTest(MacsyTest):

    def setUp(self):
        self._reset_id()
        AbstractUnordered._id = itertools.count(1)


    def _reset_id(self):
        """
        reset System._id and RejectedCluster._id to get predictable ids
        """
        System._id = itertools.count(1)
        RejectedCandidate._id = itertools.count(1)


    def test_outfile_header(self):
        models = 'my_models'
        model_vers = '0.0a1'
        prog = 'macsylib'
        expected_header_begin = f"""# {{prog}} {macsylib.__version__} {macsylib.__commit__}
# models : {models}-{model_vers}
# {' '.join(sys.argv)}"""
        expected_header_end = """#
# WARNING: The replicon 'rep_1' has been SKIPPED. Cannot be solved before timeout.
# WARNING: The replicon 'rep_2' has been SKIPPED. Cannot be solved before timeout.
#"""
        # base header
        header = io.outfile_header(models, model_vers)
        self.assertEqual(header, expected_header_begin.format(prog=prog))

        # header when replicon has been skipped
        header = io.outfile_header(models, model_vers, skipped_replicons=['rep_1', 'rep_2'])
        self.assertEqual(header, f"{expected_header_begin.format(prog=prog)}\n{expected_header_end}")

        # header when it's not macsylib
        prog = 'msf'
        header = io.outfile_header(models, model_vers, prog_name=prog)
        self.assertEqual(header, expected_header_begin.format(prog=prog))

    def test_system_to_tsv(self):
        args = argparse.Namespace()
        args.sequence_db = self.find_data("base", "test_1.fasta")
        args.db_type = 'gembase'
        args.models_dir = self.find_data('models')
        cfg = Config(MacsyDefaults(), args)

        model_name = 'foo'
        models_location = ModelLocation(path=os.path.join(args.models_dir, model_name))

        # we need to reset the ProfileFactory
        # because it's a like a singleton
        # so other tests are influenced by ProfileFactory and it's configuration
        # for instance search_genes get profile without hmmer_exe
        profile_factory = ProfileFactory(cfg)

        model = Model("foo/T2SS", 10)
        gene_name = "gspD"
        c_gene_gspd = CoreGene(models_location, gene_name, profile_factory)
        gene_gspd = ModelGene(c_gene_gspd, model)
        model.add_mandatory_gene(gene_gspd)
        gene_name = "sctJ"
        c_gene_sctj = CoreGene(models_location, gene_name, profile_factory)
        gene_sctj = ModelGene(c_gene_sctj, model)
        model.add_accessory_gene(gene_sctj)

        hit_1 = CoreHit(c_gene_gspd, "hit_1", 803, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
        v_hit_1 = ModelHit(hit_1, gene_gspd, GeneStatus.MANDATORY)
        hit_2 = CoreHit(c_gene_sctj, "hit_2", 803, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
        v_hit_2 = ModelHit(hit_2, gene_sctj, GeneStatus.ACCESSORY)
        system_1 = System(model,
                          [Cluster([v_hit_1, v_hit_2], model, HitWeight(**cfg.hit_weights()))],
                          cfg.redundancy_penalty())
        model_fam_name = 'foo'
        model_vers = '0.0b2'
        system_tsv = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# Systems found:
"""
        system_tsv += "\t".join(["replicon", "hit_id", "gene_name", "hit_pos", "model_fqn", "sys_id",
                                 "sys_loci", "locus_num", "sys_wholeness", "sys_score", "sys_occ",
                                 "hit_gene_ref", "hit_status", "hit_seq_len", "hit_i_eval", "hit_score",
                                 "hit_profile_cov", "hit_seq_cov", "hit_begin_match", "hit_end_match", "counterpart",
                                 "used_in"])
        system_tsv += "\n"
        system_tsv += "\t".join(["replicon_id", "hit_1", "gspD", "1", "foo/T2SS", system_1.id,
                                 "1", "1", "1.000", "1.500", "1", "gspD", "mandatory", "803", "1.0", "1.000",
                                 "1.000", "1.000", "10", "20", "", ""])
        system_tsv += "\n"
        system_tsv += "\t".join(["replicon_id", "hit_2", "sctJ", "1", "foo/T2SS", system_1.id,
                                 "1", "1", "1.000", "1.500", "1", "sctJ", "accessory", "803", "1.0", "1.000",
                                 "1.000", "1.000", "10", "20", "", ""])
        system_tsv += "\n\n"

        f_out = StringIO()
        track_multi_systems_hit = HitSystemTracker([system_1])
        systems_to_tsv(model_fam_name, model_vers, [system_1], track_multi_systems_hit, f_out)
        self.assertMultiLineEqual(system_tsv, f_out.getvalue())

        # test No system found
        system_str = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# No System found
"""
        f_out = StringIO()
        track_multi_systems_hit = HitSystemTracker([])
        systems_to_tsv(model_fam_name, model_vers, [], track_multi_systems_hit, f_out)
        self.assertMultiLineEqual(system_str, f_out.getvalue())

        # test No system found replicon skipped
        system_str = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
#
# WARNING: The replicon 'rep_1' has been SKIPPED. Cannot be solved before timeout.
# WARNING: The replicon 'rep_2' has been SKIPPED. Cannot be solved before timeout.
#
# No System found
"""
        f_out = StringIO()
        track_multi_systems_hit = HitSystemTracker([])
        systems_to_tsv(model_fam_name, model_vers, [], track_multi_systems_hit, f_out, skipped_replicons=['rep_1', 'rep_2'])
        self.assertMultiLineEqual(system_str, f_out.getvalue())

        gene_name = "tadZ"
        c_gene_tadz = CoreGene(models_location, gene_name, profile_factory)
        gene_tadz = ModelGene(c_gene_tadz, model, loner=True)
        model.add_accessory_gene(gene_tadz)
        hit_3 = CoreHit(c_gene_tadz, "hit_3", 803, "replicon_id", 30, 1.0, 1.0, 1.0, 1.0, 10, 20)
        loner_1 = Loner(hit_3, gene_tadz, GeneStatus.ACCESSORY)
        system_2 = System(model,
                          [Cluster([v_hit_1, v_hit_2], model, HitWeight(**cfg.hit_weights())),
                           Cluster([loner_1], model, HitWeight(**cfg.hit_weights()))],
                          cfg.redundancy_penalty())
        hit_4 = CoreHit(c_gene_gspd, "hit_4", 803, "replicon_id", 40, 1.0, 1.0, 1.0, 1.0, 10, 20)
        mhit_4 = ModelHit(hit_4, gene_gspd, GeneStatus.MANDATORY)
        hit_5 = CoreHit(c_gene_sctj, "hit_5", 803, "replicon_id", 41, 1.0, 1.0, 1.0, 1.0, 10, 20)
        mhit_5 = ModelHit(hit_5, gene_sctj, GeneStatus.ACCESSORY)
        system_3 = System(model,
                          [Cluster([mhit_4, mhit_5], model, HitWeight(**cfg.hit_weights())),
                           Cluster([loner_1], model, HitWeight(**cfg.hit_weights()))],
                          cfg.redundancy_penalty())
        f_out = StringIO()
        track_multi_systems_hit = HitSystemTracker([system_2, system_3])
        systems_to_tsv(model_fam_name, model_vers, [system_2, system_3], track_multi_systems_hit, f_out)

        system_tsv = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# Systems found:
replicon\thit_id\tgene_name\thit_pos\tmodel_fqn\tsys_id\tsys_loci\tlocus_num\tsys_wholeness\tsys_score\tsys_occ\thit_gene_ref\thit_status\thit_seq_len\thit_i_eval\thit_score\thit_profile_cov\thit_seq_cov\thit_begin_match\thit_end_match\tcounterpart\tused_in
replicon_id\thit_1\tgspD\t1\tfoo/T2SS\treplicon_id_T2SS_2\t1\t1\t1.000\t1.850\t1\tgspD\tmandatory\t803\t1.0\t1.000\t1.000\t1.000\t10\t20\t\t
replicon_id\thit_2\tsctJ\t1\tfoo/T2SS\treplicon_id_T2SS_2\t1\t1\t1.000\t1.850\t1\tsctJ\taccessory\t803\t1.0\t1.000\t1.000\t1.000\t10\t20\t\t
replicon_id\thit_3\ttadZ\t30\tfoo/T2SS\treplicon_id_T2SS_2\t1\t-1\t1.000\t1.850\t1\ttadZ\taccessory\t803\t1.0\t1.000\t1.000\t1.000\t10\t20\t\t

replicon_id\thit_4\tgspD\t40\tfoo/T2SS\treplicon_id_T2SS_3\t1\t1\t1.000\t1.850\t1\tgspD\tmandatory\t803\t1.0\t1.000\t1.000\t1.000\t10\t20\t\t
replicon_id\thit_5\tsctJ\t41\tfoo/T2SS\treplicon_id_T2SS_3\t1\t1\t1.000\t1.850\t1\tsctJ\taccessory\t803\t1.0\t1.000\t1.000\t1.000\t10\t20\t\t
replicon_id\thit_3\ttadZ\t30\tfoo/T2SS\treplicon_id_T2SS_3\t1\t-1\t1.000\t1.850\t1\ttadZ\taccessory\t803\t1.0\t1.000\t1.000\t1.000\t10\t20\t\t

# WARNING Loner: there is only 1 occurrence(s) of loner 'tadZ' and 2 potential systems [replicon_id_T2SS_2, replicon_id_T2SS_3]
"""
        self.assertMultiLineEqual(system_tsv, f_out.getvalue())



    def test_system_to_txt(self):
        args = argparse.Namespace()
        args.sequence_db = self.find_data("base", "test_1.fasta")
        args.db_type = 'gembase'
        args.models_dir = self.find_data('models')
        cfg = Config(MacsyDefaults(), args)

        model_name = 'foo'
        models_location = ModelLocation(path=os.path.join(args.models_dir, model_name))

        # we need to reset the ProfileFactory
        # because it's a like a singleton
        # so other tests are influenced by ProfileFactory and it's configuration
        # for instance search_genes get profile without hmmer_exe
        profile_factory = ProfileFactory(cfg)

        model = Model("foo/T2SS", 10)
        gene_name = "gspD"
        c_gene_gspd = CoreGene(models_location, gene_name, profile_factory)
        gene_gspd = ModelGene(c_gene_gspd, model)
        model.add_mandatory_gene(gene_gspd)
        gene_name = "sctJ"
        c_gene_sctj = CoreGene(models_location, gene_name, profile_factory)
        gene_sctj = ModelGene(c_gene_sctj, model)
        model.add_accessory_gene(gene_sctj)

        hit_1 = CoreHit(c_gene_gspd, "hit_1", 803, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
        v_hit_1 = ModelHit(hit_1, gene_gspd, GeneStatus.MANDATORY)
        hit_2 = CoreHit(c_gene_sctj, "hit_2", 803, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
        v_hit_2 = ModelHit(hit_2, gene_sctj, GeneStatus.ACCESSORY)
        system_1 = System(model,
                          [Cluster([v_hit_1, v_hit_2], model, HitWeight(**cfg.hit_weights()))],
                          cfg.redundancy_penalty())
        model_fam_name = 'foo'
        model_vers = '0.0b2'
        system_txt = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# Systems found:

system id = replicon_id_T2SS_1
model = foo/T2SS
replicon = replicon_id
clusters = [('hit_1', 'gspD', 1), ('hit_2', 'sctJ', 1)]
occ = 1
wholeness = 1.000
loci nb = 1
score = 1.500

mandatory genes:
\t- gspD: 1 (gspD)

accessory genes:
\t- sctJ: 1 (sctJ)

neutral genes:

{"=" * 60}
"""

        f_out = StringIO()
        track_multi_systems_hit = HitSystemTracker([system_1])
        systems_to_txt(model_fam_name, model_vers,
                       [system_1], track_multi_systems_hit, f_out)

        self.assertMultiLineEqual(system_txt, f_out.getvalue())

        # test No system found
        system_str = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# No System found
"""
        f_out = StringIO()
        track_multi_systems_hit = HitSystemTracker([])
        systems_to_txt(model_fam_name, model_vers,
                       [], track_multi_systems_hit, f_out)
        self.assertMultiLineEqual(system_str, f_out.getvalue())

        # test No system found replicon skipped
        system_str = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
#
# WARNING: The replicon 'rep_1' has been SKIPPED. Cannot be solved before timeout.
# WARNING: The replicon 'rep_2' has been SKIPPED. Cannot be solved before timeout.
#
# No System found
"""
        f_out = StringIO()
        track_multi_systems_hit = HitSystemTracker([])
        systems_to_txt(model_fam_name, model_vers, [], track_multi_systems_hit, f_out,
                       skipped_replicons=['rep_1', 'rep_2'])
        self.assertMultiLineEqual(system_str, f_out.getvalue())

        gene_name = "tadZ"
        c_gene_tadz = CoreGene(models_location, gene_name, profile_factory)
        gene_tadz = ModelGene(c_gene_tadz, model, loner=True)
        model.add_accessory_gene(gene_tadz)
        hit_3 = CoreHit(c_gene_tadz, "hit_3", 803, "replicon_id", 30, 1.0, 1.0, 1.0, 1.0, 10, 20)
        loner_1 = Loner(hit_3, gene_tadz, GeneStatus.ACCESSORY)
        system_2 = System(model,
                          [Cluster([v_hit_1, v_hit_2], model, HitWeight(**cfg.hit_weights())),
                           Cluster([loner_1], model, HitWeight(**cfg.hit_weights()))],
                          cfg.redundancy_penalty())
        hit_4 = CoreHit(c_gene_gspd, "hit_4", 803, "replicon_id", 40, 1.0, 1.0, 1.0, 1.0, 10, 20)
        mhit_4 = ModelHit(hit_4, gene_gspd, GeneStatus.MANDATORY)
        hit_5 = CoreHit(c_gene_sctj, "hit_5", 803, "replicon_id", 41, 1.0, 1.0, 1.0, 1.0, 10, 20)
        mhit_5 = ModelHit(hit_5, gene_sctj, GeneStatus.ACCESSORY)
        system_3 = System(model,
                          [Cluster([mhit_4, mhit_5], model, HitWeight(**cfg.hit_weights())),
                           Cluster([loner_1], model, HitWeight(**cfg.hit_weights()))],
                          cfg.redundancy_penalty())

        system_str = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# Systems found:

system id = replicon_id_T2SS_2
model = foo/T2SS
replicon = replicon_id
clusters = [('hit_1', 'gspD', 1), ('hit_2', 'sctJ', 1)], [('hit_3', 'tadZ', 30)]
occ = 1
wholeness = 1.000
loci nb = 1
score = 1.850

mandatory genes:
\t- gspD: 1 (gspD)

accessory genes:
\t- sctJ: 1 (sctJ)
\t- tadZ: 1 (tadZ)

neutral genes:

============================================================
system id = replicon_id_T2SS_3
model = foo/T2SS
replicon = replicon_id
clusters = [('hit_4', 'gspD', 40), ('hit_5', 'sctJ', 41)], [('hit_3', 'tadZ', 30)]
occ = 1
wholeness = 1.000
loci nb = 1
score = 1.850

mandatory genes:
\t- gspD: 1 (gspD)

accessory genes:
\t- sctJ: 1 (sctJ)
\t- tadZ: 1 (tadZ)

neutral genes:

============================================================
# WARNING Loner: there is only 1 occurrence(s) of loner 'tadZ' and 2 potential systems [replicon_id_T2SS_2, replicon_id_T2SS_3]
"""
        f_out = StringIO()
        track_multi_systems_hit = HitSystemTracker([system_2, system_3])
        systems_to_txt(model_fam_name, model_vers, [system_2, system_3], track_multi_systems_hit, f_out)
        self.assertMultiLineEqual(system_str, f_out.getvalue())


    def test_solution_to_tsv(self):
        args = argparse.Namespace()
        args.sequence_db = self.find_data("base", "test_1.fasta")
        args.db_type = 'gembase'
        args.models_dir = self.find_data('models')
        cfg = Config(MacsyDefaults(), args)
        model_name = 'foo'
        models_location = ModelLocation(path=os.path.join(args.models_dir, model_name))

        # we need to reset the ProfileFactory
        # because it's a like a singleton
        # so other tests are influenced by ProfileFactory and it's configuration
        # for instance search_genes get profile without hmmer_exe
        profile_factory = ProfileFactory(cfg)

        model_A = Model("foo/A", 10)
        model_B = Model("foo/B", 10)
        model_C = Model("foo/C", 10)

        c_gene_sctn_flg = CoreGene(models_location, "sctN_FLG", profile_factory)
        gene_sctn_flg = ModelGene(c_gene_sctn_flg, model_B)
        c_gene_sctj_flg = CoreGene(models_location, "sctJ_FLG", profile_factory)
        gene_sctj_flg = ModelGene(c_gene_sctj_flg, model_B)
        c_gene_flgB = CoreGene(models_location, "flgB", profile_factory)
        gene_flgB = ModelGene(c_gene_flgB, model_B)
        c_gene_tadZ = CoreGene(models_location, "tadZ", profile_factory)
        gene_tadZ = ModelGene(c_gene_tadZ, model_B)

        c_gene_sctn = CoreGene(models_location, "sctN", profile_factory)
        gene_sctn = ModelGene(c_gene_sctn, model_A)
        gene_sctn_hom = Exchangeable(c_gene_sctn_flg, gene_sctn)
        gene_sctn.add_exchangeable(gene_sctn_hom)

        c_gene_sctj = CoreGene(models_location, "sctJ", profile_factory)
        gene_sctj = ModelGene(c_gene_sctj, model_A)
        gene_sctj_an = Exchangeable(c_gene_sctj_flg, gene_sctj)
        gene_sctj.add_exchangeable(gene_sctj_an)

        c_gene_gspd = CoreGene(models_location, "gspD", profile_factory)
        gene_gspd = ModelGene(c_gene_gspd, model_A)
        gene_gspd_an = Exchangeable(c_gene_flgB, gene_gspd)
        gene_gspd.add_exchangeable(gene_gspd_an)

        c_gene_abc = CoreGene(models_location, "abc", profile_factory)
        gene_abc = ModelGene(c_gene_abc, model_A)
        gene_abc_ho = Exchangeable(c_gene_tadZ, gene_abc)
        gene_abc.add_exchangeable(gene_abc_ho)

        model_A.add_mandatory_gene(gene_sctn)
        model_A.add_mandatory_gene(gene_sctj)
        model_A.add_accessory_gene(gene_gspd)
        model_A.add_forbidden_gene(gene_abc)

        model_B.add_mandatory_gene(gene_sctn_flg)
        model_B.add_mandatory_gene(gene_sctj_flg)
        model_B.add_accessory_gene(gene_flgB)
        model_B.add_accessory_gene(gene_tadZ)

        model_C.add_mandatory_gene(gene_sctn_flg)
        model_C.add_mandatory_gene(gene_sctj_flg)
        model_C.add_mandatory_gene(gene_flgB)
        model_C.add_accessory_gene(gene_tadZ)
        model_C.add_accessory_gene(gene_gspd)

        #                    gene,     hit_id, hit_seq_len, rep_name, pos, i_eval
        h_sctj = CoreHit(c_gene_sctj, "hit_sctj", 803, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
        h_sctn = CoreHit(c_gene_sctn, "hit_sctn", 803, "replicon_id", 2, 1.0, 1.0, 1.0, 1.0, 10, 20)
        h_gspd = CoreHit(c_gene_gspd, "hit_gspd", 803, "replicon_id", 3, 1.0, 1.0, 1.0, 1.0, 10, 20)
        h_sctj2 = CoreHit(c_gene_sctj, "hit_sctj2", 803, "replicon_id", 4, 1.0, 1.0, 1.0, 1.0, 10, 20)
        h_sctn2 = CoreHit(c_gene_sctn, "hit_sctn2", 803, "replicon_id", 5, 1.0, 1.0, 1.0, 1.0, 10, 20)

        h_sctj_flg = CoreHit(c_gene_sctj_flg, "hit_sctj_flg", 803, "replicon_id", 6, 1.0, 1.0, 1.0, 1.0, 10, 20)
        h_tadZ = CoreHit(c_gene_tadZ, "hit_tadZ", 803, "replicon_id", 7, 1.0, 1.0, 1.0, 1.0, 10, 20)
        h_flgB = CoreHit(c_gene_flgB, "hit_flgB", 803, "replicon_id", 8, 1.0, 1.0, 1.0, 1.0, 10, 20)
        h_sctj_flg2 = CoreHit(c_gene_sctj_flg, "hit_sctj_flg2", 803, "replicon_id", 14, 1.0, 1.0, 1.0, 1.0, 10, 20)
        h_tadZ2 = CoreHit(c_gene_tadZ, "hit_tadZ2", 803, "replicon_id", 15, 1.0, 1.0, 1.0, 1.0, 10, 20)
        h_flgB2 = CoreHit(c_gene_flgB, "hit_flgB2", 803, "replicon_id", 16, 1.0, 1.0, 1.0, 1.0, 10, 20)
        h_gspd2 = CoreHit(c_gene_gspd, "hit_gspd2", 803, "replicon_id", 17, 1.0, 1.0, 1.0, 1.0, 10, 20)

        model_A._min_mandatory_genes_required = 2
        model_A._min_genes_required = 2
        hit_weights = HitWeight(**cfg.hit_weights())
        c1 = Cluster([ModelHit(h_sctj, gene_sctj, GeneStatus.MANDATORY),
                      ModelHit(h_sctn, gene_sctn, GeneStatus.MANDATORY),
                      ModelHit(h_gspd, gene_gspd, GeneStatus.ACCESSORY)
                      ],
                     model_A, hit_weights)

        c2 = Cluster([ModelHit(h_sctj2, gene_sctj, GeneStatus.MANDATORY),
                      ModelHit(h_sctn2, gene_sctn, GeneStatus.MANDATORY)],
                     model_A, hit_weights)

        model_B._min_mandatory_genes_required = 1
        model_B._min_genes_required = 2
        c3 = Cluster([ModelHit(h_sctj_flg, gene_sctj_flg, GeneStatus.MANDATORY),
                      ModelHit(h_tadZ, gene_tadZ, GeneStatus.ACCESSORY),
                      ModelHit(h_flgB, gene_flgB, GeneStatus.ACCESSORY)],
                     model_B, hit_weights)

        model_C._min_mandatory_genes_required = 1
        model_C._min_genes_required = 2
        c4 = Cluster([ModelHit(h_sctj_flg2, gene_sctj_flg, GeneStatus.MANDATORY),
                      ModelHit(h_tadZ2, gene_tadZ, GeneStatus.ACCESSORY),
                      ModelHit(h_flgB2, gene_flgB, GeneStatus.MANDATORY),
                      ModelHit(h_gspd2, gene_gspd, GeneStatus.ACCESSORY)],
                     model_C, hit_weights)

        sys_A = System(model_A, [c1, c2], cfg.redundancy_penalty())
        sys_A.id = "sys_id_A"
        sys_B = System(model_B, [c3], cfg.redundancy_penalty())
        sys_B.id = "sys_id_B"
        sys_C = System(model_C, [c4], cfg.redundancy_penalty())
        sys_C.id = "sys_id_C"

        sol_1 = Solution([sys_A, sys_C])
        sol_2 = Solution([sys_A, sys_B])
        sol_id_1 = '1'
        sol_id_2 = '2'

        model_fam_name = 'foo'
        model_vers = '0.0b2'
        sol_tsv = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# Systems found:
"""
        sol_tsv += "\t".join(["sol_id", "replicon", "hit_id", "gene_name", "hit_pos", "model_fqn", "sys_id",
                              "sys_loci", "locus_num",
                              "sys_wholeness", "sys_score", "sys_occ", "hit_gene_ref", "hit_status",
                              "hit_seq_len", "hit_i_eval", "hit_score", "hit_profile_cov", "hit_seq_cov",
                              "hit_begin_match", "hit_end_match", "counterpart", "used_in"])
        sol_tsv += "\n"
        sol_tsv += '\t'.join([sol_id_1, 'replicon_id', 'hit_sctj', 'sctJ', '1', 'foo/A', 'sys_id_A',
                              '2', '1', '1.000', '1.500', '2', 'sctJ', 'mandatory',
                              '803', '1.0', '1.000', '1.000', '1.000', '10', '20', '', ''])
        sol_tsv += "\n"
        sol_tsv += '\t'.join([sol_id_1, 'replicon_id', 'hit_sctn', 'sctN', '2', 'foo/A', 'sys_id_A',
                              '2', '1', '1.000', '1.500', '2', 'sctN', 'mandatory',
                              '803', '1.0', '1.000', '1.000', '1.000', '10', '20', '', ''])
        sol_tsv += "\n"
        sol_tsv += '\t'.join([sol_id_1, 'replicon_id', 'hit_gspd', 'gspD', '3', 'foo/A', 'sys_id_A',
                              '2', '1', '1.000', '1.500', '2', 'gspD', 'accessory',
                              '803', '1.0', '1.000', '1.000', '1.000', '10', '20', '', ''])
        sol_tsv += "\n"
        sol_tsv += '\t'.join([sol_id_1, 'replicon_id', 'hit_sctj2', 'sctJ', '4', 'foo/A', 'sys_id_A',
                              '2', '2', '1.000', '1.500', '2', 'sctJ', 'mandatory',
                              '803', '1.0', '1.000', '1.000', '1.000', '10', '20', '', ''])
        sol_tsv += "\n"
        sol_tsv += '\t'.join([sol_id_1, 'replicon_id', 'hit_sctn2', 'sctN', '5', 'foo/A', 'sys_id_A',
                              '2', '2', '1.000', '1.500', '2', 'sctN', 'mandatory',
                              '803', '1.0', '1.000', '1.000', '1.000', '10', '20', '', ''])
        sol_tsv += "\n"
        sol_tsv += "\n"
        sol_tsv += '\t'.join([sol_id_1, 'replicon_id', 'hit_sctj_flg2', 'sctJ_FLG', '14', 'foo/C', 'sys_id_C',
                              '1', '1', '0.800', '3.000', '1', 'sctJ_FLG', 'mandatory',
                              '803', '1.0', '1.000', '1.000', '1.000', '10', '20', '', ''])
        sol_tsv += "\n"
        sol_tsv += '\t'.join([sol_id_1, 'replicon_id', 'hit_tadZ2', 'tadZ', '15', 'foo/C', 'sys_id_C',
                              '1', '1', '0.800', '3.000', '1', 'tadZ', 'accessory',
                              '803', '1.0', '1.000', '1.000', '1.000', '10', '20', '', ''])
        sol_tsv += "\n"
        sol_tsv += '\t'.join([sol_id_1, 'replicon_id', 'hit_flgB2', 'flgB', '16', 'foo/C', 'sys_id_C',
                              '1', '1', '0.800', '3.000', '1', 'flgB', 'mandatory',
                              '803', '1.0', '1.000', '1.000', '1.000', '10', '20', '', ''])
        sol_tsv += "\n"
        sol_tsv += '\t'.join([sol_id_1, 'replicon_id', 'hit_gspd2', 'gspD', '17', 'foo/C', 'sys_id_C',
                              '1', '1', '0.800', '3.000', '1', 'gspD', 'accessory',
                              '803', '1.0', '1.000', '1.000', '1.000', '10', '20', '', ''])
        sol_tsv += "\n"
        sol_tsv += "\n"
        sol_tsv += '\t'.join([sol_id_2, 'replicon_id', 'hit_sctj', 'sctJ', '1', 'foo/A', 'sys_id_A',
                              '2', '1', '1.000', '1.500', '2', 'sctJ', 'mandatory',
                              '803', '1.0', '1.000', '1.000', '1.000', '10', '20', '', ''])
        sol_tsv += "\n"
        sol_tsv += '\t'.join([sol_id_2, 'replicon_id', 'hit_sctn', 'sctN', '2', 'foo/A', 'sys_id_A',
                              '2', '1', '1.000', '1.500', '2', 'sctN', 'mandatory',
                              '803', '1.0', '1.000', '1.000', '1.000', '10', '20', '', ''])
        sol_tsv += "\n"
        sol_tsv += '\t'.join([sol_id_2, 'replicon_id', 'hit_gspd', 'gspD', '3', 'foo/A', 'sys_id_A',
                              '2', '1', '1.000', '1.500', '2', 'gspD', 'accessory',
                              '803', '1.0', '1.000', '1.000', '1.000', '10', '20', '', ''])
        sol_tsv += "\n"
        sol_tsv += '\t'.join([sol_id_2, 'replicon_id', 'hit_sctj2', 'sctJ', '4', 'foo/A', 'sys_id_A',
                              '2', '2', '1.000', '1.500', '2', 'sctJ', 'mandatory',
                              '803', '1.0', '1.000', '1.000', '1.000', '10', '20', '', ''])
        sol_tsv += "\n"
        sol_tsv += '\t'.join([sol_id_2, 'replicon_id', 'hit_sctn2', 'sctN', '5', 'foo/A', 'sys_id_A',
                              '2', '2', '1.000', '1.500', '2', 'sctN', 'mandatory',
                              '803', '1.0', '1.000', '1.000', '1.000', '10', '20', '', ''])
        sol_tsv += "\n"
        sol_tsv += "\n"
        sol_tsv += '\t'.join([sol_id_2, 'replicon_id', 'hit_sctj_flg', 'sctJ_FLG', '6', 'foo/B', 'sys_id_B',
                              '1', '1', '0.750', '2.000', '1', 'sctJ_FLG', 'mandatory',
                              '803', '1.0', '1.000', '1.000', '1.000', '10', '20', '', ''])
        sol_tsv += "\n"
        sol_tsv += '\t'.join([sol_id_2, 'replicon_id', 'hit_tadZ', 'tadZ', '7', 'foo/B', 'sys_id_B',
                              '1', '1', '0.750', '2.000', '1', 'tadZ', 'accessory',
                              '803', '1.0', '1.000', '1.000', '1.000', '10', '20', '', ''])
        sol_tsv += "\n"
        sol_tsv += '\t'.join([sol_id_2, 'replicon_id', 'hit_flgB', 'flgB', '8', 'foo/B', 'sys_id_B',
                              '1', '1', '0.750', '2.000', '1', 'flgB', 'accessory',
                              '803', '1.0', '1.000', '1.000', '1.000', '10', '20', '', ''])
        sol_tsv += "\n"
        sol_tsv += "\n"

        f_out = StringIO()
        hit_multi_sys_tracker = HitSystemTracker([sys_A, sys_B, sys_C])
        solutions_to_tsv(model_fam_name, model_vers, [sol_1, sol_2], hit_multi_sys_tracker, f_out)
        self.maxDiff = None
        self.assertMultiLineEqual(sol_tsv, f_out.getvalue())

        # No solutions
        solution_file = StringIO()
        solutions_to_tsv(model_fam_name, model_vers, [], hit_multi_sys_tracker, solution_file)
        solution_file.seek(0)
        self.assertMultiLineEqual(sol_tsv, f_out.getvalue())


    def test_summary_best_solution(self):
        best_solution_path = self.find_data('best_solution.tsv')
        expected_summary_path = self.find_data('best_solution_summary.tsv')
        model_fam_name = 'set_1'
        model_vers = '0.0b2'
        f_out = StringIO()
        models_fqn = ['set_1/MSH', 'set_1/T2SS', 'set_1/T4P', 'set_1/T4bP']
        replicon_names= ['VICH001.B.00001.C001']
        summary_best_solution(model_fam_name,
                              model_vers,
                              best_solution_path,
                              f_out,
                              models_fqn,
                              replicon_names)
        f_out.seek(0) # have to put cursor at the beginning before testing the content
        self.assertTsvEqual(expected_summary_path, f_out, tsv_type='best_solution_summary.tsv')


    def test_summary_best_solution_empty(self):
        best_solution_path = self.find_data('best_solution_empty.tsv')
        model_fam_name = 'set_1'
        model_vers = '0.0b2'
        expected_summary_file = StringIO()
        expected_summary_file.write("# macsylib vers\n")
        expected_summary_file.write("# models: set_1-0.0b2\n")
        expected_summary_file.write("# msf command line\n")
        expected_summary_file.write('\t'.join(['replicon', 'set_1/MSH', 'set_1/T2SS', 'set_1/T4P', 'set_1/T4bP']) + '\n')
        expected_summary_file.write('\t'.join(['VICH001.B.00001.C001',	'0', '0', '0', '0']) + '\n')
        expected_summary_file.seek(0)

        computed_summary_file = StringIO()
        models_fqn = ['set_1/MSH', 'set_1/T2SS', 'set_1/T4P', 'set_1/T4bP']
        replicon_names = ['VICH001.B.00001.C001']
        summary_best_solution(model_fam_name,
                              model_vers,
                              best_solution_path,
                              computed_summary_file,
                              models_fqn,
                              replicon_names)
        computed_summary_file.seek(0)
        self.assertTsvEqual(expected_summary_file, computed_summary_file, tsv_type='best_solution_summary.tsv')


    def test_summary_best_solution_lack_models(self):
        best_solution_path = self.find_data('best_solution.tsv')
        expected_summary_path = self.find_data('summary_best_solution_lack_models.tsv')
        model_fam_name = 'set_1'
        model_vers = '0.0b2'
        computed_summary_file = StringIO()
        models_fqn = ['set_1/MSH', 'set_1/T2SS', 'set_1/T4P', 'set_1/T4bP', "empty/model"]
        replicon_names = ['VICH001.B.00001.C001']
        summary_best_solution(model_fam_name,
                              model_vers,
                              best_solution_path,
                              computed_summary_file,
                              models_fqn,
                              replicon_names)
        computed_summary_file.seek(0)
        self.assertTsvEqual(expected_summary_path, computed_summary_file, tsv_type='best_solution_summary.tsv')


    def test_summary_best_solution_lack_replicon(self):
        best_solution_path = self.find_data('best_solution.tsv')
        expected_summary_path = self.find_data('summary_best_solution_lack_replicon.tsv')
        model_fam_name = 'set_1'
        model_vers = '0.0b2'
        computed_summary_file = StringIO()
        models_fqn = ['set_1/MSH', 'set_1/T2SS', 'set_1/T4P', 'set_1/T4bP']
        replicon_names = ['VICH001.B.00001.C001', 'added_replicon']
        summary_best_solution(model_fam_name, model_vers, best_solution_path, computed_summary_file, models_fqn, replicon_names)
        computed_summary_file.seek(0)
        self.assertTsvEqual(expected_summary_path, computed_summary_file, tsv_type='best_solution_summary.tsv')


    def test_summary_best_solution_lack_models_replicons(self):
        best_solution_path = self.find_data('best_solution.tsv')
        expected_summary_path = self.find_data('summary_best_solution_lack_models_replicons.tsv')
        model_fam_name = 'set_1'
        model_vers = '0.0b2'
        computed_summary_file = StringIO()
        models_fqn = ['set_1/MSH', 'set_1/T2SS', 'set_1/T4P', 'set_1/T4bP', "empty/model"]
        replicon_names = ['VICH001.B.00001.C001', 'added_replicon']
        summary_best_solution(model_fam_name, model_vers, best_solution_path, computed_summary_file, models_fqn, replicon_names)
        computed_summary_file.seek(0)
        self.assertTsvEqual(expected_summary_path, computed_summary_file, tsv_type='best_solution_summary.tsv')


    def test_rejected_candidates_to_tsv(self):
        args = argparse.Namespace()
        args.sequence_db = self.find_data("base", "test_1.fasta")
        args.db_type = 'gembase'
        args.models_dir = self.find_data('models')
        args.res_search_dir = "blabla"

        cfg = Config(MacsyDefaults(), args)
        model_name = 'foo'
        models_location = ModelLocation(path=os.path.join(args.models_dir, model_name))
        profile_factory = ProfileFactory(cfg)

        model = Model("foo/T2SS", 11)

        gene_name = "gspD"
        c_gene_gspd = CoreGene(models_location, gene_name, profile_factory)
        gene_1 = ModelGene(c_gene_gspd, model)
        gene_name = "sctC"
        c_gene_sctc = CoreGene(models_location, gene_name, profile_factory)
        gene_2 = ModelGene(c_gene_sctc, model)
        model.add_mandatory_gene(gene_1)
        model.add_accessory_gene(gene_2)

        #     CoreHit(gene, model, hit_id, hit_seq_length, replicon_name, position, i_eval, score,
        #         profile_coverage, sequence_coverage, begin_match, end_match
        h10 = CoreHit(c_gene_gspd, "h10", 10, "replicon_1", 10, 1.0, 10.0, 1.0, 1.0, 10, 20)
        v_h10 = ModelHit(h10, gene_1, GeneStatus.MANDATORY)
        h20 = CoreHit(c_gene_sctc, "h20", 10, "replicon_1", 20, 1.0, 20.0, 1.0, 1.0, 10, 20)
        v_h20 = ModelHit(h20, gene_2, GeneStatus.ACCESSORY)
        h40 = CoreHit(c_gene_gspd, "h10", 10, "replicon_1", 40, 1.0, 10.0, 1.0, 1.0, 10, 20)
        v_h40 = ModelHit(h40, gene_1, GeneStatus.MANDATORY)
        h50 = CoreHit(c_gene_sctc, "h20", 10, "replicon_1", 50, 1.0, 20.0, 1.0, 1.0, 10, 20)
        v_h50 = ModelHit(h50, gene_2, GeneStatus.ACCESSORY)
        hit_weights = HitWeight(**cfg.hit_weights())
        c1 = Cluster([v_h10, v_h20], model, hit_weights)
        c2 = Cluster([v_h40, v_h50], model, hit_weights)
        r_c = RejectedCandidate(model, [c1, c2], ["The reasons to reject these candidate"])

        model_fam_name = 'foo'
        model_vers = '0.0b2'
        rej_cand_str = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# Rejected candidates found:
"""
        rej_cand_str += '\t'.join(
            ['candidate_id', 'replicon', 'model_fqn', 'cluster_id', 'hit_id', 'hit_pos', 'gene_name', 'function',
             'reasons'])
        rej_cand_str += '\n'
        rej_cand_str += '\t'.join(['replicon_1_T2SS_1', 'replicon_1', 'foo/T2SS', c1.id, 'h10', '10', 'gspD', 'gspD',
                                   'The reasons to reject these candidate'])
        rej_cand_str += '\n'
        rej_cand_str += '\t'.join(['replicon_1_T2SS_1', 'replicon_1', 'foo/T2SS', c1.id, 'h20', '20', 'sctC', 'sctC',
                                   'The reasons to reject these candidate'])
        rej_cand_str += '\n'
        rej_cand_str += '\t'.join(['replicon_1_T2SS_1', 'replicon_1', 'foo/T2SS', c2.id, 'h10', '40', 'gspD', 'gspD',
                                   'The reasons to reject these candidate'])
        rej_cand_str += '\n'
        rej_cand_str += '\t'.join(['replicon_1_T2SS_1', 'replicon_1', 'foo/T2SS', c2.id, 'h20', '50', 'sctC', 'sctC',
                                   'The reasons to reject these candidate'])
        rej_cand_str += '\n'
        rej_cand_str += '\n'

        f_out = StringIO()
        rejected_candidates_to_tsv(model_fam_name, model_vers, [r_c], f_out)
        self.maxDiff = None
        self.assertMultiLineEqual(rej_cand_str, f_out.getvalue())

        rej_cand_str = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# No Rejected candidates
"""
        f_out = StringIO()
        rejected_candidates_to_tsv(model_fam_name, model_vers, [], f_out)
        self.assertMultiLineEqual(rej_cand_str, f_out.getvalue())

        # test with skipped replicons
        rej_cand_str = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
#
# WARNING: The replicon 'rep_1' has been SKIPPED. Cannot be solved before timeout.
# WARNING: The replicon 'rep_2' has been SKIPPED. Cannot be solved before timeout.
#
# No Rejected candidates
"""
        f_out = StringIO()
        rejected_candidates_to_tsv(model_fam_name, model_vers, [], f_out, skipped_replicons=['rep_1', 'rep_2'])
        self.maxDiff = None
        self.assertMultiLineEqual(rej_cand_str, f_out.getvalue())


    def test_rejected_candidates_to_txt(self):
        args = argparse.Namespace()
        args.sequence_db = self.find_data("base", "test_1.fasta")
        args.db_type = 'gembase'
        args.models_dir = self.find_data('models')
        args.res_search_dir = "blabla"

        cfg = Config(MacsyDefaults(), args)
        model_name = 'foo'
        models_location = ModelLocation(path=os.path.join(args.models_dir, model_name))
        profile_factory = ProfileFactory(cfg)

        model = Model("foo/T2SS", 11)

        gene_name = "gspD"
        c_gene_gspd = CoreGene(models_location, gene_name, profile_factory)
        gene_1 = ModelGene(c_gene_gspd, model)
        gene_name = "sctC"
        c_gene_sctc = CoreGene(models_location, gene_name, profile_factory)
        gene_2 = ModelGene(c_gene_sctc, model)
        model.add_mandatory_gene(gene_1)
        model.add_accessory_gene(gene_2)

        #     CoreHit(gene, model, hit_id, hit_seq_length, replicon_name, position, i_eval, score,
        #         profile_coverage, sequence_coverage, begin_match, end_match
        h10 = CoreHit(c_gene_gspd, "h10", 10, "replicon_1", 10, 1.0, 10.0, 1.0, 1.0, 10, 20)
        v_h10 = ModelHit(h10, gene_1, GeneStatus.MANDATORY)
        h20 = CoreHit(c_gene_sctc, "h20", 10, "replicon_1", 20, 1.0, 20.0, 1.0, 1.0, 10, 20)
        v_h20 = ModelHit(h20, gene_2, GeneStatus.ACCESSORY)
        h40 = CoreHit(c_gene_gspd, "h10", 10, "replicon_1", 40, 1.0, 10.0, 1.0, 1.0, 10, 20)
        v_h40 = ModelHit(h40, gene_1, GeneStatus.MANDATORY)
        h50 = CoreHit(c_gene_sctc, "h20", 10, "replicon_1", 50, 1.0, 20.0, 1.0, 1.0, 10, 20)
        v_h50 = ModelHit(h50, gene_2, GeneStatus.ACCESSORY)
        hit_weights = HitWeight(**cfg.hit_weights())
        c1 = Cluster([v_h10, v_h20], model, hit_weights)
        c2 = Cluster([v_h40, v_h50], model, hit_weights)
        r_c = RejectedCandidate(model, [c1, c2], ["The reasons to reject this candidate"])

        model_fam_name = 'foo'
        model_vers = '0.0b2'
        rej_cand_str = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# Rejected candidates:

Cluster:
- model = T2SS
- replicon = replicon_1
- hits = (h10, gspD, 10), (h20, sctC, 20)
Cluster:
- model = T2SS
- replicon = replicon_1
- hits = (h10, gspD, 40), (h20, sctC, 50)
This candidate has been rejected because:
\t- The reasons to reject this candidate
============================================================
"""

        f_out = StringIO()
        rejected_candidates_to_txt(model_fam_name, model_vers, [r_c], f_out)
        self.maxDiff = None
        self.assertMultiLineEqual(rej_cand_str, f_out.getvalue())

        rej_cand_str = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# No Rejected candidates
"""
        f_out = StringIO()
        rejected_candidates_to_txt(model_fam_name, model_vers, [], f_out)
        self.assertMultiLineEqual(rej_cand_str, f_out.getvalue())

        # test with skipped replicons
        rej_cand_str = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
#
# WARNING: The replicon 'rep_1' has been SKIPPED. Cannot be solved before timeout.
# WARNING: The replicon 'rep_2' has been SKIPPED. Cannot be solved before timeout.
#
# No Rejected candidates
"""
        f_out = StringIO()
        rejected_candidates_to_txt(model_fam_name, model_vers, [], f_out, skipped_replicons=['rep_1', 'rep_2'])
        self.maxDiff = None
        self.assertMultiLineEqual(rej_cand_str, f_out.getvalue())


    def test_loners_to_tsv(self):
        args = argparse.Namespace()
        args.sequence_db = self.find_data("base", "test_1.fasta")
        args.db_type = 'gembase'
        args.models_dir = self.find_data('models')
        cfg = Config(MacsyDefaults(), args)

        model_name = 'foo'
        models_location = ModelLocation(path=os.path.join(args.models_dir, model_name))

        # we need to reset the ProfileFactory
        # because it's a like a singleton
        # so other tests are influenced by ProfileFactory and it's configuration
        # for instance search_genes get profile without hmmer_exe
        profile_factory = ProfileFactory(cfg)
        model = Model("foo/T2SS", 10)

        gene_name = "gspD"
        cg_gspd = CoreGene(models_location, gene_name, profile_factory)
        mg_gspd = ModelGene(cg_gspd, model, loner=True)

        gene_name = "sctJ"
        cg_sctj = CoreGene(models_location, gene_name, profile_factory)
        mg_sctj = ModelGene(cg_sctj, model)

        gene_name = "abc"
        cg_abc = CoreGene(models_location, gene_name, profile_factory)
        mg_abc = ModelGene(cg_abc, model)

        model.add_mandatory_gene(mg_gspd)
        model.add_accessory_gene(mg_sctj)
        model.add_accessory_gene(mg_abc)

        chit_abc = CoreHit(cg_abc, "hit_abc", 803, "replicon_id", 3, 1.0, 1.0, 1.0, 1.0, 10, 20)
        chit_sctj = CoreHit(cg_sctj, "hit_sctj", 803, "replicon_id", 4, 1.0, 1.0, 1.0, 1.0, 10, 20)
        chit_gspd1 = CoreHit(cg_gspd, "hit_gspd1", 803, "replicon_id", 20, 1.0, 2.0, 1.0, 1.0, 10, 20)
        chit_gspd2 = CoreHit(cg_gspd, "hit_gspd2", 803, "replicon_id", 30, 1.0, 3.0, 1.0, 1.0, 10, 20)
        mhit_abc = ModelHit(chit_abc, mg_abc, GeneStatus.ACCESSORY)
        mhit_sctj = ModelHit(chit_sctj, mg_sctj, GeneStatus.ACCESSORY)
        mhit_gspd1 = ModelHit(chit_gspd1, mg_gspd, GeneStatus.MANDATORY)
        mhit_gspd2 = ModelHit(chit_gspd2, mg_gspd, GeneStatus.MANDATORY)
        l_gspd1 = Loner(mhit_gspd1, counterpart=[mhit_gspd2])
        system_1 = System(model,
                          [Cluster([mhit_abc, mhit_sctj], model, HitWeight(**cfg.hit_weights())),
                           Cluster([l_gspd1], model, HitWeight(**cfg.hit_weights()))],
                          cfg.redundancy_penalty())
        model_fam_name = 'foo'
        model_vers = '0.0b2'
        loner_tsv = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# Loners found:
"""
        loner_tsv += "\t".join(['replicon', 'model_fqn', 'function', 'gene_name', 'hit_id', 'hit_pos', 'hit_status',
                                 'hit_seq_len', 'hit_i_eval', 'hit_score', 'hit_profile_cov',
                                 'hit_seq_cov', 'hit_begin_match', 'hit_end_match'])
        loner_tsv += "\n"
        loner_tsv += "\t".join(['replicon_id', 'foo/T2SS', 'gspD', 'gspD', 'hit_gspd1', '20', 'mandatory', '803',
                                 '1.000e+00', '2.000', '1.000', '1.000', '10', '20'])
        loner_tsv += "\n"
        loner_tsv += "\t".join(['replicon_id', 'foo/T2SS', 'gspD', 'gspD', 'hit_gspd2', '30', 'mandatory', '803',
                                 '1.000e+00', '3.000', '1.000', '1.000', '10', '20'])
        loner_tsv += "\n\n"

        f_out = StringIO()
        loners_to_tsv(model_fam_name, model_vers, [system_1], f_out)
        self.assertMultiLineEqual(loner_tsv, f_out.getvalue())

        # test No system found
        system_str = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# No Loners found
"""
        f_out = StringIO()
        loners_to_tsv(model_fam_name, model_vers, [], f_out)
        self.assertMultiLineEqual(system_str, f_out.getvalue())

        # test No loners
        loner_tsv = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# No Loners found
"""
        system_2 = System(model,
                          [Cluster([mhit_abc, mhit_sctj], model, HitWeight(**cfg.hit_weights()))],
                          cfg.redundancy_penalty())
        f_out = StringIO()
        loners_to_tsv(model_fam_name, model_vers, [system_2], f_out)
        self.assertMultiLineEqual(loner_tsv, f_out.getvalue())


    def test_multisystem_to_tsv(self):
        args = argparse.Namespace()
        args.sequence_db = self.find_data("base", "test_1.fasta")
        args.db_type = 'gembase'
        args.models_dir = self.find_data('models')
        cfg = Config(MacsyDefaults(), args)

        model_name = 'foo'
        models_location = ModelLocation(path=os.path.join(args.models_dir, model_name))

        # we need to reset the ProfileFactory
        # because it's a like a singleton
        # so other tests are influenced by ProfileFactory and it's configuration
        # for instance search_genes get profile without hmmer_exe
        profile_factory = ProfileFactory(cfg)
        model = Model("foo/T2SS", 10)

        gene_name = "gspD"
        cg_gspd = CoreGene(models_location, gene_name, profile_factory)
        mg_gspd = ModelGene(cg_gspd, model, multi_system=True)

        gene_name = "sctJ"
        cg_sctj = CoreGene(models_location, gene_name, profile_factory)
        mg_sctj = ModelGene(cg_sctj, model)

        gene_name = "abc"
        cg_abc = CoreGene(models_location, gene_name, profile_factory)
        mg_abc = ModelGene(cg_abc, model)

        model.add_mandatory_gene(mg_gspd)
        model.add_accessory_gene(mg_sctj)
        model.add_accessory_gene(mg_abc)

        chit_abc = CoreHit(cg_abc, "hit_abc", 803, "replicon_id", 3, 1.0, 1.0, 1.0, 1.0, 10, 20)
        chit_sctj = CoreHit(cg_sctj, "hit_sctj", 803, "replicon_id", 4, 1.0, 1.0, 1.0, 1.0, 10, 20)
        chit_gspd1 = CoreHit(cg_gspd, "hit_gspd1", 803, "replicon_id", 20, 1.0, 2.0, 1.0, 1.0, 10, 20)
        chit_gspd2 = CoreHit(cg_gspd, "hit_gspd2", 803, "replicon_id", 30, 1.0, 3.0, 1.0, 1.0, 10, 20)
        mhit_abc = ModelHit(chit_abc, mg_abc, GeneStatus.ACCESSORY)
        mhit_sctj = ModelHit(chit_sctj, mg_sctj, GeneStatus.ACCESSORY)
        mhit_gspd1 = ModelHit(chit_gspd1, mg_gspd, GeneStatus.MANDATORY)
        mhit_gspd2 = ModelHit(chit_gspd2, mg_gspd, GeneStatus.MANDATORY)
        l_gspd1 = MultiSystem(mhit_gspd1, counterpart=[mhit_gspd2])
        system_1 = System(model,
                          [Cluster([mhit_abc, mhit_sctj], model, HitWeight(**cfg.hit_weights())),
                           Cluster([l_gspd1], model, HitWeight(**cfg.hit_weights()))],
                          cfg.redundancy_penalty())
        model_fam_name = 'foo'
        model_vers = '0.0b2'
        multisystem_tsv = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# Multisystems found:
"""
        multisystem_tsv += "\t".join(
            ['replicon', 'model_fqn', 'function', 'gene_name', 'hit_id', 'hit_pos', 'hit_status',
             'hit_seq_len', 'hit_i_eval', 'hit_score', 'hit_profile_cov',
             'hit_seq_cov', 'hit_begin_match', 'hit_end_match'])
        multisystem_tsv += "\n"
        multisystem_tsv += "\t".join(
            ['replicon_id', 'foo/T2SS', 'gspD', 'gspD', 'hit_gspd1', '20', 'mandatory', '803',
             '1.000e+00', '2.000', '1.000', '1.000', '10', '20'])
        multisystem_tsv += "\n"
        multisystem_tsv += "\t".join(
            ['replicon_id', 'foo/T2SS', 'gspD', 'gspD', 'hit_gspd2', '30', 'mandatory', '803',
             '1.000e+00', '3.000', '1.000', '1.000', '10', '20'])
        multisystem_tsv += "\n\n"

        f_out = StringIO()
        multisystems_to_tsv(model_fam_name, model_vers, [system_1], f_out)
        self.assertMultiLineEqual(multisystem_tsv,
                                  f_out.getvalue())

        # test No system found
        system_str = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# No Multisystems found
"""
        f_out = StringIO()
        multisystems_to_tsv(model_fam_name, model_vers, [], f_out)
        self.assertMultiLineEqual(system_str, f_out.getvalue())

        # test No multisystem found
        system_2 = System(model,
                          [Cluster([mhit_abc, mhit_sctj], model, HitWeight(**cfg.hit_weights()))],
                          cfg.redundancy_penalty())
        system_str = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# No Multisystems found
"""
        f_out = StringIO()
        multisystems_to_tsv(model_fam_name, model_vers, [system_2], f_out)
        self.assertMultiLineEqual(system_str, f_out.getvalue())

    def test_likely_systems_to_txt(self):
        args = argparse.Namespace()
        args.sequence_db = self.find_data("base", "test_1.fasta")
        args.db_type = 'unordered'
        args.models_dir = self.find_data('models')
        cfg = Config(MacsyDefaults(), args)

        model_name = 'foo'
        models_location = ModelLocation(path=os.path.join(args.models_dir, model_name))

        # we need to reset the ProfileFactory
        # because it's a like a singleton
        # so other tests are influenced by ProfileFactory and it's configuration
        # for instance search_genes get profile without hmmer_exe
        profile_factory = ProfileFactory(cfg)

        model = Model("foo/T2SS", 10)
        # test if id is well incremented
        gene_name = "gspD"
        c_gene_gspd = CoreGene(models_location, gene_name, profile_factory)
        gene_gspd = ModelGene(c_gene_gspd, model)
        model.add_mandatory_gene(gene_gspd)
        gene_name = "sctJ"
        c_gene_sctj = CoreGene(models_location, gene_name, profile_factory)
        gene_sctj = ModelGene(c_gene_sctj, model)
        model.add_accessory_gene(gene_sctj)
        gene_name = "sctC"
        c_gene_sctc = CoreGene(models_location, gene_name, profile_factory)
        gene_sctc = ModelGene(c_gene_sctc, model)
        model.add_neutral_gene(gene_sctc)
        gene_name = "tadZ"
        c_gene_tadz = CoreGene(models_location, gene_name, profile_factory)
        gene_tadz = ModelGene(c_gene_tadz, model)
        model.add_forbidden_gene(gene_tadz)

        hit_1 = CoreHit(c_gene_gspd, "hit_1", 803, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
        v_hit_1 = ModelHit(hit_1, gene_gspd, GeneStatus.MANDATORY)
        hit_2 = CoreHit(c_gene_sctj, "hit_2", 804, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
        v_hit_2 = ModelHit(hit_2, gene_sctj, GeneStatus.ACCESSORY)
        hit_3 = CoreHit(c_gene_sctc, "hit_3", 805, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
        v_hit_3 = ModelHit(hit_3, gene_sctc, GeneStatus.NEUTRAL)
        hit_4 = CoreHit(c_gene_tadz, "hit_4", 806, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
        v_hit_4 = ModelHit(hit_4, gene_tadz, GeneStatus.FORBIDDEN)

        system_1 = LikelySystem(model, [v_hit_1], [v_hit_2], [v_hit_3], [v_hit_4])

        model_fam_name = 'foo'
        model_vers = '0.0b2'
        system_str = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# Systems found:

This replicon contains genetic materials needed for system foo/T2SS
WARNING the quorum is reached but there is also some forbidden genes.

system id = replicon_id_T2SS_1
model = foo/T2SS
replicon = replicon_id
hits = [('hit_1', 'gspD', 1), ('hit_2', 'sctJ', 1), ('hit_3', 'sctC', 1), ('hit_4', 'tadZ', 1)]
wholeness = 1.000

mandatory genes:
\t- gspD: 1 (gspD)

accessory genes:
\t- sctJ: 1 (sctJ)

neutral genes:
\t- sctC: 1 (sctC)

forbidden genes:
\t- tadZ: 1 (tadZ)

Use ordered replicon to have better prediction.

"""

        f_out = StringIO()
        track_multi_systems_hit = HitSystemTracker([system_1])
        likely_systems_to_txt(model_fam_name, model_vers, [system_1], track_multi_systems_hit, f_out)
        self.assertMultiLineEqual(system_str, f_out.getvalue())

        f_out = StringIO()
        likely_systems_to_txt(model_fam_name, model_vers, [], track_multi_systems_hit, f_out)
        expected_out = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# No Likely Systems found
"""
        self.assertEqual(expected_out, f_out.getvalue())


    def test_likely_systems_to_tsv(self):
        args = argparse.Namespace()
        args.sequence_db = self.find_data("base", "test_1.fasta")
        args.db_type = 'unordered'
        args.models_dir = self.find_data('models')
        cfg = Config(MacsyDefaults(), args)

        model_name = 'foo'
        models_location = ModelLocation(path=os.path.join(args.models_dir, model_name))

        # we need to reset the ProfileFactory
        # because it's a like a singleton
        # so other tests are influenced by ProfileFactory and it's configuration
        # for instance search_genes get profile without hmmer_exe
        profile_factory = ProfileFactory(cfg)

        model = Model("foo/T2SS", 10)
        # test if id is well incremented
        gene_name = "gspD"
        c_gene_gspd = CoreGene(models_location, gene_name, profile_factory)
        gene_gspd = ModelGene(c_gene_gspd, model)
        model.add_mandatory_gene(gene_gspd)
        gene_name = "sctJ"
        c_gene_sctj = CoreGene(models_location, gene_name, profile_factory)
        gene_sctj = ModelGene(c_gene_sctj, model)
        model.add_accessory_gene(gene_sctj)
        gene_name = "sctC"
        c_gene_sctc = CoreGene(models_location, gene_name, profile_factory)
        gene_sctc = ModelGene(c_gene_sctc, model)
        model.add_neutral_gene(gene_sctc)
        gene_name = "tadZ"
        c_gene_tadz = CoreGene(models_location, gene_name, profile_factory)
        gene_tadz = ModelGene(c_gene_tadz, model)
        model.add_forbidden_gene(gene_tadz)

        hit_1 = CoreHit(c_gene_gspd, "hit_1", 803, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
        v_hit_1 = ModelHit(hit_1, gene_gspd, GeneStatus.MANDATORY)
        hit_2 = CoreHit(c_gene_sctj, "hit_2", 804, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
        v_hit_2 = ModelHit(hit_2, gene_sctj, GeneStatus.ACCESSORY)
        hit_3 = CoreHit(c_gene_sctc, "hit_3", 805, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
        v_hit_3 = ModelHit(hit_3, gene_sctc, GeneStatus.NEUTRAL)
        hit_4 = CoreHit(c_gene_tadz, "hit_4", 806, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
        v_hit_4 = ModelHit(hit_4, gene_tadz, GeneStatus.FORBIDDEN)

        system_1 = LikelySystem(model, [v_hit_1], [v_hit_2], [v_hit_3], [v_hit_4])

        model_fam_name = 'foo'
        model_vers = '0.0b2'
        sol_tsv = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# Likely Systems found:
"""
        sol_tsv += "\n"
        sol_tsv += "# This replicon contains genetic materials needed for system foo/T2SS\n"
        sol_tsv += "# WARNING the quorum is reached but there is also some forbidden genes."
        sol_tsv += "\n"
        sol_tsv += "\t".join(["replicon", "hit_id", "gene_name", "hit_pos", "model_fqn", "sys_id", "sys_wholeness",
                              "hit_gene_ref", "hit_status", "hit_seq_len", "hit_i_eval", "hit_score",
                              "hit_profile_cov", "hit_seq_cov", "hit_begin_match", "hit_end_match", "used_in"])
        sol_tsv += "\n"
        sol_tsv += '\t'.join(["replicon_id", "hit_1", "gspD", "1", "foo/T2SS", "replicon_id_T2SS_1", "1.000",
                              "gspD", "mandatory", "803", "1.0", "1.000", "1.000", "1.000", "10", "20", ""])
        sol_tsv += "\n"
        sol_tsv += '\t'.join(["replicon_id", "hit_2", "sctJ", "1", "foo/T2SS", "replicon_id_T2SS_1", "1.000",
                              "sctJ", "accessory", "804", "1.0", "1.000", "1.000", "1.000", "10", "20", ""])
        sol_tsv += "\n"
        sol_tsv += '\t'.join(["replicon_id", "hit_4", "tadZ", "1", "foo/T2SS", "replicon_id_T2SS_1", "1.000",
                              "tadZ", "forbidden", "806", "1.0", "1.000", "1.000", "1.000", "10", "20", ""])
        sol_tsv += "\n"
        sol_tsv += '\t'.join(["replicon_id", "hit_3", "sctC", "1", "foo/T2SS", "replicon_id_T2SS_1", "1.000",
                              "sctC", "neutral", "805", "1.0", "1.000", "1.000", "1.000", "10", "20", ""])
        sol_tsv += "\n"
        sol_tsv += "\n"

        f_out = StringIO()
        track_multi_systems_hit = HitSystemTracker([system_1])
        likely_systems_to_tsv(model_fam_name, model_vers, [system_1], track_multi_systems_hit, f_out)
        self.assertMultiLineEqual(sol_tsv, f_out.getvalue())

        f_out = StringIO()
        likely_systems_to_tsv(model_fam_name, model_vers, [], track_multi_systems_hit, f_out)
        expected_out = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# No Likely Systems found
"""
        self.assertEqual(expected_out, f_out.getvalue())


        def test_likely_systems_to_tsv(self):
            args = argparse.Namespace()
            args.sequence_db = self.find_data("base", "test_1.fasta")
            args.db_type = 'unordered'
            args.models_dir = self.find_data('models')
            cfg = Config(MacsyDefaults(), args)

            model_name = 'foo'
            models_location = ModelLocation(path=os.path.join(args.models_dir, model_name))

            # we need to reset the ProfileFactory
            # because it's a like a singleton
            # so other tests are influenced by ProfileFactory and it's configuration
            # for instance search_genes get profile without hmmer_exe
            profile_factory = ProfileFactory(cfg)

            model = Model("foo/T2SS", 10)
            # test if id is well incremented
            gene_name = "gspD"
            c_gene_gspd = CoreGene(models_location, gene_name, profile_factory)
            gene_gspd = ModelGene(c_gene_gspd, model)
            model.add_mandatory_gene(gene_gspd)
            gene_name = "sctJ"
            c_gene_sctj = CoreGene(models_location, gene_name, profile_factory)
            gene_sctj = ModelGene(c_gene_sctj, model)
            model.add_accessory_gene(gene_sctj)
            gene_name = "sctC"
            c_gene_sctc = CoreGene(models_location, gene_name, profile_factory)
            gene_sctc = ModelGene(c_gene_sctc, model)
            model.add_neutral_gene(gene_sctc)
            gene_name = "tadZ"
            c_gene_tadz = CoreGene(models_location, gene_name, profile_factory)
            gene_tadz = ModelGene(c_gene_tadz, model)
            model.add_forbidden_gene(gene_tadz)

            hit_1 = CoreHit(c_gene_gspd, "hit_1", 803, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
            v_hit_1 = ModelHit(hit_1, gene_gspd, GeneStatus.MANDATORY)
            hit_2 = CoreHit(c_gene_sctj, "hit_2", 804, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
            v_hit_2 = ModelHit(hit_2, gene_sctj, GeneStatus.ACCESSORY)
            hit_3 = CoreHit(c_gene_sctc, "hit_3", 805, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
            v_hit_3 = ModelHit(hit_3, gene_sctc, GeneStatus.NEUTRAL)
            hit_4 = CoreHit(c_gene_tadz, "hit_4", 806, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
            v_hit_4 = ModelHit(hit_4, gene_tadz, GeneStatus.FORBIDDEN)

            system_1 = LikelySystem(model, [v_hit_1], [v_hit_2], [v_hit_3], [v_hit_4])

            model_fam_name = 'foo'
            model_vers = '0.0b2'
            sol_tsv = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
    # models : {model_fam_name}-{model_vers}
    # {' '.join(sys.argv)}
    # Likely Systems found:
    """
            sol_tsv += "\n"
            sol_tsv += "# This replicon contains genetic materials needed for system foo/T2SS\n"
            sol_tsv += "# WARNING the quorum is reached but there is also some forbidden genes."
            sol_tsv += "\n"
            sol_tsv += "\t".join(["replicon", "hit_id", "gene_name", "hit_pos", "model_fqn", "sys_id", "sys_wholeness",
                                  "hit_gene_ref", "hit_status", "hit_seq_len", "hit_i_eval", "hit_score",
                                  "hit_profile_cov", "hit_seq_cov", "hit_begin_match", "hit_end_match", "used_in"])
            sol_tsv += "\n"
            sol_tsv += '\t'.join(["replicon_id", "hit_1", "gspD", "1", "foo/T2SS", "replicon_id_T2SS_1", "1.000",
                                  "gspD", "mandatory", "803", "1.0", "1.000", "1.000", "1.000", "10", "20", ""])
            sol_tsv += "\n"
            sol_tsv += '\t'.join(["replicon_id", "hit_2", "sctJ", "1", "foo/T2SS", "replicon_id_T2SS_1", "1.000",
                                  "sctJ", "accessory", "804", "1.0", "1.000", "1.000", "1.000", "10", "20", ""])
            sol_tsv += "\n"
            sol_tsv += '\t'.join(["replicon_id", "hit_4", "tadZ", "1", "foo/T2SS", "replicon_id_T2SS_1", "1.000",
                                  "tadZ", "forbidden", "806", "1.0", "1.000", "1.000", "1.000", "10", "20", ""])
            sol_tsv += "\n"
            sol_tsv += '\t'.join(["replicon_id", "hit_3", "sctC", "1", "foo/T2SS", "replicon_id_T2SS_1", "1.000",
                                  "sctC", "neutral", "805", "1.0", "1.000", "1.000", "1.000", "10", "20", ""])
            sol_tsv += "\n"
            sol_tsv += "\n"

            f_out = StringIO()
            track_multi_systems_hit = HitSystemTracker([system_1])
            likely_systems_to_tsv(model_fam_name, model_vers, [system_1], track_multi_systems_hit, f_out)
            self.assertMultiLineEqual(sol_tsv, f_out.getvalue())

            f_out = StringIO()
            likely_systems_to_tsv(model_fam_name, model_vers, [], track_multi_systems_hit, f_out)
            expected_out = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
    # models : {model_fam_name}-{model_vers}
    # {' '.join(sys.argv)}
    # No Likely Systems found
    """
            self.assertEqual(expected_out, f_out.getvalue())


    def test_unnlikely_systems_to_txt(self):
        args = argparse.Namespace()
        args.sequence_db = self.find_data("base", "test_1.fasta")
        args.db_type = 'unordered'
        args.models_dir = self.find_data('models')
        cfg = Config(MacsyDefaults(), args)

        model_name = 'foo'
        models_location = ModelLocation(path=os.path.join(args.models_dir, model_name))

        # we need to reset the ProfileFactory
        # because it's a like a singleton
        # so other tests are influenced by ProfileFactory and it's configuration
        # for instance search_genes get profile without hmmer_exe
        profile_factory = ProfileFactory(cfg)

        model = Model("foo/T2SS", 10)
        # test if id is well incremented
        gene_name = "gspD"
        c_gene_gspd = CoreGene(models_location, gene_name, profile_factory)
        gene_gspd = ModelGene(c_gene_gspd, model)
        model.add_mandatory_gene(gene_gspd)
        gene_name = "sctJ"
        c_gene_sctj = CoreGene(models_location, gene_name, profile_factory)
        gene_sctj = ModelGene(c_gene_sctj, model)
        model.add_accessory_gene(gene_sctj)
        gene_name = "sctC"
        c_gene_sctc = CoreGene(models_location, gene_name, profile_factory)
        gene_sctc = ModelGene(c_gene_sctc, model)
        model.add_neutral_gene(gene_sctc)
        gene_name = "tadZ"
        c_gene_tadz = CoreGene(models_location, gene_name, profile_factory)
        gene_tadz = ModelGene(c_gene_tadz, model)
        model.add_forbidden_gene(gene_tadz)

        hit_1 = CoreHit(c_gene_gspd, "hit_1", 803, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
        v_hit_1 = ModelHit(hit_1, gene_gspd, GeneStatus.MANDATORY)
        hit_2 = CoreHit(c_gene_sctj, "hit_2", 804, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
        v_hit_2 = ModelHit(hit_2, gene_sctj, GeneStatus.ACCESSORY)
        hit_3 = CoreHit(c_gene_sctc, "hit_3", 805, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
        v_hit_3 = ModelHit(hit_3, gene_sctc, GeneStatus.NEUTRAL)
        hit_4 = CoreHit(c_gene_tadz, "hit_4", 806, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
        v_hit_4 = ModelHit(hit_4, gene_tadz, GeneStatus.FORBIDDEN)
        reason = "why it not a system"
        system_1 = UnlikelySystem(model, [v_hit_1], [v_hit_2], [v_hit_3], [v_hit_4], reason)

        model_fam_name = 'foo'
        model_vers = '0.0b2'

        exp_txt = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# Unlikely Systems found:

This replicon probably not contains a system foo/T2SS:
{reason}

system id = replicon_id_T2SS_1
model = foo/T2SS
replicon = replicon_id
hits = [('hit_1', 'gspD', 1), ('hit_2', 'sctJ', 1), ('hit_3', 'sctC', 1), ('hit_4', 'tadZ', 1)]
wholeness = 1.000

mandatory genes:
\t- gspD: 1 (gspD)

accessory genes:
\t- sctJ: 1 (sctJ)

neutral genes:
\t- sctC: 1 (sctC)

forbidden genes:
\t- tadZ: 1 (tadZ)

Use ordered replicon to have better prediction.

============================================================
"""

        f_out = StringIO()
        unlikely_systems_to_txt(model_fam_name, model_vers, [system_1], f_out)
        self.assertMultiLineEqual(exp_txt, f_out.getvalue())

        f_out = StringIO()
        unlikely_systems_to_txt(model_fam_name, model_vers, [], f_out)
        expected_out = f"""# macsylib {macsylib.__version__} {macsylib.__commit__}
# models : {model_fam_name}-{model_vers}
# {' '.join(sys.argv)}
# No Unlikely Systems found
"""
        self.assertEqual(expected_out, f_out.getvalue())


    def test_loner_warning(self):
        args = argparse.Namespace()
        args.sequence_db = self.find_data("base", "test_1.fasta")
        args.db_type = 'gembase'
        args.models_dir = self.find_data('models')
        cfg = Config(MacsyDefaults(), args)

        model_name = 'foo'
        models_location = ModelLocation(path=os.path.join(args.models_dir, model_name))

        # we need to reset the ProfileFactory
        # because it's a like a singleton
        # so other tests are influenced by ProfileFactory and it's configuration
        # for instance search_genes get profile without hmmer_exe
        profile_factory = ProfileFactory(cfg)

        model = Model("foo/T2SS", 10)
        c_gene_gspd = CoreGene(models_location, 'gspD', profile_factory)
        c_gene_sctj = CoreGene(models_location, 'sctJ', profile_factory)
        c_gene_tadz = CoreGene(models_location, 'tadZ', profile_factory)

        gene_gspd = ModelGene(c_gene_gspd, model)
        gene_sctj = ModelGene(c_gene_sctj, model)
        gene_tadz = ModelGene(c_gene_tadz, model, loner=True)

        model.add_mandatory_gene(gene_gspd)
        model.add_accessory_gene(gene_sctj)
        model.add_accessory_gene(gene_tadz)

        hit_1 = CoreHit(c_gene_gspd, "hit_1", 803, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
        v_hit_1 = ModelHit(hit_1, gene_gspd, GeneStatus.MANDATORY)
        hit_2 = CoreHit(c_gene_sctj, "hit_2", 803, "replicon_id", 1, 1.0, 1.0, 1.0, 1.0, 10, 20)
        v_hit_2 = ModelHit(hit_2, gene_sctj, GeneStatus.ACCESSORY)
        hit_3 = CoreHit(c_gene_tadz, "hit_3", 803, "replicon_id", 30, 1.0, 1.0, 1.0, 1.0, 10, 20)
        loner_1 = Loner(hit_3, gene_tadz, GeneStatus.ACCESSORY)
        hit_4 = CoreHit(c_gene_gspd, "hit_4", 803, "replicon_id", 40, 1.0, 1.0, 1.0, 1.0, 10, 20)
        mhit_4 = ModelHit(hit_4, gene_gspd, GeneStatus.MANDATORY)
        hit_5 = CoreHit(c_gene_sctj, "hit_5", 803, "replicon_id", 41, 1.0, 1.0, 1.0, 1.0, 10, 20)
        mhit_5 = ModelHit(hit_5, gene_sctj, GeneStatus.ACCESSORY)

        system_1 = System(model,
                  [Cluster([v_hit_1, v_hit_2], model, HitWeight(**cfg.hit_weights())),
                           Cluster([loner_1], model, HitWeight(**cfg.hit_weights()))],
                          cfg.redundancy_penalty())

        system_2 = System(model,
                          [Cluster([mhit_4, mhit_5], model, HitWeight(**cfg.hit_weights())),
                           Cluster([loner_1], model, HitWeight(**cfg.hit_weights()))],
                          cfg.redundancy_penalty())
        warnings = loner_warning([system_1, system_2])
        self.assertListEqual(warnings,
                             ["# WARNING Loner: there is only 1 occurrence(s) of loner 'tadZ' and 2 potential systems [replicon_id_T2SS_1, replicon_id_T2SS_2]"])

        # The loner is also multisystem -> no warning
        model = Model("foo/T2SS", 10)
        gene_gspd = ModelGene(c_gene_gspd, model)
        gene_sctj = ModelGene(c_gene_sctj, model)
        gene_tadz = ModelGene(c_gene_tadz, model, loner=True, multi_system=True)
        model.add_mandatory_gene(gene_gspd)
        model.add_accessory_gene(gene_sctj)
        model.add_accessory_gene(gene_tadz)

        loner_ms_1 = LonerMultiSystem(hit_3, gene_tadz, GeneStatus.ACCESSORY)
        system_3 = System(model,
                          [Cluster([v_hit_1, v_hit_2], model, HitWeight(**cfg.hit_weights())),
                           Cluster([loner_ms_1], model, HitWeight(**cfg.hit_weights()))],
                          cfg.redundancy_penalty())

        system_4 = System(model,
                          [Cluster([mhit_4, mhit_5], model, HitWeight(**cfg.hit_weights())),
                           Cluster([loner_ms_1], model, HitWeight(**cfg.hit_weights()))],
                          cfg.redundancy_penalty())
        warnings = loner_warning([system_3, system_4])
        self.assertListEqual(warnings, [])

        # there is one loner and one system -> no warning
        warnings = loner_warning([system_1])
        self.assertListEqual(warnings, [])
