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
module that deals with the satellite_finder outputs
"""

import sys
import typing
from collections.abc import Callable
import pandas as pd

import macsylib
from macsylib.system import HitSystemTracker, System, RejectedCandidate, LikelySystem, UnlikelySystem
from macsylib.solution import Solution
from macsylib.serialization import (TsvSystemSerializer,
                                    TsvSolutionSerializer,
                                    TsvRejectedCandidatesSerializer,
                                    TsvSpecialHitSerializer,
                                    TsvLikelySystemSerializer,
                                    TxtLikelySystemSerializer, TxtUnikelySystemSerializer, TxtSystemSerializer)



def outfile_header(models_fam_name: str,
                   models_version: str,
                   skipped_replicons: list[str] | None = None,
                   prog_name:str = 'macsylib') -> str:
    """
    :return: The first lines of each result file
    """
    header = f"""# {prog_name} {macsylib.__version__} {macsylib.__commit__}
# models : {models_fam_name}-{models_version}
# {' '.join(sys.argv)}"""
    if skipped_replicons:
        header += "\n#"
        for rep_name in skipped_replicons:
            header += f"\n# WARNING: The replicon '{rep_name}' has been SKIPPED. Cannot be solved before timeout."
        header += "\n#"
    return header


def systems_to_tsv(models_fam_name: str, models_version: str, systems: list[System],
                   hit_system_tracker: HitSystemTracker,
                   sys_file: typing.IO,
                   skipped_replicons: list[str] | None = None,
                   header: Callable[[str, str, list[str], str],str]=outfile_header,
                   system_name:str = 'System') -> None:
    """
    print systems occurrences in a file in tabulated  format

    :param models_fam_name: the name name of the models (Conj, CrisprCAS, ...)
    :param models_version: the version of the models
    :param systems: list of systems found
    :param hit_system_tracker: a filled HitSystemTracker.
    :param sys_file: The file where to write down the systems occurrences
    :param skipped_replicons: the replicons name for which msf reach the timeout
    :param header: A function that generate the string which will be place on the head of the results
    :return: None
    """
    print(header(models_fam_name, models_version, skipped_replicons=skipped_replicons),
          file=sys_file)
    if skipped_replicons:
        systems = [s for s in systems if s.replicon_name not in skipped_replicons]
    if systems:
        print(f"# {system_name.capitalize()}s found:", file=sys_file)
        print(TsvSystemSerializer.header, file=sys_file)
        for system in systems:
            sys_serializer = TsvSystemSerializer()
            print(sys_serializer.serialize(system, hit_system_tracker), file=sys_file)
        warnings = loner_warning(systems)
        if warnings:
            print("\n".join(warnings), file=sys_file)
    else:
        print(f"# No {system_name.capitalize()} found", file=sys_file)


def systems_to_txt(models_fam_name: str, models_version: str,
                   systems: list[System],
                   hit_system_tracker: HitSystemTracker,
                   sys_file: typing.IO,
                   skipped_replicons: list[str] | None = None,
                   header: Callable[[str, str, list[str], str], str] = outfile_header,
                   ) -> None:
    """
    print systems occurrences in a file in human-readable format

    :param models_fam_name: the family name of the models (Conj, CrisprCAS, ...)
    :param models_version: the version of the models
    :param systems: list of systems found
    :param hit_system_tracker: a filled HitSystemTracker.
    :param sys_file: The file where to write down the systems occurrences
    :param skipped_replicons: the replicons name for which msf reach the timeout
    :param header: A function that generate the string which will be place on the head of the results
    :return: None
    """

    print(header(models_fam_name, models_version, skipped_replicons=skipped_replicons), file=sys_file)
    if skipped_replicons:
        systems = [s for s in systems if s.replicon_name not in skipped_replicons]
    if systems:
        print("# Systems found:\n", file=sys_file)
        for system in systems:
            sys_serializer = TxtSystemSerializer()
            print(sys_serializer.serialize(system, hit_system_tracker), file=sys_file)
            print("=" * 60, file=sys_file)

        warnings = loner_warning(systems)
        if warnings:
            print("\n".join(warnings), file=sys_file)
    else:
        print("# No System found", file=sys_file)


