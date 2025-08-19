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
import logging

import colorlog
import os
import argparse
import unittest
import platform
import shutil
import tempfile

from macsylib.registries import ModelRegistry, scan_models_dir
from macsylib.utils import get_def_to_detect, get_replicon_names, threads_available, parse_time, list_models
from macsylib.error import MacsylibError

from tests import MacsyTest


class TestUtils(MacsyTest):

    def test_list_models(self):
        cmd_args = argparse.Namespace()
        cmd_args.models_dir = self.find_data('fake_model_dir')
        cmd_args.list_models = True
        rcv_list_models = list_models(cmd_args)
        exp_list_models = """set_1
      /def_1_1
      /def_1_2
      /def_1_3
      /def_1_4
set_2
      /level_1
              /def_1_1
              /def_1_2
              /level_2
                      /def_2_3
                      /def_2_4
"""
        self.assertEqual(exp_list_models, rcv_list_models)


    @unittest.skipIf(platform.system() == 'Windows' or os.getuid() == 0, 'Skip test on Windows or if run as root')
    def test_list_models_no_permission(self):
        # on gitlab it is not allowed to change the permission of a directory
        # located in tests/data
        # So I need to copy it in /tmp
        tmp_dir= tempfile.TemporaryDirectory(prefix='test_msl_Config_')
        model_dir_name = 'fake_model_dir'
        src_model_dir = self.find_data(model_dir_name)
        dst_model_dir = os.path.join(tmp_dir.name, 'fake_model_dir')
        shutil.copytree(src_model_dir, dst_model_dir)

        log = colorlog.getLogger('macsylib')
        log.setLevel(logging.WARNING)
        cmd_args = argparse.Namespace()
        cmd_args.models_dir = dst_model_dir
        cmd_args.list_models = True
        models_dir_perm = os.stat(cmd_args.models_dir).st_mode

        try:
            os.chmod(cmd_args.models_dir, 0o110)
            with self.catch_log(log_name='macsylib') as log:
                rcv_list_models = list_models(cmd_args)
                log_msg = log.get_value().strip()
            self.assertEqual(rcv_list_models, '')
            self.assertEqual(log_msg, f"{cmd_args.models_dir} is not readable: [Errno 13] Permission denied: '{cmd_args.models_dir}' : skip it.")
        finally:
            os.chmod(cmd_args.models_dir, models_dir_perm)
            tmp_dir.cleanup()

    def test_get_def_to_detect(self):
        cmd_args = argparse.Namespace()
        cmd_args.models_dir = self.find_data('fake_model_dir')
        cmd_args.models = ('set_1', 'def_1_1', 'def_1_2', 'def_1_3')
        registry = ModelRegistry()
        models_location = scan_models_dir(cmd_args.models_dir)
        for ml in models_location:
            registry.add(ml)

        # case where models are specified on command line
        res, model_family, model_vers = get_def_to_detect(('set_1', ['def_1_1', 'def_1_2', 'def_1_3']), registry)
        model_loc = registry['set_1']
        self.assertEqual(model_family, 'set_1')
        self.assertEqual(model_vers, '0.0b2')
        exp = [model_loc.get_definition(name) for name in ('set_1/def_1_1', 'set_1/def_1_2', 'set_1/def_1_3')]
        self.assertListEqual(res, exp)

        # case we search all models
        res, model_family, model_vers = get_def_to_detect(('set_1', ['all']), registry)
        self.assertEqual(model_family, 'set_1')
        self.assertEqual(model_vers, '0.0b2')
        exp = model_loc.get_all_definitions()
        self.assertListEqual(res, exp)

        # case the models required does not exists
        with self.assertRaises(ValueError):
            get_def_to_detect(('set_1', ['FOO', 'BAR']), registry)


    def test_get_replicon_names_gembase(self):
        replicon_names = get_replicon_names(self.find_data('base', 'gembase.fasta'), 'gembase')
        self.assertListEqual(replicon_names,
                             ['GCF_000005845', 'GCF_000006725', 'GCF_000006745', 'GCF_000006765', 'GCF_000006845',
                              'GCF_000006905', 'GCF_000006925', 'GCF_000006945'])

    def test_get_replicon_names_ordered(self):
        replicon_names = get_replicon_names(self.find_data('base', 'MOBP1_once.prt'), 'ordered_replicon')
        self.assertListEqual(replicon_names,
                             ['MOBP1_once'])

    def test_get_replicon_names_unordered(self):
        replicon_names = get_replicon_names(self.find_data('base', 'MOBP1_once.prt'), 'unordered')
        self.assertListEqual(replicon_names,
                             ['MOBP1_once'])

    def test_get_replicon_names_bad_type(self):
        with self.assertRaises(MacsylibError) as ctx:
            get_replicon_names(self.find_data('base', 'MOBP1_once.prt'), 'bad_dbtype')
        self.assertEqual(str(ctx.exception),
                         'Invalid genome type: bad_dbtype')

    def test_threads_available(self):
        if hasattr(os, "sched_getaffinity"):
            sched_getaffinity_ori = os.sched_getaffinity
        else:
            sched_getaffinity_ori = None
        cpu_count_ori = os.cpu_count

        threads_nb = 7
        cpu_nb = 8

        os.cpu_count = lambda : cpu_nb

        try:
            del os.sched_getaffinity
            self.assertEqual(threads_available(), cpu_nb)
            os.sched_getaffinity = lambda x: [None] * threads_nb
            self.assertEqual(threads_available(), threads_nb)
        finally:
            os.cpu_count = cpu_count_ori
            if sched_getaffinity_ori:
                os.sched_getaffinity = sched_getaffinity_ori
            else:
                del os.sched_getaffinity

    def test_parse_time(self):
        self.assertEqual(parse_time(10), 10)
        self.assertEqual(parse_time('10s'), 10)
        self.assertEqual(parse_time('10m'), 600)
        self.assertEqual(parse_time('1h'), 3600)
        self.assertEqual(parse_time('1d'), 86400)
        self.assertEqual(parse_time(10.5), 10)
        self.assertEqual(parse_time('10m10s1h'), 600 + 10 + 3600)
        self.assertEqual(parse_time('10m 10s 1h'), 600 + 10 + 3600)
        with self.assertRaises(ValueError) as ctx:
            parse_time('10W')
        self.assertEqual(str(ctx.exception),
                         'Not valid time format. Units allowed h/m/s.')
