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

import subprocess
from tests import MacsyTest


class Test_msl_data(MacsyTest):

    def test_help(self):

        expected_output = r"""usage: msl_data [-h] [-v] [--version]
                {available,download,install,uninstall,search,info,list,freeze,cite,help,check,show,definition,init}"""

        p = subprocess.run("msl_data --help", shell=True, check=True, capture_output=True, text=True, encoding='utf8')
        self.assertEqual(p.returncode, 0)
        # The output is not exactly formated in same manner according to the width of the terminal where the test is executed
        # on some execution some lines ar wrapped
        # on some other no
        # so I test only the beginning of the help message
        self.assertTrue(p.stdout.startswith(expected_output))


class Test_msl_profile(MacsyTest):

    def test_help(self):

        p = subprocess.run("msl_profile --help", shell=True, check=True, capture_output=True, text=True, encoding='utf8')
        self.assertEqual(p.returncode, 0)
