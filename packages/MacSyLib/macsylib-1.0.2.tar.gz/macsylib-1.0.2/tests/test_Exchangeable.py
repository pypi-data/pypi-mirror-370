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
import tempfile
import argparse

from macsylib.gene import Exchangeable
from macsylib.gene import CoreGene, ModelGene
from macsylib.model import Model
from macsylib.profile import ProfileFactory
from macsylib.config import Config, MacsyDefaults
from macsylib.registries import ModelLocation
from macsylib.error import MacsylibError
from tests import MacsyTest


class TestExchangeable(MacsyTest):

    def setUp(self):
        args = argparse.Namespace()
        args.sequence_db = self.find_data("base", "test_1.fasta")
        args.db_type = 'gembase'
        args.models_dir = self.find_data('models')
        self.tmp_dir = tempfile.TemporaryDirectory(prefix='test_msl_Exchangeable_')
        args.res_search_dir = os.path.join(self.tmp_dir.name, 'res_search_dir')
        args.log_level = 30
        self.cfg = Config(MacsyDefaults(), args)

        self.model_name = 'foo'
        self.model_location = ModelLocation(path=os.path.join(args.models_dir, self.model_name))
        self.profile_factory = ProfileFactory(self.cfg)


    def tearDown(self):
        self.tmp_dir.cleanup()


    def test_alternate_of(self):
        model = Model("T2SS", 10)

        gene_name = 'sctJ_FLG'
        c_gene_ref = CoreGene(self.model_location, gene_name, self.profile_factory)
        gene_ref = ModelGene(c_gene_ref, model)

        gene_name = 'sctJ'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        homolog_1 = Exchangeable(c_gene, gene_ref)
        gene_ref.add_exchangeable(homolog_1)

        self.assertEqual(homolog_1.alternate_of(), gene_ref)

    def test_is_exchangeable(self):
        model = Model("T2SS", 10)
        gene_name = 'sctJ_FLG'
        c_gene_ref = CoreGene(self.model_location, gene_name, self.profile_factory)
        gene_ref = ModelGene(c_gene_ref, model)

        gene_name = 'sctJ'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        homolog_1 = Exchangeable(c_gene, gene_ref)

        self.assertTrue(homolog_1.is_exchangeable)

    def test_add_exchangeable(self):
        model = Model("T2SS", 10)
        gene_name = 'sctJ_FLG'
        c_gene_ref = CoreGene(self.model_location, gene_name, self.profile_factory)
        gene_ref = ModelGene(c_gene_ref, model)

        gene_name = 'sctJ'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        homolog_1 = Exchangeable(c_gene, gene_ref)
        homolog_2 = Exchangeable(c_gene, gene_ref)

        with self.assertRaises(MacsylibError) as ctx:
            homolog_1.add_exchangeable(homolog_2)
        self.assertEqual(str(ctx.exception),
                         "Cannot add 'Exchangeable' to an Exchangeable")

    def test_model(self):
        model = Model("T2SS", 10)
        gene_name = 'sctJ_FLG'
        c_gene_ref = CoreGene(self.model_location, gene_name, self.profile_factory)
        gene_ref = ModelGene(c_gene_ref, model)

        gene_name = 'sctJ'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        homolog_1 = Exchangeable(c_gene, gene_ref)

        self.assertEqual(homolog_1.model, gene_ref.model)


    def test_loner(self):
        model = Model("T2SS", 10)
        gene_name = 'sctJ_FLG'
        c_gene_ref = CoreGene(self.model_location, gene_name, self.profile_factory)
        gene_ref = ModelGene(c_gene_ref, model)
        gene_ref_loner = ModelGene(c_gene_ref, model, loner=True)

        gene_name = 'sctJ'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        homolog_1 = Exchangeable(c_gene, gene_ref)
        homolog_2 = Exchangeable(c_gene, gene_ref_loner)

        self.assertFalse(homolog_1.loner)
        self.assertTrue(homolog_2.loner)


    def test_multi_system(self):
        model = Model("T2SS", 10)
        gene_name = 'sctJ_FLG'
        c_gene_ref = CoreGene(self.model_location, gene_name, self.profile_factory)
        gene_ref = ModelGene(c_gene_ref, model)
        gene_ref_multi_system = ModelGene(c_gene_ref, model, multi_system=True)

        gene_name = 'sctJ'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        homolog_1 = Exchangeable(c_gene, gene_ref)
        homolog_2 = Exchangeable(c_gene, gene_ref_multi_system)

        self.assertFalse(homolog_1.multi_system)
        self.assertTrue(homolog_2.multi_system)
