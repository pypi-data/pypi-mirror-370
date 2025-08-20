.. MacSyLib - python library that provide functions for
    detection of macromolecular systems in protein datasets
    using systems modelling and similarity search.
    Authors: Sophie Abby, Bertrand Néron
    Copyright © 2014-2025 Institut Pasteur (Paris) and CNRS.
    See the COPYRIGHT file for details
    MacSyLib is distributed under the terms of the GNU General Public License (GPLv3).
    See the COPYING file for details.

.. _dev_installation:


************
Installation
************

MacSyLib works with models for macromolecular systems that are not shipped with it,
you have to install them separately. See the :ref:`msl_data section <modeler_msl_data>` below.
(msl_data is packaged alongside macsylib)

.. dev_dependencies:

=====================
MacSyLib dependencies
=====================
**Python version >=3.10** is required to run MacSyLib: https://docs.python.org/3.10/index.html

MacSyLib has one program dependency:

 - the *Hmmer* program, version 3.1 or greater (http://hmmer.org/).

The *hmmsearch* program should be installed (*e.g.*, in the PATH) in order to use MacSyLib.
Otherwise, the paths to this executable must be specified in the command-line:
see the :ref:`command-line options <hmmer-options>`.


MacSyLib also relies on some Python library dependencies:

 - colorlog
 - colorama
 - pyyaml
 - packaging
 - networkx
 - pandas

For modeler (models creator)

 - GitPython

For developper

 - sphinx
 - sphinx_rtd_theme
 - sphinx-autodoc-typehints
 - sphinxcontrib-svg2pdfconverter
 - coverage
 - build
 - ruff
 - pre-commit

These dependencies will be automatically retrieved and installed when using `pip` for installation (see below).


.. dev_install:

============================================
MacSyLib Installation and testing procedures
============================================

Installation steps:
===================

Make sure every required dependency/software is present.
--------------------------------------------------------

By default MacSyLib will try to use `hmmsearch` in your PATH. If `hmmsearch` is not in the PATH,
you have to set the absolute path to `hmmsearch` in a :ref:`configuration file <config-definition-label>`
or in the :ref:`command-line <hmmer-options>` upon execution.
If the tools are not in the path, some test will be skipped and a warning will be raised.


installation in a virtualenv
""""""""""""""""""""""""""""

.. code-block:: bash

    # create a new virtaulenv
    python3 -m venv MacSyLib
    # activate it
    cd MacSyLib
    source bin/activate
    # clone/install the project in editable mode
    git clone
    cd MacSyLib
    python3 -m pip install -e .[dev]
    # install tools to ensure coding style
    pre-commit install

To exit the virtualenv just execute the `deactivate` command.

.. code-block:: bash

    source MacSyLib/bin/activate

Then use `MacSyLib` :ref:`python-example` or installed models with `msl_data` tool.


.. note::

    *MacSyLib* has adopted `ruff <https://docs.astral.sh/ruff/>`_ as linter and *pre-commit* to ensure the coding style.
    Please read `CONTRIBUTING.md <https://github.com/gem-pasteur/macsylib/blob/master/CONTRIBUTING.md>`_ guide lines.


.. dev_testing:

Testing
=======

MacSyLib project use `unittest` framework (included in the standard library) to test the code.

All tests stuff is in `tests` directory.

* The data directory contains data needed by the tests
* in the *__init__.py* file a *MacsyTest* class is defined and should be the base of all testcase use in the project
* each *test_*.py* represent a file containing unit tests.

To run all the tests (in the virtualenv)

.. code-block:: shell

    python -m unittest discover

To increase verbosity of output

.. code-block:: shell

    python -m unittest discover -vv

.. code-block:: text

    ...
    test_average_wholeness (tests.test_solution.SolutionTest.test_average_wholeness) ... ok
    test_gt (tests.test_solution.SolutionTest.test_gt) ... ok
    test_hits_number (tests.test_solution.SolutionTest.test_hits_number) ... ok
    test_hits_positions (tests.test_solution.SolutionTest.test_hits_positions) ... ok
    test_iteration (tests.test_solution.SolutionTest.test_iteration) ... ok
    test_lt (tests.test_solution.SolutionTest.test_lt) ... ok
    test_score (tests.test_solution.SolutionTest.test_score) ... ok
    test_sorting (tests.test_solution.SolutionTest.test_sorting) ... ok
    test_systems (tests.test_solution.SolutionTest.test_systems) ... ok
    test_get_def_to_detect (tests.test_utils.TestUtils.test_get_def_to_detect) ... ok
    test_get_replicon_names_bad_type (tests.test_utils.TestUtils.test_get_replicon_names_bad_type) ... ok
    test_get_replicon_names_gembase (tests.test_utils.TestUtils.test_get_replicon_names_gembase) ... ok
    test_get_replicon_names_ordered (tests.test_utils.TestUtils.test_get_replicon_names_ordered) ... ok
    test_get_replicon_names_unordered (tests.test_utils.TestUtils.test_get_replicon_names_unordered) ... ok
    test_parse_time (tests.test_utils.TestUtils.test_parse_time) ... ok
    test_threads_available (tests.test_utils.TestUtils.test_threads_available) ... ok

    ----------------------------------------------------------------------
    Ran 548 tests in 34.265s

    OK

The tests must be in python file (`.py`) starting with with `test\_` \
It's possible to specify one or several test files, one module, or one class in a module or a method in a Test class.

Test the `test_package` module

.. code-block:: shell

    python -m unittest -vv tests.test_package

.. code-block:: text

    test_init (tests.test_package.TestLocalModelIndex.test_init) ... ok
    test_repos_url (tests.test_package.TestLocalModelIndex.test_repos_url) ... ok
    test_check (tests.test_package.TestPackage.test_check) ... ok
    test_check_bad_metadata (tests.test_package.TestPackage.test_check_bad_metadata) ... ok
    test_check_dir_in_profile (tests.test_package.TestPackage.test_check_dir_in_profile) ... ok

    ...

    test_list_package_vers (tests.test_package.TestRemoteModelIndex.test_list_package_vers) ... ok
    test_list_packages (tests.test_package.TestRemoteModelIndex.test_list_packages) ... ok
    test_remote_exists (tests.test_package.TestRemoteModelIndex.test_remote_exists) ... ok
    test_repos_url (tests.test_package.TestRemoteModelIndex.test_repos_url) ... ok
    test_unarchive (tests.test_package.TestRemoteModelIndex.test_unarchive) ... ok
    test_url_json (tests.test_package.TestRemoteModelIndex.test_url_json) ... ok
    test_url_json_reach_limit (tests.test_package.TestRemoteModelIndex.test_url_json_reach_limit) ... ok

    ----------------------------------------------------------------------
    Ran 56 tests in 0.242s

    OK

Test only the class `TestPackage` (this module contains 3 classes)

.. code-block:: shell

    python -m unittest -vv tests.test_package.TestPackage

.. code-block:: text

    test_check (tests.test_package.TestPackage.test_check) ... ok
    test_check_bad_metadata (tests.test_package.TestPackage.test_check_bad_metadata) ... ok
    test_check_dir_in_profile (tests.test_package.TestPackage.test_check_dir_in_profile) ... ok
    test_check_empty_profile (tests.test_package.TestPackage.test_check_empty_profile) ... ok
    test_check_metadata (tests.test_package.TestPackage.test_check_metadata) ... ok
    test_check_metadata_no_cite (tests.test_package.TestPackage.test_check_metadata_no_cite) ... ok

    ...

    test_metadata (tests.test_package.TestPackage.test_metadata) ... ok
    test_profile_with_bad_ext (tests.test_package.TestPackage.test_profile_with_bad_ext) ... ok

    ----------------------------------------------------------------------
    Ran 42 tests in 0.151s

    OK

Test only the method `test_metadata` from the test Class `TestPackage` in module `test_package`

.. code-block:: shell

    python -m unittest -vv tests.test_package.TestPackage.test_metadata

.. code-block:: text

    test_metadata (tests.test_package.TestPackage.test_metadata) ... ok

    ----------------------------------------------------------------------
    Ran 1 test in 0.005s

    OK


Coverage
========

To compute the tests coverage, we use the `coverage <https://pypi.org/project/coverage/>`_ package.
The package is automatically installed if you have installed `MacSyLib` with the `dev` target see :ref:`installation <dev_installation>`
The coverage package is setup in the `pyproject.toml` configuration file

To compute the coverage

.. code-block:: shell

    coverage run

.. code-block:: text

    ...

    test_lt (tests.test_solution.SolutionTest.test_lt) ... ok
    test_score (tests.test_solution.SolutionTest.test_score) ... ok
    test_sorting (tests.test_solution.SolutionTest.test_sorting) ... ok
    test_systems (tests.test_solution.SolutionTest.test_systems) ... ok
    test_get_def_to_detect (tests.test_utils.TestUtils.test_get_def_to_detect) ... ok
    test_get_replicon_names_bad_type (tests.test_utils.TestUtils.test_get_replicon_names_bad_type) ... ok
    test_get_replicon_names_gembase (tests.test_utils.TestUtils.test_get_replicon_names_gembase) ... ok
    test_get_replicon_names_ordered (tests.test_utils.TestUtils.test_get_replicon_names_ordered) ... ok
    test_get_replicon_names_unordered (tests.test_utils.TestUtils.test_get_replicon_names_unordered) ... ok
    test_parse_time (tests.test_utils.TestUtils.test_parse_time) ... ok
    test_threads_available (tests.test_utils.TestUtils.test_threads_available) ... ok

    ----------------------------------------------------------------------
    Ran 548 tests in 34.485s

    OK

Then display a report

.. code-block:: shell

    coverage report


.. code-block:: text

    Name                                   Stmts   Miss Branch BrPart  Cover
    ------------------------------------------------------------------------
    src/macsylib/__init__.py                  56      2     12      1    96%
    src/macsylib/cluster.py                  278      7    114      2    97%
    src/macsylib/config.py                   391     12    140      7    96%
    src/macsylib/data/__init__.py              0      0      0      0   100%
    src/macsylib/database.py                 203      3     52      1    98%
    src/macsylib/definition_parser.py        219      3     70      2    98%
    src/macsylib/error.py                      8      0      0      0   100%
    src/macsylib/gene.py                     144      2     18      1    98%
    src/macsylib/hit.py                      198      1     54      2    99%
    src/macsylib/io.py                       173      1     76      1    99%
    src/macsylib/licenses.py                  14      0      2      0   100%
    src/macsylib/metadata.py                 126      0     36      2    99%
    src/macsylib/model.py                    127      0     34      0   100%
    src/macsylib/model_conf_parser.py         62      0     12      0   100%
    src/macsylib/package.py                  326      9    110      4    96%
    src/macsylib/profile.py                  115      7     28      1    94%
    src/macsylib/registries.py               189      5     62      6    96%
    src/macsylib/report.py                   121      0     28      2    99%
    src/macsylib/scripts/__init__.py           0      0      0      0   100%
    src/macsylib/scripts/macsydata.py        682     57    182     15    91%
    src/macsylib/scripts/macsyprofile.py     247      5     64      6    96%
    src/macsylib/search_genes.py              79      7     20      3    90%
    src/macsylib/search_systems.py           150      7     50      5    94%
    src/macsylib/serialization.py            137      3     48      2    97%
    src/macsylib/solution.py                  97      0     34      0   100%
    src/macsylib/system.py                   397      3     96      0    99%
    src/macsylib/utils.py                     84      0     24      1    99%
    ------------------------------------------------------------------------
    TOTAL                                   4623    134   1366     64    96%

or generate a html report

.. code-block:: shell

    coverage html

.. code-block:: text

    Wrote HTML report to htmlcov/index.html

The results are in the `htmlcov` directory. With you favourite web browser, open the `index.html` file.
for more options please refer to the `coverage documentation <https://coverage.readthedocs.io/en/latest/>`_ .
