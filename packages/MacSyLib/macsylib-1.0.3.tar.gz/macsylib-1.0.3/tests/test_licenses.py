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


from macsylib.licenses import  license

from tests import MacsyTest


class TestLicense(MacsyTest):


    def test_license(self):
        prog_name = 'prog_name'
        cc_by = license('cc-by',
                        prog_name,
                        'bibi',
                        '2025',
                        'Pasteur',
                        'this is a short desc'
                        )
        expected_license = """Authors: bibi
Copyright: 2025 Pasteur
See COPYRIGHT file for details.

prog_name is a package of models for MacSyLib
(https://github.com/gem-pasteur/macsylib)
prog_name this is a short desc

This work is licensed under the Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""
        self.assertEqual(expected_license, cc_by)


    def test_license_no_copyright(self):
        prog_name = 'prog_name'
        cc_by = license('cc-by-sa',
                        prog_name,
                        'bibi',
                        '2025',
                        '',
                        'this is a short desc'
                        )
        expected_license = """Authors: bibi

prog_name is a package of models for MacSyLib
(https://github.com/gem-pasteur/macsylib)
prog_name this is a short desc

This work is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""
        self.assertEqual(expected_license, cc_by)
