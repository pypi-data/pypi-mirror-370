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


import tempfile
import argparse

from macsylib.model import ModelBank
from macsylib.model import Model
from macsylib.config import Config, MacsyDefaults
from tests import MacsyTest


class TestModelBank(MacsyTest):


    def setUp(self):
        self._tmp_dir = tempfile.TemporaryDirectory(prefix='test_msl_ModelBank_')
        args = argparse.Namespace()
        args.sequence_db = self.find_data("base", "test_1.fasta")
        args.db_type = 'gembase'
        args.models_dir = self.find_data('models')
        args.res_search_dir =  self._tmp_dir.name
        args.log_level = 30
        self.cfg = Config(MacsyDefaults(), args)
        self.system_bank = ModelBank()


    def tearDown(self):
        ModelBank._model_bank = {}
        self._tmp_dir.cleanup()


    def test_add_get_model(self):
        model_name = 'foo'
        self.assertRaises(KeyError,  self.system_bank.__getitem__, model_name)
        model_foo = Model(model_name, 10)
        self.system_bank.add_model(model_foo)
        self.assertTrue(isinstance(model_foo, Model))
        self.assertEqual(model_foo,  self.system_bank[model_name])
        with self.assertRaises(KeyError) as ctx:
            self.system_bank.add_model(model_foo)
        self.assertEqual(str(ctx.exception),
                         '"a model named {0} is already registered in the models\' bank"'.format(model_name))

    def test_contains(self):
        system_in = Model("foo", 10)
        self.system_bank.add_model(system_in)
        self.assertIn(system_in,  self.system_bank)
        system_out = Model("bar", 10)
        self.assertNotIn(system_out,  self.system_bank)

    def test_iter(self):
        systems = [Model('foo', 10), Model('bar', 10)]
        for s in systems:
            self.system_bank.add_model(s)
        i = 0
        for s in self.system_bank:
            self.assertIn(s, systems)
            i += 1
        self.assertEqual(i, len(systems))

    def test_get_uniq_object(self):
        model_foo = Model("foo", 10)
        self.system_bank.add_model(model_foo)
        system_1 = self.system_bank[model_foo.name]
        system_2 = self.system_bank[model_foo.name]
        self.assertEqual(system_1, system_2)
