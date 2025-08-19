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


def _preambule(PN: str, authors: str, cr_date: str, cr_holders: str, short_desc: str) -> str:
    """

    :param PN: The package name
    :param authors: the authors of the package
    :param cr_date: the date of the copyright (year)
    :param cr_holders: the holders of the copyright
    :param short_desc: One line description of the package
    :return: The preamble of the license declaration
    """
    short_desc = f"\n{PN} {short_desc}" if short_desc else ''

    if cr_holders:
        copyright = f"""
Copyright: {cr_date} {cr_holders}
See COPYRIGHT file for details."""
    else:
        copyright = ''

    preambule = f"""Authors: {authors}{copyright}

{PN} is a package of models for MacSyLib
(https://github.com/gem-pasteur/macsylib){short_desc}"""

    return preambule


def license(license_name: str, PN: str, authors: str, cr_date: str, cr_holders: str, short_desc: str) -> str:
    """
    Create a text to put in the headers of all package file

    :param license_name: The name of the license (accepted values are acronym for creative commons)
    :param PN: The program Name
    :param authors: the authors of the package
    :param cr_date: The date (year) of the copyright
    :param cr_holders: the holders of the copyright
    :param short_desc: One line description of the package
    :return: The text of the license to put on header of each package file
    :raise KeyError: when license_name is not managed (not a CC license)
    """
    preambule = _preambule(PN, authors, cr_date, cr_holders, short_desc)

    license = {
        'cc-by': f"""{preambule}

This work is licensed under the Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
""",
        'cc-by-sa': f"""{preambule}

This work is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
""",
        'cc-by-nc': f"""{preambule}

This work is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nc/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
""",
        'cc-by-nc-sa': f"""{preambule}

This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
""",
        'cc-by-nc-nd': f"""{preambule}

This work is licensed under the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-nd/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""
    }

    return license[license_name]


def name_2_url(license_name: str):
    """

    :param license_name:
    :type license_name:
    :return:
    :rtype:
    """
    acronym = license_name.strip('cc-')
    return f"http://creativecommons.org/licenses/{acronym}/4.0/"
