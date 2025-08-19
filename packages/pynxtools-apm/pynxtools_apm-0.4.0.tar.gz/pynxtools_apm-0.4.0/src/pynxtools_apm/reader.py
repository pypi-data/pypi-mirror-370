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
"""Generic parser for loading atom probe microscopy data into NXapm."""

import os
from time import perf_counter_ns
from typing import Any, Tuple

import numpy as np
from pynxtools.dataconverter.readers.base.reader import BaseReader

from pynxtools_apm.examples.usa_madison_cameca_eln import NxApmCustomElnCamecaRoot
from pynxtools_apm.parsers.ifes_ranging import IfesRangingDefinitionsParser
from pynxtools_apm.parsers.ifes_reconstruction import IfesReconstructionParser
from pynxtools_apm.parsers.oasis_config import NxApmNomadOasisConfigParser
from pynxtools_apm.parsers.oasis_eln import NxApmNomadOasisElnSchemaParser
from pynxtools_apm.utils.create_nx_default_plots import apm_default_plot_generator
from pynxtools_apm.utils.custom_logging import logger
from pynxtools_apm.utils.io_case_logic import ApmUseCaseSelector
from pynxtools_apm.utils.remove_uninstantiated import remove_uninstantiated_sensors


class APMReader(BaseReader):
    """Parse content from community file formats.

    Specifically, (local electrode) atom probe microscopy and field-ion microscopy
    into a NXapm.nxdl-compliant NeXus file.

    """

    # Whitelist for the NXDLs that the reader supports and can process
    supported_nxdls = ["NXapm"]

    def read(
        self,
        template: dict = None,
        file_paths: Tuple[str] = None,
        objects: Tuple[Any] = None,
    ) -> dict:
        """Read data from given file, return filled template dictionary apm."""
        logger.info(os.getcwd())
        tic = perf_counter_ns()
        template.clear()

        entry_id = 1

        # eln_data, and ideally recon and ranging definitions from technology partner file
        logger.debug(
            "Identify information sources (RDM config, ELN, tech-partner files) to deal with..."
        )
        case = ApmUseCaseSelector(file_paths)
        if not case.is_valid:
            logger.warning(
                "Such a combination of input-file(s, if any) is not supported !"
            )
            return {}
        case.report_workflow(template, entry_id)

        if len(case.cfg) == 1:
            logger.debug("Parse (meta)data coming from a custom NOMAD OASIS RDM...")
            nx_apm_cfg = NxApmNomadOasisConfigParser(case.cfg[0], entry_id, False)
            nx_apm_cfg.parse(template)

        if len(case.eln) == 1:
            logger.debug("Parse (meta)data coming from an ELN exemplified for NOMAD")
            nx_apm_eln = NxApmNomadOasisElnSchemaParser(case.eln[0], entry_id)
            nx_apm_eln.parse(template)

        if 1 <= len(case.apsuite) <= 2:
            logger.debug("Parse (meta)data coming from a customized ELN...")
            for cameca_input_file in case.apsuite:
                nx_apm_cameca = NxApmCustomElnCamecaRoot(cameca_input_file, entry_id)
                nx_apm_cameca.parse(template)

        if len(case.reconstruction) == 1:
            logger.debug("Parse (meta)data from a reconstructed dataset file...")
            nx_apm_recon = IfesReconstructionParser(case.reconstruction[0], entry_id)
            nx_apm_recon.parse(template)

        if len(case.ranging) == 1:
            logger.debug("Parse (meta)data from a ranging definitions file...")
            nx_apm_range = IfesRangingDefinitionsParser(case.ranging[0], entry_id)
            nx_apm_range.parse(template)

        logger.debug("Create NeXus default plottable data...")
        apm_default_plot_generator(template, entry_id)

        logger.debug("Naive removal of concepts that have missing values")
        # these are introduced via the "use" functor but might not be populated with instance data
        remove_uninstantiated_sensors(template, entry_id)

        debugging = False
        if debugging:
            logger.debug(
                "Reporting state of template before passing to HDF5 writing..."
            )
            for keyword, value in sorted(template.items()):
                logger.info(f"{keyword}____{type(value)}____{value}")

        logger.debug("Forward instantiated template to the NXS writer...")
        toc = perf_counter_ns()
        trg = f"/ENTRY[entry{entry_id}]/profiling/template_filling_elapsed_time"
        template[f"{trg}"] = np.float64((toc - tic) / 1.0e9)
        template[f"{trg}/@units"] = "s"
        return template


# This has to be set to allow the convert script to use this reader.
READER = APMReader