def solutions_to_tsv(models_fam_name: str,
                     models_version: str,
                     solutions: list[Solution],
                     hit_system_tracker: HitSystemTracker,
                     sys_file: typing.IO, skipped_replicons: list[str] | None = None,
                     header: Callable[[str, str, list[str], str],str]=outfile_header,
                     system_name: str = 'system') -> None:
    """
    print solution in a file in tabulated format
    A solution is a set of systems which represents an optimal combination of
    systems to maximize the score.

    :param models_fam_name: the name name of the models (Conj, CrisprCAS, ...)
    :param models_version: the version of the models
    :param solutions: list of systems found
    :param hit_system_tracker: a filled HitSystemTracker.
    :param sys_file: The file where to write down the systems occurrences
    :param header: A function that generate the string which will be place on the head of the results
    :param skipped_replicons: the replicons name for which msf reach the timeout
    :return: None
    """
    print(header(models_fam_name, models_version, skipped_replicons=skipped_replicons),
          file=sys_file)
    if solutions:
        sol_serializer = TsvSolutionSerializer()
        print(f"# {system_name.capitalize()}s found:", file=sys_file)
        print(sol_serializer.header, file=sys_file)

        for sol_id, solution in enumerate(solutions, 1):
            print(sol_serializer.serialize(solution, sol_id, hit_system_tracker), file=sys_file, end='')
            if warnings := loner_warning(solution.systems):
                print("\n".join(warnings) + "\n", file=sys_file)
    else:
        print(f"# No {system_name.capitalize()}s found", file=sys_file)


def summary_best_solution(models_fam_name: str,
                          models_version: str,
                          best_solution_path: str,
                          sys_file: typing.IO,
                          models_fqn: list[str],
                          replicon_names: list[str],
                          header: Callable[[str, str, list[str], str],str]=outfile_header,
                          skipped_replicons: list[str] | None = None) -> None:
    """
    do a summary of best_solution in best_solution_path and write it on out_path
    a summary compute the number of system occurrence for each model and each replicon

    .. code-block:: text

        replicon        model_fqn_1  model_fqn_2  ....
        rep_name_1           1           2
        rep_name_2           2           0

    columns are separated by \t character

    :param models_fam_name: the name name of the models (Conj, CrisprCAS, ...)
    :param models_version: the version of the models
    :param str best_solution_path: the path to the best_solution file in tsv format
    :param sys_file: the file where to save the summary
    :param models_fqn: the fully qualified names of the models
    :param replicon_names: the names of the replicons used
    :param header: A function that generate the string which will be place on the head of the results
    :param skipped_replicons: the replicons name for which msf reach the timeout
    """
    skipped_replicons = skipped_replicons if skipped_replicons else set()
    print(header(models_fam_name, models_version, skipped_replicons=skipped_replicons),
          file=sys_file)

    def fill_replicon(summary: pd.DataFrame) -> pd.DataFrame:
        """
        add row with 0 for all models for lacking replicons

        :param summary: the
        :return:
        """
        index_name = summary.index.name
        computed_replicons = set(summary.index)
        lacking_replicons = set(replicon_names) - computed_replicons - set(skipped_replicons)
        lacking_replicons = sorted(lacking_replicons)
        if lacking_replicons:
            rows = pd.DataFrame({models: [0 * len(lacking_replicons)] for models in summary.columns},
                                index=lacking_replicons)
            summary = pd.concat([summary, rows], ignore_index=False)
        summary.index.name = index_name
        return summary


    def fill_models(summary: pd.DataFrame) -> pd.DataFrame:
        """
        add columns for lacking models (it means no occurrence found)

        :param summary: the dataframe which summary the results
        :return: a summary with lacking models set to 0 occurrence
        """
        computed_models = set(summary.columns)
        lacking_models = set(models_fqn) - computed_models
        lacking_models = sorted(lacking_models)
        for model in lacking_models:
            summary[model] = [0 for _ in summary.index]
        return summary

    try:
        best_solution = pd.read_csv(best_solution_path, sep='\t', comment='#')
    except pd.errors.EmptyDataError:
        # No results Found
        # may be there is no results so I have to report
        # may be the solution cannot be found So I do not to report (Warning)
        # may be the both one replicon without results one replicon not solved
        # So I have to report only the replicon without results
        replicon_to_report = list(set(replicon_names) - set(skipped_replicons))
        summary = pd.DataFrame(0, index=replicon_to_report, columns=models_fqn)
        summary.index.name = 'replicon'
    else:
        selection = best_solution[['replicon', 'sys_id', 'model_fqn']]
        dropped = selection.drop_duplicates(subset=['replicon', 'sys_id'])
        summary = pd.crosstab(index=dropped.replicon, columns=dropped['model_fqn'])
        summary = fill_replicon(summary)
        summary = fill_models(summary)

    summary.to_csv(sys_file, sep='\t')


