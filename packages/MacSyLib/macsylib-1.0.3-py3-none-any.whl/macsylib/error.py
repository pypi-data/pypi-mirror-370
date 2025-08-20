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
Manage MacSyLib specific errors
"""


class MacsylibError(Exception):
    """
    The base class for MacSyLib specific exceptions.
    """


class MacsydataError(MacsylibError):
    """
    Raised when error is encounter during model package handling
    """


class MacsyDataLimitError(MacsydataError):
    """
    Raised when the maximum number of GitHub api call is reached
    """


class OptionError(MacsylibError):
    """
    Raised when command line option is not set properly
    """


class ModelInconsistencyError(MacsylibError):
    """
    Raised when a definition model is not consistent.
    """


class SystemDetectionError(MacsylibError):
    """
    Raised when the detection of systems from Hits encountered a problem.
    """


class Timeout(MacsylibError):
    """
    Raised when best solution reach the timeout
    """


class EmptyFileError(MacsylibError):
    """
    Raised when fasta file does not contains sequences
    """
