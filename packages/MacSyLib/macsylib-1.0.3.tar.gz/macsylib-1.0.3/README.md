![MacSyLib banner](./.github/logo_macsylib.png "MacSyLib")


# MacSyLib

MacSyLib is a python package library that allow to model and detect macromolecular systems, genetic pathways…
by similarity search in prokaryotes datasets.

[![Build Status](https://github.com/gem-pasteur/macsylib/actions/workflows/testing.yml/badge.svg?branch=main)](https://github.com/gem-pasteur/macsylib/actions/workflows/testing.yml)

[![Doc](https://readthedocs.org/projects/macsylib/badge/?version=latest)](http://macsylib.readthedocs.org/en/latest/#)

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/macsylib)](https://pypi.org/project/macsylib/)

[![Open Source License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://opensource.org/licenses/GPL-3.0)

[![PyPI](https://img.shields.io/pypi/v/macsylib)](https://pypi.org/project/macsylib/)
[![Conda](https://img.shields.io/conda/vn/bioconda/macsylib?style=plastic)](https://github.com/bioconda/bioconda-recipes/tree/master/recipes/macsylib)

[![SWH](https://archive.softwareheritage.org/badge/origin/https://github.com/gem-pasteur/macsylib/)](https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/gem-pasteur/macsylib)
[![SWH](https://archive.softwareheritage.org/badge/swh:1:dir:cbb7c2e40ba02825297590edf6734ee64800d3e1/)](https://archive.softwareheritage.org/swh:1:dir:cbb7c2e40ba02825297590edf6734ee64800d3e1;origin=https://github.com/gem-pasteur/macsylib;visit=swh:1:snp:c1e51a6ffb6ac45cae6aecde26217fa05003f225;anchor=swh:1:rev:5da144b39117f614543edfc5b06aba099d97f586)

[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/10994/badge)](https://www.bestpractices.dev/projects/10994)
[![FAIR checklist badge](https://fairsoftwarechecklist.net/badge.svg)](https://fairsoftwarechecklist.net/v0.2?f=31&a=32113&i=32321&r=133)

## Citations

MacSyFinder v2:
Néron, Bertrand; Denise, Rémi; Coluzzi, Charles; Touchon, Marie; Rocha, Eduardo P.C.; Abby, Sophie S.
MacSyFinder v2: Improved modelling and search engine to identify molecular systems in genomes.
Peer Community Journal, Volume 3 (2023), article no. e28. doi : 10.24072/pcjournal.250.
https://peercommunityjournal.org/articles/10.24072/pcjournal.250/

## Licence:

MacSyLib is developed and released under [![Open Source License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://opensource.org/licenses/GPL-3.0)

## Installation

> [!IMPORTANT]
> MacSyLib requires hmmer >= 3.1 (http://hmmer.org/).
> You need to install hmmer by yourself (except if you install macsylib via *conda/mamba*).
> If you are a modeler, you will need also `git`
> The other dependencies are managed by the python package manager *pip*.

### Installation from distribution

We encourage to install macsylib in a [virtualenv](https://virtualenv.pypa.io/en/latest/)

After creating a virtualenv dedicated to MacSyLib and activating it

    python3 -m venv my_project
    cd my_project
    source bin/activate

you can install macsylib as described below:

We distinguish 3 kind of MacSyLib users:

- The **end user**, who want to analyse it's data with the library
- The **modeler**, who want to modelize new macromolecular systems
- The **developer** who want to add or fix methods in the macsylib code

By default the installation is for the end user, if you are modeler or developer there is a specific pip target.

For instance for the *modelers*
```bash
python -m pip install .[model]
```

For the *developpers*
```bash
python -m pip install -e .[dev]
```

For someone who is both *developper* and *modeler*

```bash
python -m pip install -e [dev,model]
```

For the developers:  
Once you have installed macsylib do not forget to install pre-commit hooks

```bash
pre-commit install
```

## Models installation

Models are no longer shipped along macsyfinder nor macsylib packages.
To install Models you can use `msl_data` (shipped with MacSyLib).
*msl_data* (formely *macsydata*) allow to manage models stored in [macsy-models](https://github.com/macsy-models).
Below some most useful commands.

  * available: List Models available on macsy-models.
  * search: Discover new packages.
  * install: Install or upgarde packages.
  * uninstall: Uninstall packages.
  * cite: How to cite a package.
  * ...

For complete documentation see
[macsydata section on readthedoc](https://macsylib.readthedocs.io/en/latest/user_guide/installation.html#models-installation-with-macsydata)

For models not stored in macsy-models the commands *available*, *search*, *installation from remote* or *upgrade from remote*
are **NOT** available.

For models **Not** stored in *macsy-models*, you have to manage them semi-manually.
Download the archive (do not unarchive it), then use *msl_data* for the installation.

## Use MacSyLib

    import macsylib


## Contributing

We encourage contributions, bug report, enhancement ...

But before to do that, we encourage to read [the contributing guide](CONTRIBUTING.md).

## Contributors

[List of all people who participated in the macsylib project](CONTRIBUTORS.md).