def rejected_candidates_to_txt(models_fam_name: str, models_version: str,
                               rejected_candidates: list[RejectedCandidate],
                               cand_file: typing.IO,
                               header: Callable[[str, str, list[str], str],str]=outfile_header,
                               skipped_replicons: list[str] | None = None):
    """
    print rejected clusters in a file

    :param models_fam_name: the family name of the models (Conj, CrisprCAS, ...)
    :param models_version: the version of the models
    :param rejected_candidates: list of candidates which does not contitute a system
    :param cand_file: The file where to write down the rejected candidates
    :param header: A function that generate the string which will be place on the head of the results
    :param skipped_replicons: the replicons name for which msf reach the timeout
    :return: None
    """
    print(header(models_fam_name, models_version, skipped_replicons=skipped_replicons), file=cand_file)
    if skipped_replicons:
        rejected_candidates = [rc for rc in rejected_candidates if rc.replicon_name not in skipped_replicons]
    if rejected_candidates:
        print("# Rejected candidates:\n", file=cand_file)
        for rej_cand in rejected_candidates:
            print(rej_cand, file=cand_file, end='')
            print("=" * 60, file=cand_file)
    else:
        print("# No Rejected candidates", file=cand_file)


def rejected_candidates_to_tsv(models_fam_name: str, models_version: str,
                               rejected_candidates: list[RejectedCandidate],
                               cand_file: typing.IO,
                               header: Callable[[str, str, list[str], str],str]=outfile_header,
                               skipped_replicons: list[str] | None = None):
    """
    print rejected clusters in a file

    :param models_fam_name: the name name of the models (Conj, CrisprCAS, ...)
    :param models_version: the version of the models
    :param rejected_candidates: list of candidates which does not contitute a system
    :param cand_file: The file where to write down the rejected candidates
    :param header: A function that generate the string which will be place on the head of the results
    :param skipped_replicons: the replicons name for which msf reach the timeout
    :return: None
    """
    print(header(models_fam_name, models_version, skipped_replicons=skipped_replicons),
          file=cand_file)
    if skipped_replicons:
        rejected_candidates = [rc for rc in rejected_candidates if rc.replicon_name not in skipped_replicons]
    if rejected_candidates:
        serializer = TsvRejectedCandidatesSerializer()
        rej_candidates = serializer.serialize(rejected_candidates)
        print("# Rejected candidates found:", file=cand_file)
        print(rej_candidates, file=cand_file, end='')
    else:
        print("# No Rejected candidates", file=cand_file)


def loners_to_tsv(models_fam_name: str, models_version: str, systems:list[System], sys_file:typing.IO,
                  header: Callable[[str, str, list[str], str],str]=outfile_header,
                  skipped_replicons: list[str] | None = None) -> None:
    """
    get loners from valid systems and save them on file

    :param models_fam_name: the family name of the models (Conj, CrisprCAS, ...)
    :param models_version: the version of the models
    :param systems: the systems from which the loners are extract
    :param sys_file: the file where loners are saved
    :param header: A function that generate the string which will be place on the head of the results
    :param skipped_replicons: the replicons name for which msf reach the timeout
    """
    print(header(models_fam_name, models_version, skipped_replicons=skipped_replicons),
          file=sys_file)
    if systems:
        best_loners = set()
        for syst in systems:
            best_loners.update(syst.get_loners())
        if best_loners:
            serializer = TsvSpecialHitSerializer()
            loners = serializer.serialize(best_loners)
            print("# Loners found:", file=sys_file)
            print(loners, file=sys_file)
        else:
            print("# No Loners found", file=sys_file)
    else:
        print("# No Loners found", file=sys_file)


def multisystems_to_tsv(models_fam_name:str, models_version:str, systems:list[System], sys_file:typing.IO,
                        header:Callable[[str, str, list[str], str],str]=outfile_header,
                        skipped_replicons: list[str] | None = None) -> None:
    """
    get multisystems from valid systems and save them on file

    :param models_fam_name: the family name of the models (Conj, CrisprCAS, ...)
    :param models_version: the version of the models
    :param systems: the systems from which the loners are extract
    :param sys_file: the file where multisystems are saved
    :param header: A function that generate the string which will be place on the head of the results
    :param skipped_replicons: the replicons name for which msf reach the timeout
    """
    print(header(models_fam_name, models_version, skipped_replicons=skipped_replicons),
          file=sys_file)
    if systems:
        best_multisystems = set()
        for syst in systems:
            best_multisystems.update(syst.get_multisystems())
        if best_multisystems:
            serializer = TsvSpecialHitSerializer()
            multisystems = serializer.serialize(best_multisystems)
            print("# Multisystems found:", file=sys_file)
            print(multisystems, file=sys_file)
        else:
            print("# No Multisystems found", file=sys_file)
    else:
        print("# No Multisystems found", file=sys_file)


