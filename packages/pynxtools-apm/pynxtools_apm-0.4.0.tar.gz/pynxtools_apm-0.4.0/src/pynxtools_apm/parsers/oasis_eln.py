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
"""Wrapping multiple parsers for vendor files with NOMAD Oasis/ELN/YAML metadata."""

import pathlib

import flatdict as fd
import yaml
from ase.data import chemical_symbols

from pynxtools_apm.concepts.mapping_functors_pint import add_specific_metadata_pint
from pynxtools_apm.configurations.oasis_eln_cfg import (
    APM_ENTRY_TO_NEXUS,
    APM_INSTRUMENT_DYNAMIC_TO_NEXUS,
    APM_INSTRUMENT_SPECIMEN_TO_NEXUS,
    APM_INSTRUMENT_STATIC_TO_NEXUS,
    APM_MEASUREMENT_TO_NEXUS,
    APM_RANGE_TO_NEXUS,
    APM_RECON_TO_NEXUS,
    APM_SAMPLE_TO_NEXUS,
    APM_SPECIMEN_TO_NEXUS,
    APM_USER_TO_NEXUS,
    APM_WORKFLOW_TO_NEXUS,
)
from pynxtools_apm.utils.custom_logging import logger
from pynxtools_apm.utils.parse_composition_table import parse_composition_table


