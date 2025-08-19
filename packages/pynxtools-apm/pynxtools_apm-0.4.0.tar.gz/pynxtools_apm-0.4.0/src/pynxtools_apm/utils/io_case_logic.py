#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Utility class to analyze which vendor/community files are passed to apm reader."""

from typing import Dict, List, Tuple

from pynxtools_apm.concepts.mapping_functors_pint import var_path_to_spcfc_path
from pynxtools_apm.utils.get_checksum import (
    DEFAULT_CHECKSUM_ALGORITHM,
    get_sha256_of_file_content,
)

VALID_FILE_NAME_SUFFIX_RECON = [".apt", ".pos", ".epos", ".ato", ".csv", ".h5"]
VALID_FILE_NAME_SUFFIX_RANGE = [
    ".rng",
    ".rrng",
    ".env",
    ".fig.txt",
    "range_.h5",
    ".analysis",
]
VALID_FILE_NAME_SUFFIX_CONFIG = [".yaml", ".yml"]
VALID_FILE_NAME_SUFFIX_CAMECA = [".cameca", ".str", ".rraw", ".rhit", ".hits", ".root"]
from pynxtools_apm.utils.custom_logging import logger


class ApmUseCaseSelector:
    """Decision maker about what needs to be parsed given arbitrary input.

    Users might invoke this dataconverter with arbitrary input, no input, or
    too much input. The UseCaseSelector decide what to do in each case.
    """

    def __init__(self, file_paths: Tuple[str] = None):
        """Initialize the class.

        dataset injects numerical data and metadata from an analysis.
        eln injects additional metadata and eventually numerical data.
        """
        self.case: Dict[str, list] = {}
        self.eln: List[str] = []
        self.cfg: List[str] = []
        self.apsuite: List[str] = []
        self.reconstruction: List[str] = []
        self.ranging: List[str] = []
        self.is_valid = False
        self.supported_file_name_suffixes = (
            VALID_FILE_NAME_SUFFIX_RECON
            + VALID_FILE_NAME_SUFFIX_RANGE
            + VALID_FILE_NAME_SUFFIX_CONFIG
            + VALID_FILE_NAME_SUFFIX_CAMECA
        )
        logger.info(
            f"self.supported_file_name_suffixes: {self.supported_file_name_suffixes}"
        )
        logger.info(f"{file_paths}")
        self.sort_files_by_file_name_suffix(file_paths)
        self.check_validity_of_file_combinations()

    def sort_files_by_file_name_suffix(self, file_paths: Tuple[str] = None):
        """Sort all input-files based on their name suffix to prepare validity check."""
        for suffix in self.supported_file_name_suffixes:
            self.case[suffix] = []
        for fpath in file_paths:
            for suffix in self.supported_file_name_suffixes:
                if suffix not in [".h5", "range_.h5"]:
                    if (fpath.lower().endswith(suffix)) and (
                        fpath not in self.case[suffix]
                    ):
                        self.case[suffix].append(fpath)
                        break
                else:
                    if fpath.lower().endswith("range_.h5"):
                        self.case["range_.h5"].append(fpath)
                        break
                    if fpath.lower().endswith(".h5"):
                        self.case[".h5"].append(fpath)
                        break
                # HDF5 files need special treatment, this already shows that magic numbers
                # should better have been used or signatures to avoid having to have as
                # complicated content checks as we had to implement e.g. for the em reader

    def check_validity_of_file_combinations(self):
        """Check if this combination of types of files is supported."""
        recon_input = 0  # reconstruction relevant file e.g. POS, ePOS, APT, ATO, CSV
        range_input = 0  # ranging definition file, e.g. RNG, RRNG, ENV, FIG.TXT
        other_input = 0  # generic ELN, Oasis-specific configurations
        apsui_input = 0  # manual yaml files composed from IVAS/AP Suite
        for suffix, value in self.case.items():
            if suffix not in [".h5", "range_.h5"]:
                if suffix in VALID_FILE_NAME_SUFFIX_RECON:
                    recon_input += len(value)
                elif suffix in VALID_FILE_NAME_SUFFIX_RANGE:
                    range_input += len(value)
                elif suffix in VALID_FILE_NAME_SUFFIX_CONFIG:
                    other_input += len(value)
                elif suffix in VALID_FILE_NAME_SUFFIX_CAMECA:
                    apsui_input += len(value)
                else:
                    continue
            else:
                if suffix == "range_.h5":
                    range_input += len(value)
                if suffix == ".h5":
                    recon_input += len(value)
        # logger.debug(f"{recon_input}, {range_input}, {other_input}")

        # if 1 <= other_input <= 2:  # and (recon_input == 1) and (range_input == 1)
        self.is_valid = True
        self.reconstruction: List[str] = []
        self.ranging: List[str] = []
        for suffix in VALID_FILE_NAME_SUFFIX_RECON:
            self.reconstruction += self.case[suffix]
        for suffix in VALID_FILE_NAME_SUFFIX_RANGE:
            self.ranging += self.case[suffix]
        yml: List[str] = []
        for suffix in VALID_FILE_NAME_SUFFIX_CONFIG:
            yml += self.case[suffix]
        for entry in yml:
            if entry.endswith((".oasis.specific.yaml", ".oasis.specific.yml")):
                self.cfg += [entry]
            else:
                self.eln += [entry]
        for suffix in VALID_FILE_NAME_SUFFIX_CAMECA:
            self.apsuite += self.case[suffix]
        logger.info(
            f"Reconstruction: {self.reconstruction}\n"
            f"Ranging definitions: {self.ranging}\n"
            f"Oasis ELN: {self.eln}\n"
            f"Oasis local config: {self.cfg}\n"
        )
        if len(self.apsuite) > 0:
            logger.info(f"IVAS/APSuite: {self.apsuite}\n")

    def report_workflow(self, template: dict, entry_id: int) -> dict:
        """Initialize the reporting of the workflow."""
        identifier = [entry_id]
        # populate automatically input-files used
        # rely on assumption made in check_validity_of_file_combination
        for fpath in self.reconstruction:
            prfx = var_path_to_spcfc_path(
                "/ENTRY[entry*]/atom_probeID[atom_probe]/reconstruction/results",
                identifier,
            )
            with open(fpath, "rb") as fp:
                template[f"{prfx}/checksum"] = get_sha256_of_file_content(fp)
                template[f"{prfx}/file_name"] = f"{fpath}"
                template[f"{prfx}/type"] = "file"
                template[f"{prfx}/algorithm"] = DEFAULT_CHECKSUM_ALGORITHM
        for fpath in self.ranging:
            prfx = var_path_to_spcfc_path(
                "/ENTRY[entry*]/atom_probeID[atom_probe]/ranging/source",
                identifier,
            )
            with open(fpath, "rb") as fp:
                template[f"{prfx}/checksum"] = get_sha256_of_file_content(fp)
                template[f"{prfx}/file_name"] = f"{fpath}"
                template[f"{prfx}/type"] = "file"
                template[f"{prfx}/algorithm"] = DEFAULT_CHECKSUM_ALGORITHM
        # FAU/Erlangen's pyccapt control and calibration file have not functional
        # distinction which makes it non-trivial to decide if a given HDF5 qualifies
        # as control or calibration file TODO::for this reason it is currently ignored
        return template