def likely_systems_to_txt(models_fam_name: str, models_version: str,
                          likely_systems: list[LikelySystem],
                          hit_system_tracker: HitSystemTracker,
                          sys_file: typing.IO,
                          header: Callable[[str, str, list[str], str],str]=outfile_header,
                          skipped_replicons: list[str] | None = None) -> None:
    """
    print likely systems occurrences (from unordered replicon)
    in a file in text human readable format

    :param models_fam_name: the family name of the models (Conj, CrisprCAS, ...)
    :param models_version: the version of the models
    :param likely_systems: list of systems found
    :param hit_system_tracker: a filled HitSystemTracker.
    :param sys_file: file object
    :param header: A function that generate the string which will be place on the head of the results
    :param skipped_replicons: the replicons name for which msf reach the timeout
    :return: None
    """
    print(header(models_fam_name, models_version, skipped_replicons=skipped_replicons), file=sys_file)
    if likely_systems:
        print("# Systems found:\n", file=sys_file)
        for system in likely_systems:
            sys_serializer = TxtLikelySystemSerializer()
            print(sys_serializer.serialize(system, hit_system_tracker), file=sys_file)
    else:
        print("# No Likely Systems found", file=sys_file)


def likely_systems_to_tsv(models_fam_name: str, models_version: str,
                          likely_systems: list[LikelySystem],
                          hit_system_tracker: HitSystemTracker,
                          sys_file: typing.IO,
                          header: Callable[[str, str, list[str], str],str]=outfile_header,
                          skipped_replicons: list[str] | None = None) -> None:
    """
    print likely systems occurrences (from unordered replicon)
    in a file in tabulated separeted value (tsv) format

    :param models_fam_name: the family name of the models (Conj, CrisprCAS, ...)
    :param models_version: the version of the models
    :param likely_systems: list of systems found
    :param hit_system_tracker: a filled HitSystemTracker.
    :param sys_file: The file where to write down the systems occurrences
    :param header: A function that generate the string which will be place on the head of the results
    :param skipped_replicons: the replicons name for which msf reach the timeout
    :return: None
    """
    print(header(models_fam_name, models_version, skipped_replicons=skipped_replicons), file=sys_file)
    if likely_systems:
        print("# Likely Systems found:\n", file=sys_file)
        for l_system in likely_systems:
            sys_serializer = TsvLikelySystemSerializer()
            print(sys_serializer.serialize(l_system, hit_system_tracker), file=sys_file)
    else:
        print("# No Likely Systems found", file=sys_file)


def unlikely_systems_to_txt(models_fam_name: str, models_version: str,
                            unlikely_systems: list[UnlikelySystem],
                            sys_file: typing.IO,
                            header: Callable[[str, str, list[str], str],str]=outfile_header,
                            skipped_replicons: list[str]|None = None) -> None:
    """
    print hits (from unordered replicon) which probably does not make a system occurrences
    in a file in human readable format

    :param models_fam_name: the family name of the models (Conj, CrisprCAS, ...)
    :param models_version: the version of the models
    :param unlikely_systems: list of :class:`macsypy.system.UnLikelySystem` objects
    :param sys_file: The file where to write down the systems occurrences
    :param header: A function that generate the string which will be place on the head of the results
    :param skipped_replicons: the replicons name for which msf reach the timeout
    :return: None
    """
    print(header(models_fam_name, models_version, skipped_replicons=skipped_replicons), file=sys_file)
    if unlikely_systems:
        print("# Unlikely Systems found:\n", file=sys_file)
        for system in unlikely_systems:
            sys_serializer = TxtUnikelySystemSerializer()
            print(sys_serializer.serialize(system), file=sys_file)
            print("=" * 60, file=sys_file)
    else:
        print("# No Unlikely Systems found", file=sys_file)


def loner_warning(systems: list[System]) -> list[str]:
    """
    :param systems: sequence of systems
    :return: warning for loner which have less occurrences than systems occurrences in which this lone is used
             except if the loner is also multi system
    """
    warnings = []
    loner_tracker = {}
    for syst in systems:
        loners = syst.get_loners()
        for loner in loners:
            if loner.multi_system:
                # the loner multi_systems are allowed to appear in several systems
                continue
            elif loner in loner_tracker:
                loner_tracker[loner].append(syst)
            else:
                loner_tracker[loner] = [syst]
    for loner, systs in loner_tracker.items():
        if len(loner) < len(systs):
            # len(loners) count the number of loner occurrence the loner and its counterpart
            warnings.append(f"# WARNING Loner: there is only {len(loner)} occurrence(s) of loner '{loner.gene.name}' "
                            f"and {len(systs)} potential systems [{', '.join([s.id for s in systs])}]")

    return warnings