class NxApmNomadOasisElnSchemaParser:
    """Parse eln_data.yaml dump file content generated from a NOMAD Oasis YAML.

    This parser implements a design where an instance of a specific NOMAD
    custom schema ELN template is used to fill pieces of information which
    are typically not contained in files from technology partners
    (e.g. pos, epos, apt, rng, rrng, ...). Until now, this custom schema and
    the NXapm application definition do not use a fully harmonized vocabulary.
    Therefore, the here hardcoded implementation is needed which maps specifically
    named pieces of information from the custom schema instance on named fields
    in an instance of NXapm

    The functionalities in this ELN YAML parser do not check if the
    instantiated template yields an instance which is compliant with NXapm.
    Instead, this task is handled by the generic part of the dataconverter
    during the verification of the template dictionary.
    """

    def __init__(self, file_path: str = "", entry_id: int = 1, verbose: bool = False):
        logger.info(f"Extracting data from ELN file: {file_path}")
        if pathlib.Path(file_path).name.endswith(("eln_data.yaml", "eln_data.yml")):
            self.file_path = file_path
        self.entry_id = entry_id if entry_id > 0 else 1
        self.verbose = verbose
        try:
            with open(self.file_path, "r", encoding="utf-8") as stream:
                self.yml = fd.FlatDict(yaml.safe_load(stream), delimiter="/")
                if self.verbose:
                    for key, val in self.yml.items():
                        logger.info(f"key: {key}, value: {val}")
        except (FileNotFoundError, IOError):
            logger.warning(f"File {self.file_path} not found !")
            self.yml = fd.FlatDict({}, delimiter="/")
            return

    def parse_sample_composition(self, template: dict) -> dict:
        """Interpret human-readable ELN input to generate consistent composition table."""
        src = "sample/composition"
        if src in self.yml:
            if isinstance(self.yml[src], list):
                dct = parse_composition_table(self.yml[src])

                prfx = f"/ENTRY[entry{self.entry_id}]/sample/chemical_composition"
                unit = "at.-%"  # the assumed default unit
                if "normalization" in dct:
                    if dct["normalization"] in [
                        "%",
                        "at%",
                        "at-%",
                        "at.-%",
                        "ppm",
                        "ppb",
                    ]:
                        unit = "at.-%"
                        template[f"{prfx}/normalization"] = "atom_percent"
                    elif dct["normalization"] in ["wt%", "wt-%", "wt.-%"]:
                        unit = "wt.-%"
                        template[f"{prfx}/normalization"] = "weight_percent"
                    else:
                        return template
                for symbol in chemical_symbols[1::]:
                    # ase convention is that chemical_symbols[0] == "X"
                    # to enable using ordinal number for indexing
                    if symbol in dct:
                        if isinstance(dct[symbol], tuple) and len(dct[symbol]) == 2:
                            trg = f"{prfx}/ELEMENT[{symbol}]"
                            template[f"{trg}/chemical_symbol"] = symbol
                            template[f"{trg}/composition"] = dct[symbol][0]
                            # template[f"{trg}/composition/@units"] = unit
                            if dct[symbol][1] is not None:
                                template[f"{trg}/composition_errors"] = dct[symbol][1]
                                # template[f"{trg}/composition_errors/@units"] = unit
        return template

    def parse_atom_types(self, template: dict) -> dict:
        """Copy atom_types, try to polish problematic user input."""
        src = "specimen/atom_types"
        if src in self.yml:
            unique_elements = set()
            for token in self.yml[src].split(","):
                symbol = token.strip()
                if symbol in chemical_symbols[1::]:
                    unique_elements.add(symbol)
                # silently ignoring all incorrect user input
            if len(unique_elements) > 0:
                template[f"/ENTRY[entry{self.entry_id}]/specimen/atom_types"] = (
                    ", ".join(list(unique_elements))
                )
        return template

    def parse_user(self, template: dict) -> dict:
        """Copy data from user section into template."""
        src = "user"
        if src in self.yml:
            if isinstance(self.yml[src], list):
                if all(isinstance(entry, dict) for entry in self.yml[src]):
                    user_id = 1
                    # custom schema delivers a list of dictionaries...
                    for user_dict in self.yml[src]:
                        if user_dict == {}:
                            continue
                        identifier = [self.entry_id, user_id]
                        add_specific_metadata_pint(
                            APM_USER_TO_NEXUS,
                            user_dict,
                            identifier,
                            template,
                        )
                        if "orcid" in user_dict:
                            trg = f"/ENTRY[entry{self.entry_id}]/userID[user{user_id}]"
                            template[f"{trg}/identifierNAME[identifier]"] = user_dict[
                                "orcid"
                            ]
                            template[f"{trg}/identifierNAME[identifier]/@type"] = "DOI"
                        user_id += 1
        return template

    def parse_pulser_source(self, template: dict) -> dict:
        """Copy data into the (laser)/source section of the pulser."""
        # additional laser-specific details only relevant when the laser was used
        if "instrument/pulser/pulse_mode" in self.yml:
            if self.yml["instrument/pulser/pulse_mode"] == "voltage":
                return template

        src = "instrument/laser_source"
        if src in self.yml:
            if isinstance(self.yml[src], list):
                if all(isinstance(entry, dict) for entry in self.yml[src]):
                    laser_id = 1
                    # custom schema delivers a list of dictionaries...
                    for ldct in self.yml[src]:
                        trg_sta = (
                            f"/ENTRY[entry{self.entry_id}]/measurement/eventID[event1]/instrument/"
                            f"pulser/sourceID[source{laser_id}]"
                        )
                        trg_dyn = (
                            f"/ENTRY[entry{self.entry_id}]/measurement/eventID[event1]/instrument/"
                            f"pulser/sourceID[source{laser_id}]"
                        )
                        if "name" in ldct:
                            template[f"{trg_sta}/name"] = ldct["name"]
                        # qnt = "wavelength"
                        # if qnt in ldct:
                        #     if "value" in ldct[qnt] and "unit" in ldct[qnt]:
                        #         template[f"{trg_sta}/{qnt}"] = ldct[qnt]["value"]
                        #        template[f"{trg_sta}/{qnt}/@units"] = ldct[qnt]["unit"]
                        for qnt in ["power", "pulse_energy", "wavelength"]:
                            if isinstance(ldct[qnt], dict):
                                if ("value" in ldct[qnt]) and ("unit" in ldct[qnt]):
                                    template[f"{trg_dyn}/{qnt}"] = ldct[qnt]["value"]
                                    template[f"{trg_dyn}/{qnt}/@units"] = ldct[qnt][
                                        "unit"
                                    ]
                        laser_id += 1
                    return template
        logger.warning("pulse_mode != voltage but no laser details specified!")
        return template

    def parse(self, template: dict) -> dict:
        """Copy data from self into template the appdef instance."""
        self.parse_sample_composition(template)
        self.parse_atom_types(template)
        self.parse_user(template)
        self.parse_pulser_source(template)
        identifier = [self.entry_id, 1]
        for cfg in [
            APM_ENTRY_TO_NEXUS,
            APM_SAMPLE_TO_NEXUS,
            APM_SPECIMEN_TO_NEXUS,
            APM_MEASUREMENT_TO_NEXUS,
            APM_INSTRUMENT_STATIC_TO_NEXUS,
            APM_INSTRUMENT_DYNAMIC_TO_NEXUS,
            APM_INSTRUMENT_SPECIMEN_TO_NEXUS,
            APM_RANGE_TO_NEXUS,
            APM_RECON_TO_NEXUS,
            APM_WORKFLOW_TO_NEXUS,
        ]:
            add_specific_metadata_pint(cfg, self.yml, identifier, template)
        return template
