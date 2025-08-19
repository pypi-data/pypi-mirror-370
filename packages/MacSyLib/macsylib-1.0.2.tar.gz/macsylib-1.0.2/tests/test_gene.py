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

from macsylib.gene import CoreGene, ModelGene, Exchangeable, GeneStatus
from macsylib.model import Model
from macsylib.config import Config, MacsyDefaults
from macsylib.registries import ModelLocation
from macsylib.profile import ProfileFactory
from macsylib.error import MacsylibError
from tests import MacsyTest


class TestCoreGene(MacsyTest):

    def setUp(self):
        args = argparse.Namespace()
        args.sequence_db = self.find_data("base", "test_1.fasta")
        args.db_type = 'gembase'
        args.models_dir = self.find_data('models')
        self._tmp_dir = tempfile.TemporaryDirectory(prefix='test_msl_CoreGene_')
        args.res_search_dir = self._tmp_dir.name
        args.log_level = 30
        self.cfg = Config(MacsyDefaults(), args)
        self.model_name = 'foo'
        self.model_location = ModelLocation(path=os.path.join(args.models_dir, self.model_name))
        self.profile_factory = ProfileFactory(self.cfg)


    def tearDown(self):
        self._tmp_dir.cleanup()


    def test_core_gene(self):
        model_fqn = "foo/bar"
        model = Model(model_fqn, 10)
        gene_name = 'toto'
        cg = CoreGene(self.model_location, gene_name, self.profile_factory)
        self.assertEqual(cg.name, gene_name)
        self.assertEqual(cg.model_family_name, model.family_name)
        self.assertEqual(cg.profile, self.profile_factory.get_profile(cg, self.model_location))
        cg2 = CoreGene(self.model_location, gene_name, self.profile_factory)
        self.assertTrue(isinstance(hash(cg), int))
        self.assertEqual(hash(cg), hash(cg2))
        gene_name = 'totote'
        cg3 = CoreGene(self.model_location, gene_name, self.profile_factory)
        self.assertNotEqual(hash(cg), hash(cg3))


