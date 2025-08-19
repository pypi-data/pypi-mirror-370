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
"""Dict mapping custom schema instances from eln_data.yaml file on concepts in NXapm."""

from typing import Any, Dict

from pynxtools_apm.utils.pint_custom_unit_registry import ureg

APM_ENTRY_TO_NEXUS: Dict[str, Any] = {
    "prefix_trg": "/ENTRY[entry*]",
    "prefix_src": "entry/",
    "map_to_str": [
        "operation_mode",
        "start_time",
        "end_time",
        "experiment_description",
    ],
    "map_to_u4": ["run_number"],
}


APM_SAMPLE_TO_NEXUS: Dict[str, Any] = {
    "prefix_trg": "/ENTRY[entry*]/sample",
    "prefix_src": "sample/",
    "map_to_bool": ["is_simulation"],
    "map_to_str": ["alias", "description"],
    "map_to_f8": [
        (
            "grain_diameter",
            ureg.micrometer,
            "grain_diameter/value",
            "grain_diameter/unit",
        ),
        (
            "grain_diameter_errors",
            ureg.micrometer,
            "grain_diameter_error/value",
            "grain_diameter_error/unit",
        ),
        (
            "heat_treatment_temperature",
            ureg.kelvin,
            "heat_treatment_temperature/value",
            "heat_treatment_temperature/unit",
        ),
        (
            "heat_treatment_temperature_errors",
            ureg.kelvin,
            "heat_treatment_temperature_error/value",
            "heat_treatment_temperature_error/unit",
        ),
        (
            "heat_treatment_quenching_rate",
            ureg.kelvin / ureg.second,
            "heat_treatment_quenching_rate/value",
            "heat_treatment_quenching_rate/unit",
        ),
        (
            "heat_treatment_quenching_rate_errors",
            ureg.kelvin / ureg.second,
            "heat_treatment_quenching_rate_error/value",
            "heat_treatment_quenching_rate_error/unit",
        ),
    ],
}


APM_SPECIMEN_TO_NEXUS: Dict[str, Any] = {
    "prefix_trg": "/ENTRY[entry*]/specimen",
    "prefix_src": "specimen/",
    "map_to_str": ["alias", "preparation_date", "description"],
    "map_to_f8": [
        (
            "initial_radius",
            ureg.nanometer,
            "initial_radius/value",
            "initial_radius/unit",
        ),
        ("shank_angle", ureg.degree, "shank_angle/value", "shank_angle/unit"),
    ],
    "map_to_bool": [
        "is_polycrystalline",
        "is_amorphous",
        "is_simulation",
    ],
}


APM_INSTRUMENT_SPECIMEN_TO_NEXUS: Dict[str, Any] = {
    "prefix_trg": "/ENTRY[entry*]/specimen",
    "prefix_src": "instrument/",
    "map_to_f8": [
        (
            "initial_radius",
            ureg.nanometer,
            "initial_radius/value",
            "initial_radius/unit",
        ),
        ("shank_angle", ureg.degree, "shank_angle/value", "shank_angle/unit"),
    ],
}


APM_MEASUREMENT_TO_NEXUS: Dict[str, Any] = {
    "prefix_trg": "/ENTRY[entry*]/measurement",
    "prefix_src": "",
    "map_to_str": ["status"],
}


APM_INSTRUMENT_STATIC_TO_NEXUS: Dict[str, Any] = {
    "prefix_trg": "/ENTRY[entry*]/measurement/instrument",
    "prefix_src": "instrument/",
    "map_to_bool": [("reflectron/applied", "reflectron_applied")],
    "map_to_str": [
        "location",
        ("name", "instrument_name"),
        ("fabrication/vendor", "fabrication_vendor"),
        ("fabrication/model", "fabrication_model"),
        ("fabrication/serial_number", "fabrication_serial_number"),
        ("local_electrode/name", "local_electrode_name"),
    ],
}


APM_INSTRUMENT_DYNAMIC_TO_NEXUS: Dict[str, Any] = {
    "prefix_trg": "/ENTRY[entry*]/measurement/eventID[event*]/instrument",
    "prefix_src": "instrument/",
    "use": [
        ("control/target_detection_rate/@units", "ions/pulse"),
        ("analysis_chamber/pressure_sensor/measurement", "pressure"),
        ("stage/temperature_sensor/measurement", "temperature"),
    ],
    "map_to_str": [
        ("pulser/pulse_mode", "pulse_mode"),
        ("control/evaporation_control", "evaporation_control"),
    ],
    "map_to_f8": [
        ("control/target_detection_rate", "target_detection_rate"),
        (
            "pulser/pulse_frequency",
            ureg.kilohertz,
            "pulse_frequency/value",
            "pulse_frequency/unit",
        ),
        ("pulser/pulse_fraction", "pulse_fraction"),
        (
            "analysis_chamber/pressure_sensor/value",
            ureg.bar,
            "chamber_pressure/value",
            "chamber_pressure/unit",
        ),
        (
            "stage/temperature_sensor/value",
            ureg.kelvin,
            "base_temperature/value",
            "base_temperature/unit",
        ),
    ],
}


APM_RANGE_TO_NEXUS: Dict[str, Any] = {
    "prefix_trg": "/ENTRY[entry*]/atom_probeID[atom_probe]/ranging",
    "prefix_src": "ranging/",
    "map_to_str": [
        ("programID[program1]/program", "program_name"),
        ("programID[program1]/program/@version", "program_version"),
    ],
}


APM_RECON_TO_NEXUS: Dict[str, Any] = {
    "prefix_trg": "/ENTRY[entry*]/atom_probeID[atom_probe]/reconstruction",
    "prefix_src": "reconstruction/",
    "map_to_str": [
        ("config/protocol_name", "protocol_name"),
        ("config/crystallographic_calibration", "crystallographic_calibration"),
        ("config/comment", "parameter"),
        ("programID[program1]/program", "program_name"),
        ("programID[program1]/program/@version", "program_version"),
    ],
    "map_to_f8": [
        ("field_of_view", ureg.nanometer, "field_of_view/value", "field_of_view/unit"),
        ("flight_path", ureg.meter, "flight_path/value", "flight_path/unit"),
    ],
}


APM_WORKFLOW_TO_NEXUS: Dict[str, Any] = {
    "prefix_trg": "/ENTRY[entry*]/atom_probeID[atom_probe]",
    "prefix_src": "workflow/",
    "sha256": [
        ("raw_data/source/checksum", "raw_dat_file"),
        ("hit_finding/config/checksum", "hit_dat_file"),
        ("reconstruction/source/checksum", "recon_cfg_file"),
    ],
}

# NeXus concept specific mapping tables which require special treatment as the current
# NOMAD Oasis custom schema implementation delivers them as a list of dictionaries instead
# of a directly flattenable list of key, value pairs

APM_USER_TO_NEXUS: Dict[str, Any] = {
    "prefix_trg": "/ENTRY[entry*]/userID[user*]",
    "prefix_src": "",
    "map": [
        "name",
        "affiliation",
        "address",
        "email",
        "telephone_number",
        "role",
    ],
}
