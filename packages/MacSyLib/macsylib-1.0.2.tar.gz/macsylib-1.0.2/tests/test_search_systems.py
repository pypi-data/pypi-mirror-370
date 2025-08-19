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


import os
import unittest
import logging
import shutil
import argparse
import tempfile
import itertools

import macsylib
from macsylib.config import MacsyDefaults, Config
from macsylib.search_systems import search_systems, search_in_unordered_replicon
from macsylib.utils import get_def_to_detect
from macsylib.system import System, AbstractUnordered, RejectedCandidate
from macsylib.registries import scan_models_dir, ModelRegistry
from macsylib.model import ModelBank
from macsylib.gene import GeneBank
from macsylib.profile import ProfileFactory
from macsylib.definition_parser import DefinitionParser
from macsylib.database import Indexes
from macsylib.hit import CoreHit

from tests import MacsyTest


class TestSearchSystems(MacsyTest):

    def setUp(self):
        self._tmp_dir = tempfile.TemporaryDirectory(prefix='test_msl_macsylib_')
        self.tmp_dir = self._tmp_dir.name
        self._reset_id()


    def tearDown(self):
        self._tmp_dir.cleanup()


    def _reset_id(self):
        """
        reset System._id and RejectedCluster._id to get predictable ids
        """
        System._id = itertools.count(1)
        RejectedCandidate._id = itertools.count(1)
        AbstractUnordered._id = itertools.count(1)


    def _fill_model_registry(self, config):
        model_registry = ModelRegistry()

        for model_dir in config.models_dir():
            models_loc_available = scan_models_dir(model_dir,
                                                   profile_suffix=config.profile_suffix(),
                                                   relative_path=config.relative_path())
            for model_loc in models_loc_available:
                model_registry.add(model_loc)
        return model_registry


    @unittest.skipIf(not shutil.which('hmmsearch'), 'hmmsearch not found in PATH')
    def test_search_systems_unordered(self):
        logger = logging.getLogger('macsylib')
        macsylib.logger_set_level(level='ERROR')
        defaults = MacsyDefaults()

        seq_db = self.find_data('base', 'VICH001.B.00001.C001.prt')
        models_dir = self.find_data('data_set', 'models')
        args = argparse.Namespace()
        args.models_dir = models_dir
        args.sequence_db = seq_db
        args.db_type = 'unordered'
        args.models = ['set_1', 'all']
        args.worker = 4
        args.out_dir = self.tmp_dir
        args.index_dir = self.tmp_dir

        config = Config(defaults, args)

        model_registry = self._fill_model_registry(config)
        def_to_detect, models_fam_name, models_version = get_def_to_detect(config.models(), model_registry)
        systems, uncomplete_sys = search_systems(config, model_registry, def_to_detect, logger)
        expected_sys_id = ['VICH001.B.00001.C001_T2SS_4', 'VICH001.B.00001.C001_MSH_3',
                           'VICH001.B.00001.C001_T4P_5', 'VICH001.B.00001.C001_T4bP_6']
        self.assertListEqual([s.id for s in systems], expected_sys_id)

        expected_uncomplete_sys_id = ['VICH001.B.00001.C001_Archaeal-T4P_1', 'VICH001.B.00001.C001_ComM_2',
                                      'VICH001.B.00001.C001_Tad_7']
        self.assertListEqual([s.id for s in uncomplete_sys], expected_uncomplete_sys_id)


    @unittest.skipIf(not shutil.which('hmmsearch'), 'hmmsearch not found in PATH')
    def test_search_systems_ordered(self):
        logger = logging.getLogger('macsylib')
        macsylib.logger_set_level(level='ERROR')
        defaults = MacsyDefaults()

        # test ordered replicon
        seq_db = self.find_data('base', 'VICH001.B.00001.C001.prt')
        models_dir = self.find_data('data_set', 'models')
        args = argparse.Namespace()
        args.models_dir = models_dir
        args.sequence_db = seq_db
        args.db_type = 'ordered_replicon'
        args.models = ['set_1', 'all']
        args.worker = 4
        args.out_dir = self.tmp_dir
        args.index_dir = self.tmp_dir

        config = Config(defaults, args)

        model_registry = self._fill_model_registry(config)
        def_to_detect, models_fam_name, models_version = get_def_to_detect(config.models(), model_registry)

        systems, rejected_clst = search_systems(config, model_registry, def_to_detect, logger)
        expected_sys_id = ['VICH001.B.00001.C001_MSH_1',
                           'VICH001.B.00001.C001_T4P_13', 'VICH001.B.00001.C001_T4P_11', 'VICH001.B.00001.C001_T4P_9',
                           'VICH001.B.00001.C001_T4P_10', 'VICH001.B.00001.C001_T4P_5', 'VICH001.B.00001.C001_T4P_4',
                           'VICH001.B.00001.C001_T4bP_14', 'VICH001.B.00001.C001_T4P_12', 'VICH001.B.00001.C001_T4P_6',
                           'VICH001.B.00001.C001_T4P_7', 'VICH001.B.00001.C001_T4P_8',
                           'VICH001.B.00001.C001_T2SS_3', 'VICH001.B.00001.C001_T2SS_2']

        self.assertListEqual([s.id for s in systems], expected_sys_id)

        expected_scores = [10.5, 12.0, 9.5, 9.0, 8.5, 6.0, 5.0, 5.5, 10.5, 7.5, 7.0, 8.0, 8.06, 7.5]
        self.assertListEqual([s.score for s in systems], expected_scores)
        self.assertEqual(len(rejected_clst), 10)


    def test_hits_but_no_systems(self):
        # test hits but No Systems
        logger = logging.getLogger('macsylib')
        macsylib.logger_set_level(level='ERROR')
        defaults = MacsyDefaults()

        # test ordered replicon
        seq_db = self.find_data('base', 'VICH001.B.00001.C001.prt')
        models_dir = self.find_data('data_set', 'models')
        args = argparse.Namespace()
        args.models_dir = models_dir
        args.sequence_db = seq_db
        args.db_type = 'ordered_replicon'
        args.models = ['set_1', 'Tad']
        args.worker = 4
        args.out_dir = self.tmp_dir
        args.index_dir = self.tmp_dir

        config = Config(defaults, args)
        model_registry = self._fill_model_registry(config)
        def_to_detect, models_fam_name, models_version = get_def_to_detect(config.models(), model_registry)
        self._reset_id()
        systems, rejected_clst = search_systems(config, model_registry, def_to_detect, logger)
        self.assertEqual(systems, [])

        # [rc.id, [hits.id], [reasons]]
        expected_rejected_clst = [
            ('VICH001.B.00001.C001_Tad_1',
             ['VICH001.B.00001.C001_00409', 'VICH001.B.00001.C001_00412'],
             ['The quorum of mandatory genes required (4) is not reached: 2', 'The quorum of genes required (6) is not reached: 2']),
            ('VICH001.B.00001.C001_Tad_2',
             ['VICH001.B.00001.C001_00829', 'VICH001.B.00001.C001_00833'],
             ['The quorum of mandatory genes required (4) is not reached: 2', 'The quorum of genes required (6) is not reached: 2']),
            ('VICH001.B.00001.C001_Tad_3',
             ['VICH001.B.00001.C001_02306', 'VICH001.B.00001.C001_02307', 'VICH001.B.00001.C001_02308'],
             ['The quorum of mandatory genes required (4) is not reached: 3', 'The quorum of genes required (6) is not reached: 3']),
            ('VICH001.B.00001.C001_Tad_4',
             ['VICH001.B.00001.C001_02599', 'VICH001.B.00001.C001_02600'],
             ['The quorum of mandatory genes required (4) is not reached: 2', 'The quorum of genes required (6) is not reached: 2']),
            ('VICH001.B.00001.C001_Tad_5',
             ['VICH001.B.00001.C001_00409', 'VICH001.B.00001.C001_00412', 'VICH001.B.00001.C001_00829', 'VICH001.B.00001.C001_00833'],
             ['The quorum of mandatory genes required (4) is not reached: 3', 'The quorum of genes required (6) is not reached: 3']),
            ('VICH001.B.00001.C001_Tad_6',
             ['VICH001.B.00001.C001_00409', 'VICH001.B.00001.C001_00412', 'VICH001.B.00001.C001_02306', 'VICH001.B.00001.C001_02307',
              'VICH001.B.00001.C001_02308'],
             ['The quorum of genes required (6) is not reached: 4']),
            ('VICH001.B.00001.C001_Tad_7',
             ['VICH001.B.00001.C001_00409', 'VICH001.B.00001.C001_00412', 'VICH001.B.00001.C001_02599', 'VICH001.B.00001.C001_02600'],
             ['The quorum of mandatory genes required (4) is not reached: 3', 'The quorum of genes required (6) is not reached: 3']),
            ('VICH001.B.00001.C001_Tad_8',
             ['VICH001.B.00001.C001_00829', 'VICH001.B.00001.C001_00833', 'VICH001.B.00001.C001_02306', 'VICH001.B.00001.C001_02307',
              'VICH001.B.00001.C001_02308'],
             ['The quorum of mandatory genes required (4) is not reached: 3', 'The quorum of genes required (6) is not reached: 3']),
            ('VICH001.B.00001.C001_Tad_9',
             ['VICH001.B.00001.C001_00829', 'VICH001.B.00001.C001_00833', 'VICH001.B.00001.C001_02599', 'VICH001.B.00001.C001_02600'],
             ['The quorum of mandatory genes required (4) is not reached: 3', 'The quorum of genes required (6) is not reached: 3']),
            ('VICH001.B.00001.C001_Tad_10',
             ['VICH001.B.00001.C001_02306', 'VICH001.B.00001.C001_02307', 'VICH001.B.00001.C001_02308', 'VICH001.B.00001.C001_02599',
              'VICH001.B.00001.C001_02600'],
             ['The quorum of mandatory genes required (4) is not reached: 3', 'The quorum of genes required (6) is not reached: 3']),
            ('VICH001.B.00001.C001_Tad_11',
             ['VICH001.B.00001.C001_00409', 'VICH001.B.00001.C001_00412', 'VICH001.B.00001.C001_00829', 'VICH001.B.00001.C001_00833',
              'VICH001.B.00001.C001_02306', 'VICH001.B.00001.C001_02307', 'VICH001.B.00001.C001_02308'],
             ['The quorum of genes required (6) is not reached: 4']),
            ('VICH001.B.00001.C001_Tad_12',
             ['VICH001.B.00001.C001_00409', 'VICH001.B.00001.C001_00412', 'VICH001.B.00001.C001_00829', 'VICH001.B.00001.C001_00833',
              'VICH001.B.00001.C001_02599', 'VICH001.B.00001.C001_02600'],
             ['The quorum of genes required (6) is not reached: 4']),
            ('VICH001.B.00001.C001_Tad_13',
             ['VICH001.B.00001.C001_00409', 'VICH001.B.00001.C001_00412', 'VICH001.B.00001.C001_02306', 'VICH001.B.00001.C001_02307',
              'VICH001.B.00001.C001_02308', 'VICH001.B.00001.C001_02599', 'VICH001.B.00001.C001_02600'],
             ['The quorum of genes required (6) is not reached: 4']),
            ('VICH001.B.00001.C001_Tad_14',
             ['VICH001.B.00001.C001_00829', 'VICH001.B.00001.C001_00833', 'VICH001.B.00001.C001_02306', 'VICH001.B.00001.C001_02307',
              'VICH001.B.00001.C001_02308', 'VICH001.B.00001.C001_02599', 'VICH001.B.00001.C001_02600'],
             ['The quorum of mandatory genes required (4) is not reached: 3', 'The quorum of genes required (6) is not reached: 3']),
            ('VICH001.B.00001.C001_Tad_15',
             ['VICH001.B.00001.C001_00409', 'VICH001.B.00001.C001_00412', 'VICH001.B.00001.C001_00829', 'VICH001.B.00001.C001_00833',
              'VICH001.B.00001.C001_02306', 'VICH001.B.00001.C001_02307', 'VICH001.B.00001.C001_02308', 'VICH001.B.00001.C001_02599',
              'VICH001.B.00001.C001_02600'],
             ['The quorum of genes required (6) is not reached: 4'])
        ]

        results = [(rc.id, [h.id for h in rc.hits], rc.reasons) for rc in rejected_clst]
        self.assertEqual(expected_rejected_clst, results)


    def test_no_hits(self):
        # test No hits
        logger = logging.getLogger('macsylib')
        macsylib.logger_set_level(level='ERROR')
        defaults = MacsyDefaults()

        # test ordered replicon
        seq_db = self.find_data('base', 'test_1.fasta')
        models_dir = self.find_data('data_set', 'models')
        args = argparse.Namespace()
        args.models_dir = models_dir
        args.sequence_db = seq_db
        args.db_type = 'ordered_replicon'
        args.models = ['set_1', 'ComM']
        args.worker = 4
        args.out_dir = self.tmp_dir
        args.index_dir = self.tmp_dir

        config = Config(defaults, args)

        model_registry = self._fill_model_registry(config)
        def_to_detect, models_fam_name, models_version = get_def_to_detect(config.models(), model_registry)
        self._reset_id()
        systems, rejected_clst = search_systems(config, model_registry, def_to_detect, logger)
        self.assertEqual(systems, [])
        self.assertEqual(rejected_clst, [])


    def test_multisystems_out_sys(self):
        # test multisystems
        # multisytem hit are not in System (to small cluster)
        # no system
        logger = logging.getLogger('macsylib')
        macsylib.logger_set_level(level='ERROR')
        defaults = MacsyDefaults()

        # test ordered replicon
        seq_db = self.find_data('base', 'test_12.fasta')
        models_dir = self.find_data('models')
        args = argparse.Namespace()
        args.models_dir = models_dir
        args.sequence_db = seq_db
        args.db_type = 'ordered_replicon'
        args.models = ['functional', 'T12SS-multisystem']
        args.worker = 4
        args.out_dir = self.tmp_dir
        args.index_dir = self.tmp_dir

        config = Config(defaults, args)
        model_registry = self._fill_model_registry(config)
        def_to_detect, models_fam_name, models_version = get_def_to_detect(config.models(), model_registry)
        self._reset_id()
        systems, rejected_clst = search_systems(config, model_registry, def_to_detect, logger)

        self.assertEqual(systems, [])
        self.assertEqual([r.id for r in rejected_clst],
                         ['test_12_T12SS-multisystem_1', 'test_12_T12SS-multisystem_2'])


    def test_multisystems_in_sys(self):
        # multisystem is in System, so it can play role for other cluster
        # 2 systems found
        logger = logging.getLogger('macsylib')
        macsylib.logger_set_level(level='ERROR')
        defaults = MacsyDefaults()

        # test ordered replicon
        seq_db = self.find_data('base', 'test_13.fasta')
        models_dir = self.find_data('models')
        args = argparse.Namespace()
        args.models_dir = models_dir
        args.sequence_db = seq_db
        args.db_type = 'ordered_replicon'
        args.models = ['functional', 'T12SS-multisystem']
        args.worker = 4
        args.out_dir = self.tmp_dir
        args.index_dir = self.tmp_dir

        config = Config(defaults, args)

        model_registry = self._fill_model_registry(config)
        def_to_detect, models_fam_name, models_version = get_def_to_detect(config.models(), model_registry)
        self._reset_id()
        systems, rejected_clst = search_systems(config, model_registry, def_to_detect, logger)
        self.assertEqual({s.id for s in systems},
                         {'test_13_T12SS-multisystem_3',
                          'test_13_T12SS-multisystem_2',
                          'test_13_T12SS-multisystem_1'})
        self.assertEqual([r.id for r in rejected_clst],
                         ['test_13_T12SS-multisystem_1'])


    def test_search_in_unordered_replicon(self):
        logger = logging.getLogger('macsylib')
        macsylib.logger_set_level(level='ERROR')
        defaults = MacsyDefaults()

        seq_db = self.find_data('base', 'VICH001.B.00001.C001.prt')
        models_dir = self.find_data('data_set', 'models')
        args = argparse.Namespace()
        args.models_dir = models_dir
        args.sequence_db = seq_db
        args.db_type = 'unordered'
        args.models = ['set_1', 'MSH']
        args.worker = 4
        args.out_dir = self.tmp_dir
        args.index_dir = self.tmp_dir

        config = Config(defaults, args)

        model_registry = self._fill_model_registry(config)
        models_def_to_detect, models_fam_name, models_version = get_def_to_detect(config.models(), model_registry)

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

        models_to_detect = [model_bank[model_loc.fqn] for model_loc in models_def_to_detect]

        rep_name = 'VICH001.B.00001.C001'
        mod_msh = models_to_detect[0]
        ch_msha = CoreHit(mod_msh.get_gene('MSH_mshA').core_gene ,
                          'VICH001.B.00001.C001_00416',
                          178,
                          rep_name,
                          376,
                          4.500e-36, 120.400, 0.948, 0.534,
                          9, 103)
        ch_mshe =  CoreHit(mod_msh.get_gene('MSH_mshE').core_gene ,
                          'VICH001.B.00001.C001_00412',
                          575,
                          rep_name,
                          372,
                          4.800e-228,753.900,0.998,0.727,
                          142, 559)
        ch_mshg = CoreHit(mod_msh.get_gene('MSH_mshG').core_gene,
                          'VICH001.B.00001.C001_02307',
                          408,
                          rep_name,
                          2204,
                          7.500e-76, 252.600, 0.994, 0.819,
                          71, 404
                          )
        ch_mshl = CoreHit(mod_msh.get_gene('MSH_mshL').core_gene,
                          'VICH001.B.00001.C001_02505',
                          578,
                          rep_name,
                          2394,
                          1.200e-22, 77.300, 0.886, 0.279,
                          416, 576
                          )
        ch_mshm = CoreHit(mod_msh.get_gene('MSH_mshM').core_gene,
                          'VICH001.B.00001.C001_00410',
                          281,
                          rep_name,
                          370,
                          1.800e-129, 428.000, 1.000, 0.940,
                          1, 264
                          )
        ch_mshb = CoreHit(mod_msh.get_gene('MSH_mshB').core_gene,
                          'VICH001.B.00001.C001_00415',
                          196,
                          rep_name,
                          375,
                          1.600e-35, 118.500,1.000, 0.388,
                          18,93
                          )
        ch_mshc = CoreHit(mod_msh.get_gene('MSH_mshC').core_gene,
                          'VICH001.B.00001.C001_00415',
                          196,
                          rep_name,
                          375,
                          5.300e-11, 40.100, 0.553, 0.214,
                          18, 59
                          )
        ch_mshd = CoreHit(mod_msh.get_gene('MSH_mshD').core_gene,
                          'VICH001.B.00001.C001_00416',
                          178,
                          rep_name,
                          376,
                          1.200e-07, 28.900, 0.518, 0.163,
                          9, 37
                          )

        hits_by_replicon = {rep_name: [ch_msha, ch_mshe, ch_mshg, ch_mshl, ch_mshm, ch_mshb, ch_mshc, ch_mshd]}

        likely_systems, unlikely_systems = search_in_unordered_replicon(hits_by_replicon, models_to_detect, logger)

        self.assertEqual(len(likely_systems), 1)
        self.assertEqual(likely_systems[0].id, 'VICH001.B.00001.C001_MSH_1')
        self.assertListEqual(likely_systems[0].hits, [ch_mshm, ch_mshe, ch_mshb, ch_mshc, ch_msha, ch_mshd, ch_mshg, ch_mshl])
        self.assertEqual(unlikely_systems, [])

    def test_search_in_unordered_replicon_no_systems(self):
        logger = logging.getLogger('macsylib')
        macsylib.logger_set_level(level='ERROR')
        defaults = MacsyDefaults()

        seq_db = self.find_data('base', 'VICH001.B.00001.C001.prt')
        models_dir = self.find_data('data_set', 'models')
        args = argparse.Namespace()
        args.models_dir = models_dir
        args.sequence_db = seq_db
        args.db_type = 'unordered'
        args.models = ['set_1', 'MSH']
        args.worker = 4
        args.out_dir = self.tmp_dir
        args.index_dir = self.tmp_dir

        config = Config(defaults, args)

        model_registry = self._fill_model_registry(config)
        models_def_to_detect, models_fam_name, models_version = get_def_to_detect(config.models(), model_registry)

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

        models_to_detect = [model_bank[model_loc.fqn] for model_loc in models_def_to_detect]

        rep_name = 'VICH001.B.00001.C001'
        mod_msh = models_to_detect[0]
        ch_mshe =  CoreHit(mod_msh.get_gene('MSH_mshE').core_gene ,
                          'VICH001.B.00001.C001_00412',
                          575,
                          rep_name,
                          372,
                          4.800e-228,753.900,0.998,0.727,
                          142, 559)
        ch_mshg = CoreHit(mod_msh.get_gene('MSH_mshG').core_gene,
                          'VICH001.B.00001.C001_02307',
                          408,
                          rep_name,
                          2204,
                          7.500e-76, 252.600, 0.994, 0.819,
                          71, 404
                          )
        ch_mshb = CoreHit(mod_msh.get_gene('MSH_mshB').core_gene,
                          'VICH001.B.00001.C001_00415',
                          196,
                          rep_name,
                          375,
                          1.600e-35, 118.500,1.000, 0.388,
                          18,93
                          )
        ch_mshc = CoreHit(mod_msh.get_gene('MSH_mshC').core_gene,
                          'VICH001.B.00001.C001_00415',
                          196,
                          rep_name,
                          375,
                          5.300e-11, 40.100, 0.553, 0.214,
                          18, 59
                          )

        hits_by_replicon = {rep_name: [ch_mshe, ch_mshg, ch_mshb, ch_mshc]}
        likely_systems, unlikely_systems = search_in_unordered_replicon(hits_by_replicon, models_to_detect, logger)

        self.assertEqual(len(unlikely_systems), 1)
        self.assertEqual(unlikely_systems[0].id, 'VICH001.B.00001.C001_MSH_1')
        self.assertListEqual(unlikely_systems[0].hits, [ch_mshe, ch_mshb, ch_mshc, ch_mshg])
        self.assertListEqual(unlikely_systems[0].reasons, ['The quorum of mandatory genes required (3) is not reached: 2'])
        self.assertEqual(likely_systems, [])

    def test_search_in_unordered_replicon_no_hits(self):
        logger = logging.getLogger('macsylib')
        macsylib.logger_set_level(level='ERROR')
        defaults = MacsyDefaults()

        seq_db = self.find_data('base', 'VICH001.B.00001.C001.prt')
        models_dir = self.find_data('data_set', 'models')
        args = argparse.Namespace()
        args.models_dir = models_dir
        args.sequence_db = seq_db
        args.db_type = 'unordered'
        args.models = ['set_1', 'MSH']
        args.worker = 4
        args.out_dir = self.tmp_dir
        args.index_dir = self.tmp_dir

        config = Config(defaults, args)

        model_registry = self._fill_model_registry(config)
        models_def_to_detect, models_fam_name, models_version = get_def_to_detect(config.models(), model_registry)

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

        models_to_detect = [model_bank[model_loc.fqn] for model_loc in models_def_to_detect]

        hits_by_replicon = {'VICH001.B.00001.C001': []}
        likely_systems, unlikely_systems = search_in_unordered_replicon(hits_by_replicon, models_to_detect, logger)
        self.assertEqual(likely_systems, [])
        self.assertEqual(unlikely_systems, [])


    def test_search_in_ordered_replicon(self):
        logger = logging.getLogger('macsylib')
        macsylib.logger_set_level(level='ERROR')
        defaults = MacsyDefaults()

        seq_db = self.find_data('base', 'VICH001.B.00001.C001.prt')
        models_dir = self.find_data('data_set', 'models')
        args = argparse.Namespace()
        args.models_dir = models_dir
        args.sequence_db = seq_db
        args.db_type = 'unordered'
        args.models = ['set_1', 'MSH']
        args.worker = 4
        args.out_dir = self.tmp_dir
        args.index_dir = self.tmp_dir

        config = Config(defaults, args)

        model_registry = self._fill_model_registry(config)
        models_def_to_detect, models_fam_name, models_version = get_def_to_detect(config.models(), model_registry)

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

        models_to_detect = [model_bank[model_loc.fqn] for model_loc in models_def_to_detect]

        rep_name = 'VICH001.B.00001.C001'
        mod_msh = models_to_detect[0]
        ch_msha = CoreHit(mod_msh.get_gene('MSH_mshA').core_gene ,
                          'VICH001.B.00001.C001_00416',
                          178,
                          rep_name,
                          300,
                          4.500e-36, 120.400, 0.948, 0.534,
                          9, 103)
        ch_mshe =  CoreHit(mod_msh.get_gene('MSH_mshE').core_gene ,
                          'VICH001.B.00001.C001_00412',
                          400,
                          rep_name,
                          372,
                          4.800e-228,753.900,0.998,0.727,
                          142, 559)
        ch_mshg = CoreHit(mod_msh.get_gene('MSH_mshG').core_gene,
                          'VICH001.B.00001.C001_02307',
                          404,
                          rep_name,
                          2204,
                          7.500e-76, 252.600, 0.994, 0.819,
                          71, 404
                          )
        ch_mshl = CoreHit(mod_msh.get_gene('MSH_mshL').core_gene,
                          'VICH001.B.00001.C001_02505',
                          408,
                          rep_name,
                          2394,
                          1.200e-22, 77.300, 0.886, 0.279,
                          416, 576
                          )
        ch_mshm = CoreHit(mod_msh.get_gene('MSH_mshM').core_gene,
                          'VICH001.B.00001.C001_00410',
                          412,
                          rep_name,
                          370,
                          1.800e-129, 428.000, 1.000, 0.940,
                          1, 264
                          )
        ch_mshb = CoreHit(mod_msh.get_gene('MSH_mshB').core_gene,
                          'VICH001.B.00001.C001_00415',
                          100,
                          rep_name,
                          375,
                          1.600e-35, 118.500,1.000, 0.388,
                          18,93
                          )
        ch_mshc = CoreHit(mod_msh.get_gene('MSH_mshC').core_gene,
                          'VICH001.B.00001.C001_00415',
                          104,
                          rep_name,
                          375,
                          5.300e-11, 40.100, 0.553, 0.214,
                          18, 59
                          )
        ch_mshd = CoreHit(mod_msh.get_gene('MSH_mshD').core_gene,
                          'VICH001.B.00001.C001_00416',
                          108,
                          rep_name,
                          376,
                          1.200e-07, 28.900, 0.518, 0.163,
                          9, 37
                          )

        hits_by_replicon = {rep_name: [ch_msha, ch_mshe, ch_mshg, ch_mshl, ch_mshm, ch_mshb, ch_mshc, ch_mshd]}
        systems, rej_cand = search_in_unordered_replicon(hits_by_replicon, models_to_detect, logger)

        self.assertEqual(len(systems), 1)
        self.assertEqual(systems[0].id, 'VICH001.B.00001.C001_MSH_1')
        self.assertListEqual(systems[0].hits, [ch_msha, ch_mshm, ch_mshe, ch_mshb, ch_mshc, ch_mshd, ch_mshg, ch_mshl])
        self.assertEqual(rej_cand, [])


    def test_search_in_ordered_replicon_rej_cand(self):
        logger = logging.getLogger('macsylib')
        macsylib.logger_set_level(level='ERROR')
        defaults = MacsyDefaults()

        seq_db = self.find_data('base', 'VICH001.B.00001.C001.prt')
        models_dir = self.find_data('data_set', 'models')
        args = argparse.Namespace()
        args.models_dir = models_dir
        args.sequence_db = seq_db
        args.db_type = 'unordered'
        args.models = ['set_1', 'MSH']
        args.worker = 4
        args.out_dir = self.tmp_dir
        args.index_dir = self.tmp_dir

        config = Config(defaults, args)

        model_registry = self._fill_model_registry(config)
        models_def_to_detect, models_fam_name, models_version = get_def_to_detect(config.models(), model_registry)

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

        models_to_detect = [model_bank[model_loc.fqn] for model_loc in models_def_to_detect]

        rep_name = 'VICH001.B.00001.C001'
        mod_msh = models_to_detect[0]

        ch_mshe =  CoreHit(mod_msh.get_gene('MSH_mshE').core_gene ,
                          'VICH001.B.00001.C001_00412',
                          400,
                          rep_name,
                          372,
                          4.800e-228,753.900,0.998,0.727,
                          142, 559)
        ch_mshg = CoreHit(mod_msh.get_gene('MSH_mshG').core_gene,
                          'VICH001.B.00001.C001_02307',
                          404,
                          rep_name,
                          2204,
                          7.500e-76, 252.600, 0.994, 0.819,
                          71, 404
                          )
        ch_mshb = CoreHit(mod_msh.get_gene('MSH_mshB').core_gene,
                          'VICH001.B.00001.C001_00415',
                          100,
                          rep_name,
                          375,
                          1.600e-35, 118.500,1.000, 0.388,
                          18,93
                          )

        hits_by_replicon = {rep_name: [ch_mshe, ch_mshg, ch_mshb]}
        systems, rej_cand = search_in_unordered_replicon(hits_by_replicon, models_to_detect, logger)

        self.assertEqual(len(rej_cand), 1)
        self.assertEqual(rej_cand[0].id, 'VICH001.B.00001.C001_MSH_1')
        self.assertListEqual(rej_cand[0].hits, [ch_mshe, ch_mshb, ch_mshg])
        self.assertEqual(systems, [])