class TestModelGene(MacsyTest):

    def setUp(self):
        args = argparse.Namespace()
        args.sequence_db = self.find_data("base", "test_1.fasta")
        args.db_type = 'gembase'
        args.models_dir = self.find_data('models')
        self._tmp_dir = tempfile.TemporaryDirectory(prefix='test_msl_CoreGene_')
        args.res_search_dir = self._tmp_dir.name
        args.log_level = 30
        self.cfg = Config(MacsyDefaults(), args)
        self.model_name = 'foo'
        self.model_location = ModelLocation(path=os.path.join(args.models_dir, self.model_name))
        self.profile_factory = ProfileFactory(self.cfg)


    def tearDown(self):
        self._tmp_dir.cleanup()


    def test_init(self):
        model_foo = Model("foo", 10)
        gene_name = 'sctJ_FLG'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        gene_1 = ModelGene(c_gene, model_foo)
        with self.assertRaises(MacsylibError) as ctx:
            ModelGene(gene_1, model_foo)
        self.assertEqual(str(ctx.exception),
                         "The ModeleGene gene argument must be a CoreGene not <class 'macsylib.gene.ModelGene'>.")

    def test_hash(self):
        model_foo = Model("foo", 10)
        gene_name = 'sctJ_FLG'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        gene_1 = ModelGene(c_gene, model_foo)
        gene_2 = ModelGene(c_gene, model_foo)

        self.assertTrue(isinstance(hash(gene_1), int))
        self.assertEqual(hash(gene_1), hash(gene_1))
        self.assertNotEqual(hash(gene_1), hash(gene_2))

    def test_unknown_attribute(self):
        model_foo = Model("foo", 10)
        gene_name = 'sctJ_FLG'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        gene = ModelGene(c_gene, model_foo)
        with self.assertRaises(AttributeError) as ctx:
            gene.foo
        self.assertEqual(str(ctx.exception), "'ModelGene' object has no attribute 'foo'")


    def test_add_exchangeable(self):
        model_foo = Model("foo", 10)
        gene_name = 'sctJ'
        c_gene_ref = CoreGene(self.model_location, gene_name, self.profile_factory)
        gene_ref = ModelGene(c_gene_ref,  model_foo)

        h_gene_name = 'sctJ_FLG'
        h_c_gene = CoreGene(self.model_location, h_gene_name, self.profile_factory)

        homolog = Exchangeable(h_c_gene, gene_ref)
        gene_ref.add_exchangeable(homolog)
        self.assertEqual(len(gene_ref.exchangeables), 1)
        self.assertEqual(gene_ref.exchangeables[0], homolog)


    def test_exchangeables(self):
        model_foo = Model("foo", 10)

        gene_name = 'sctN'
        c_sctn = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctn = ModelGene(c_sctn, model_foo)

        gene_name = 'sctJ_FLG'
        c_sctJ_FLG = CoreGene(self.model_location, gene_name, self.profile_factory)

        gene_name = 'sctJ'
        c_sctJ = CoreGene(self.model_location, gene_name, self.profile_factory)

        homolog_1 = Exchangeable(c_sctJ, sctn)
        sctn.add_exchangeable(homolog_1)
        homolog_2 = Exchangeable(c_sctJ_FLG, sctn)
        sctn.add_exchangeable(homolog_2)
        self.assertEqual(sctn.exchangeables, [homolog_1, homolog_2])

        gene_name = 'flgB'
        c_flgb = CoreGene(self.model_location, gene_name, self.profile_factory)
        flgb = ModelGene(c_flgb, model_foo)
        gene_name = 'flgC'
        c_flgc = CoreGene(self.model_location, gene_name, self.profile_factory)
        exch_1 = Exchangeable(c_flgc, flgb)
        flgb.add_exchangeable(exch_1)
        model_foo.add_mandatory_gene(flgb)
        self.assertEqual(flgb.status, GeneStatus.MANDATORY)
        self.assertEqual(exch_1.status, GeneStatus.MANDATORY)
        # test the cache
        self.assertEqual(exch_1.status, GeneStatus.MANDATORY)


    def test_is_exchangeable(self):
        model_foo = Model("foo", 10)

        gene_name = 'sctN'
        c_sctn = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctn = ModelGene(c_sctn, model_foo)

        gene_name = 'sctJ_FLG'
        c_sctj_flg = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctj_flg = ModelGene(c_sctj_flg, model_foo)

        gene_name = 'sctJ'
        c_sctj = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctj = ModelGene(c_sctj, model_foo)
        homolog = Exchangeable(c_sctj_flg, sctj)
        sctj.add_exchangeable(homolog)

        self.assertFalse(sctj_flg.is_exchangeable)
        self.assertFalse(sctj.is_exchangeable)
        self.assertTrue(homolog.is_exchangeable)
        self.assertFalse(sctn.is_exchangeable)


    def test_alternate_of(self):
        model_foo = Model("foo", 10)

        gene_name = 'sctJ'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctj = ModelGene(c_gene, model_foo)

        gene_name = 'sctJ_FLG'
        c_sctj_flg = CoreGene(self.model_location, gene_name, self.profile_factory)
        analog = Exchangeable(c_sctj_flg, sctj)
        sctj.add_exchangeable(analog)
        self.assertEqual(sctj.alternate_of(), sctj)


    def test_model(self):
        """
        test getter/setter for model property
        """
        model_foo = Model("foo", 10)
        gene_name = 'sctJ_FLG'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctJ_FLG = ModelGene(c_gene, model_foo)
        self.assertEqual(sctJ_FLG.model, model_foo)


    def test_core_gene(self):
        """
        test getter/setter for core_gene property
        """
        model_foo = Model("foo", 10)
        gene_name = 'sctJ_FLG'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctJ_FLG = ModelGene(c_gene, model_foo)
        self.assertEqual(sctJ_FLG.core_gene, c_gene)


    def test_loner(self):
        """
        test getter for loner property
        """
        model_foo = Model("foo", 10)
        gene_name = 'sctJ_FLG'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctJ_FLG = ModelGene(c_gene, model_foo)
        self.assertFalse(sctJ_FLG.loner)

        gene_name = 'sctJ'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctJ = ModelGene(c_gene, model_foo, loner=True)
        self.assertTrue(sctJ.loner)


    def test_is_mandatory(self):
        """
        test if gene belong to model mandatory genes
        """
        model_foo = Model("foo", 10)

        gene_name = 'sctJ_FLG'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctJ_FLG = ModelGene(c_gene, model_foo)
        model_foo.add_mandatory_gene(sctJ_FLG)
        self.assertTrue(sctJ_FLG.is_mandatory())

        gene_name = 'sctJ'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctJ = ModelGene(c_gene, model_foo)
        model_foo.add_accessory_gene(sctJ)
        self.assertFalse(sctJ.is_mandatory())


    def test_is_accessory(self):
        """
        test if gene belong to model mandatory genes
        """
        model_foo = Model("foo", 10)

        gene_name = 'sctJ_FLG'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctJ_FLG = ModelGene(c_gene, model_foo)
        model_foo.add_mandatory_gene(sctJ_FLG)
        self.assertFalse(sctJ_FLG.is_accessory())

        gene_name = 'sctJ'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctJ = ModelGene(c_gene, model_foo)
        model_foo.add_accessory_gene(sctJ)
        self.assertTrue(sctJ.is_accessory())


    def test_is_Forbidden(self):
        """
        test if gene belong to model mandatory genes
        """
        model_foo = Model("foo", 10)
        gene_name = 'sctJ_FLG'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctJ_FLG = ModelGene(c_gene, model_foo)
        model_foo.add_mandatory_gene(sctJ_FLG)
        self.assertFalse(sctJ_FLG.is_forbidden())

        gene_name = 'sctJ'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctJ = ModelGene(c_gene, model_foo)
        model_foo.add_forbidden_gene(sctJ)
        self.assertTrue(sctJ.is_forbidden())


    def test_multi_system(self):
        """
        test getter for multi_system property
        """
        model_foo = Model("foo", 10)

        gene_name = 'sctJ_FLG'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctJ_FLG = ModelGene(c_gene, model_foo)
        self.assertFalse(sctJ_FLG.multi_system)

        gene_name = 'sctJ'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctJ = ModelGene(c_gene, model_foo, multi_system=True)
        self.assertTrue(sctJ.multi_system)


    def test_multi_model(self):
        """
        test getter for multi_modelproperty
        """
        model_foo = Model("foo", 10)

        gene_name = 'sctJ_FLG'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctJ_FLG = ModelGene(c_gene, model_foo)
        self.assertFalse(sctJ_FLG.multi_model)

        gene_name = 'sctJ'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctJ = ModelGene(c_gene, model_foo, multi_model=True)
        self.assertTrue(sctJ.multi_model)


    def test_status(self):
        """
        test getter for multi_modelproperty
        """
        model_foo = Model("foo", 10)

        gene_name = 'sctJ_FLG'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctJ_FLG = ModelGene(c_gene, model_foo)
        self.assertFalse(sctJ_FLG.multi_model)

        gene_name = 'sctJ'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctJ = ModelGene(c_gene, model_foo)
        self.assertIsNone(sctJ.status)

        sctJ.set_status(GeneStatus.MANDATORY)
        self.assertEqual(sctJ.status, GeneStatus.MANDATORY)


    def test_inter_gene_max_space(self):
        """
        test getter for inter_gene_max_space property
        """
        system_inter_gene_max_space = 40
        gene_inter_gene_max_space = 50
        model_foo = Model("foo", system_inter_gene_max_space)

        gene_name = 'sctJ_FLG'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctJ_FLG = ModelGene(c_gene, model_foo)
        self.assertIsNone(sctJ_FLG.inter_gene_max_space, None)

        gene_name = 'sctJ'
        c_gene = CoreGene(self.model_location, gene_name, self.profile_factory)
        sctJ = ModelGene(c_gene, model_foo, inter_gene_max_space=gene_inter_gene_max_space)
        self.assertEqual(sctJ.inter_gene_max_space, gene_inter_gene_max_space)


    def test_str(self):
        """
        """
        model_foo = Model("foo", 10)

        c_sctJ_FLG = CoreGene(self.model_location, 'sctJ_FLG', self.profile_factory)
        c_sctJ = CoreGene(self.model_location, 'sctJ', self.profile_factory)
        c_sctN = CoreGene(self.model_location, 'sctN', self.profile_factory)
        c_tadZ = CoreGene(self.model_location, 'tadZ', self.profile_factory)

        sctJ_FLG = ModelGene(c_sctJ_FLG, model_foo)
        homolog = Exchangeable(c_sctJ, sctJ_FLG)
        sctJ_FLG.add_exchangeable(homolog)
        analog = Exchangeable(c_sctN, sctJ_FLG)
        sctJ_FLG.add_exchangeable(analog)

        s = """name : sctJ_FLG
inter_gene_max_space: None
    exchangeables: sctJ, sctN"""
        self.assertEqual(str(sctJ_FLG), s)

        sctJ_FLG = ModelGene(c_sctJ_FLG, model_foo, loner=True, multi_system=True, inter_gene_max_space=10)
        s = """name : sctJ_FLG
inter_gene_max_space: 10
loner
multi_system"""
        self.assertEqual(str(sctJ_FLG), s)

        tadZ = ModelGene(c_tadZ, model_foo, loner=True, multi_system=False, multi_model=True, inter_gene_max_space=10)
        s = """name : tadZ
inter_gene_max_space: 10
loner
multi_model"""
        self.assertEqual(str(tadZ), s)


class TestGeneStatus(MacsyTest):

    def test_str(self):
        self.assertEqual(str(GeneStatus.MANDATORY), 'mandatory')
