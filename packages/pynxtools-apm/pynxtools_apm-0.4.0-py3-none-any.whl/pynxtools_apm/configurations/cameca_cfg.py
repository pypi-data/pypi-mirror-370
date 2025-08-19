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
"""Dict mapping custom schema instances from custom yaml file on concepts in NXapm."""

from typing import Any, Dict

from pynxtools_apm.utils.pint_custom_unit_registry import ureg

APM_CAMECA_TO_NEXUS: Dict[str, Any] = {
    "prefix_trg": "/ENTRY[entry*]",
    "prefix_src": "",
    "use": [
        (
            "measurement/eventID[event*]/instrument/analysis_chamber/pressure_sensor/measurement",
            "pressure",
        ),
        (
            "measurement/eventID[event*]/instrument/stage/temperature_sensor/measurement",
            "temperature",
        ),
    ],
    "cameca_to_iso8601": [("start_time", "fStartISO8601")],
    "map_to_str": [
        ("atom_probeID[atom_probe]/reconstruction/quality", "fQuality"),
        (
            "atom_probeID[atom_probe]/reconstruction/config/primary_element",
            "fPrimaryElement",
        ),
        ("measurement/instrument/local_electrode/name", "fApertureName"),
        ("measurement/instrument/name", "fAtomProbeName"),
        ("measurement/instrument/fabrication/model", "fLeapModel"),
        ("measurement/instrument/fabrication/serial_number", "fSerialNumber"),
        (
            "measurement/instrument/pulser/sourceID[source*]/fabrication/model",
            "fLaserModelString",
        ),
        (
            "measurement/instrument/pulser/sourceID[source*]/fabrication/serial_number",
            "fLaserSerialNumber",
        ),
        (
            "measurement/instrument/pulser/fabrication/model",
            "fPulserType",
        ),
        ("measurement/instrument/comment", "fInstrumentComment"),
        ("atom_probeID[atom_probe]/raw_data/source/file_name", "fRawPathName"),
        ("measurement/status", "fResults"),
        ("specimen/description", "fSpecimenCondition"),
        ("specimen/alias", "fSpecimenName"),
    ],
    "map_to_u4": [("run_number", "fRunNumber")],
    "map_to_f8": [
        ("atom_probeID[atom_probe]/reconstruction/config/efficiency", "fEfficiency"),
        (
            "atom_probeID[atom_probe]/reconstruction/config/evaporation_field",
            ureg.volt / ureg.nanometer**2,
            "fEvaporationField",
        ),
        (
            "atom_probeID[atom_probe]/reconstruction/config/flight_path",
            ureg.millimeter,
            "fFlightPath",
        ),
        (
            "atom_probeID[atom_probe]/reconstruction/config/image_compression",
            "fImageCompression",
        ),  # ??
        ("atom_probeID[atom_probe]/reconstruction/config/kfactor", "fKfactor"),  # ??
        (
            "atom_probeID[atom_probe]/reconstruction/volume",
            ureg.nanometer**3,
            "fReconVolume",
        ),
        (
            "atom_probeID[atom_probe]/reconstruction/config/shank_angle",
            ureg.degrees,
            "fShankAngle",
        ),
        ("atom_probeID[atom_probe]/reconstruction/obb/xmax", ureg.nanometer, "fXmax"),
        ("atom_probeID[atom_probe]/reconstruction/obb/xmin", ureg.nanometer, "fXmin"),
        ("atom_probeID[atom_probe]/reconstruction/obb/ymax", ureg.nanometer, "fYmax"),
        ("atom_probeID[atom_probe]/reconstruction/obb/ymin", ureg.nanometer, "fYmin"),
        ("atom_probeID[atom_probe]/reconstruction/obb/zmax", ureg.nanometer, "fZmax"),
        ("atom_probeID[atom_probe]/reconstruction/obb/zmin", ureg.nanometer, "fZmin"),
        (
            "atom_probeID[atom_probe]/reconstruction/config/tip_radius",
            ureg.nanometer,
            "fTipRadius",
        ),
        (
            "atom_probeID[atom_probe]/reconstruction/config/tip_radius_zero",
            ureg.nanometer,
            "fTipRadius0",
        ),
        (
            "atom_probeID[atom_probe]/reconstruction/config/voltage_zero",
            ureg.volt,
            "fVoltage0",
        ),
        (
            "measurement/eventID[event*]/instrument/analysis_chamber/pressure_sensor/value",
            ureg.bar,
            "fAnalysisPressure",
            ureg.torr,
        ),
        (
            "measurement/eventID[event*]/instrument/local_electrode/voltage",
            ureg.volt,
            "fAnodeAccelVoltage",
        ),
        ("elapsed_time", ureg.second, "fElapsedTime"),
        (
            "measurement/eventID[event*]/instrument/pulser/pulse_frequency",
            ureg.kilohertz,
            "fInitialPulserFreq",
        ),
        ("measurement/instrument/ion_detector/mcp_efficiency", "fMcpEfficiency"),
        ("measurement/instrument/ion_detector/mesh_efficiency", "fMeshEfficiency"),
        (
            "measurement/instrument/flight_path",
            ureg.millimeter,
            "fMaximumFlightPathMm",
        ),
        (
            "measurement/eventID[event*]/instrument/stage/temperature_sensor/value",
            ureg.kelvin,
            "fSpecimenTemperature",
        ),
        (
            "atom_probeID[atom_probe]/voltage_and_bowl/tof_zero_estimate",
            ureg.nanosecond,
            "fT0Estimate",
        ),
    ],
}

# third
# ("", "fBcaSerialRev")
# ("", "fFirmwareVersion")
# ("", "fFlangeSerialNumber")
# ("", "fHvpsType")
# ("", "fLaserModel")
# ("", "fLcbSerialRev")
# ("", "fMcpSerialNumber")
# ("", "fTaSerialRev")
# ("", "fTdcType")
# ("", "fTargetEvapRate")
# ("", "fTargetPulseFraction")
# ("", "fPidAlgorithmID")
# ("", "fPidMaxInitialSlew")
# ("", "fPidMaxTurnOnSlew")
# ("", "fPidPropCoef")
# ("", "fPidPulsesPerUpdate")
# ("", "fPidTradHysterisis")
# ("", "fPidTradStep")
