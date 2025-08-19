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
"""Generator for NXapm default plots."""

import numpy as np

from pynxtools_apm.utils.custom_logging import logger
from pynxtools_apm.utils.versioning import (
    MASS_SPECTRUM_DEFAULT_BINNING,
    NAIVE_GRID_DEFAULT_VOXEL_SIZE,
    NX_APM_EXEC_NAME,
    NX_APM_EXEC_VERSION,
)


def decorate_path_to_default_plot(template: dict, nxpath: str) -> dict:
    """Write @default attribute to point to the default plot."""
    # an example for nxpath
    # "/ENTRY[entry1]/atom_probeID[atom_probe]/ranging/mass_to_charge_distribution/mass_spectrum"
    path = nxpath.split("/")
    trg = "/"
    for idx in np.arange(0, len(path) - 1):
        symbol_s = path[idx + 1].find("[")
        symbol_e = path[idx + 1].find("]")
        if 0 <= symbol_s < symbol_e:
            template[f"{trg}@default"] = f"{path[idx + 1][symbol_s + 1 : symbol_e]}"
            trg += f"{path[idx + 1]}/"
        else:
            template[f"{trg}@default"] = f"{path[idx + 1]}"
            trg += f"{path[idx + 1]}/"
    return template


def iedge(imi, imx, resolution):
    """Generate linearly-spaced support positions."""
    return np.linspace(
        imi, imx, num=int(np.ceil((imx - imi) / resolution)) + 1, endpoint=True
    )


def icenter(imi, imx, resolution):
    """Generate approximate center of linearly-spaced support positions."""
    return int(np.ceil((imx - imi) / resolution) / 2) + 1


def create_default_plot_reconstruction(template: dict, entry_id: int) -> dict:
    """Compute on-the-fly, add, and give path to discretized reconstruction."""
    trg = f"/ENTRY[entry{entry_id}]/atom_probeID[atom_probe]/reconstruction/"
    xyz = template[f"{trg}reconstructed_positions"]["compress"]

    logger.debug(f"\tEnter histogram computation, np.shape(xyz) {np.shape(xyz)}")
    # make the bounding box a quadric prism, discretized using cubic voxel edge in nm
    aabb: dict = {
        "x": [0.0, 0.0],
        "y": [0.0, 0.0],
        "z": [0.0, 0.0],
        "xedge": None,
        "yedge": None,
        "zedge": None,
    }
    col = 0
    logger.debug("reconstruction aabb3d")
    for dim in ["x", "y", "z"]:
        aabb[f"{dim}"] = [np.min(xyz[:, col]), np.max(xyz[:, col])]
        logger.debug(f"\t{dim}: {aabb[f'''{dim}''']}")
        imi = np.floor(aabb[f"{dim}"][0]) - NAIVE_GRID_DEFAULT_VOXEL_SIZE
        imx = np.ceil(aabb[f"{dim}"][1]) + NAIVE_GRID_DEFAULT_VOXEL_SIZE
        aabb[f"{dim}edge"] = iedge(imi, imx, NAIVE_GRID_DEFAULT_VOXEL_SIZE)
        col += 1

    hist3d = np.histogramdd(
        (xyz[:, 0], xyz[:, 1], xyz[:, 2]),
        bins=(aabb["xedge"], aabb["yedge"], aabb["zedge"]),
    )
    del xyz
    if isinstance(hist3d[0], np.ndarray) is False:
        raise ValueError("Hist3d computation from the reconstruction failed!")
    if len(np.shape(hist3d[0])) != 3:
        raise ValueError("Hist3d computation from the reconstruction failed!")
    for idx in [0, 1, 2]:
        if np.shape(hist3d[0])[idx] == 0:
            raise ValueError(f"Dimensions {idx} has no length!")

    trg = f"/ENTRY[entry{entry_id}]/atom_probeID[atom_probe]/reconstruction/naive_discretization/"
    template[f"{trg}programID[program1]/program"] = NX_APM_EXEC_NAME
    template[f"{trg}programID[program1]/program/@version"] = NX_APM_EXEC_VERSION
    trg = (
        f"/ENTRY[entry{entry_id}]/atom_probeID[atom_probe]/reconstruction/"
        f"naive_discretization/DATA[data]/"
    )
    template[f"{trg}title"] = "Discretized reconstruction space"
    # template[f"{trg}@long_name"] = "Discretized reconstruction space"
    template[f"{trg}@signal"] = "intensity"
    template[f"{trg}@default_slice"] = [
        ".",
        f"{icenter(imi, imx, NAIVE_GRID_DEFAULT_VOXEL_SIZE)}",
        ".",
    ]
    # there is an issue lately with H5Web in how it reads default_slice
    # both options, the abovementioned and this one should work but with
    # jupyterlab_h5web 12.4.0 and hgrove 2.3.0
    # template[f"{trg}@default_slice"] = []
    # for dim in ["x", "y", "z"]:
    #     imi = np.floor(aabb[f"{dim}"][0]) - NAIVE_GRID_DEFAULT_VOXEL_SIZE
    #     imx = np.ceil(aabb[f"{dim}"][1]) + NAIVE_GRID_DEFAULT_VOXEL_SIZE
    #     template[f"{trg}@default_slice"].append(
    #         icenter(imi, imx, NAIVE_GRID_DEFAULT_VOXEL_SIZE)
    #     )

    col = 0
    dims = ["x", "y", "z"]
    axes = []
    for dim in dims:
        axes.append(f"axis_{dim}")
        template[f"{trg}@AXISNAME_indices[@axis_{dim}_indices]"] = np.uint32(col)
        col += 1
    template[f"{trg}@axes"] = axes

    # mind that histogram does not follow Cartesian conventions so a transpose
    # might be necessary, for now we implement the transpose in the appdef
    template[f"{trg}intensity"] = {
        "compress": np.asarray(hist3d[0], np.uint32),
        "strength": 1,
    }
    col = 0
    for dim in dims:
        template[f"{trg}AXISNAME[axis_{dim}]"] = {
            "compress": np.asarray(hist3d[1][col][1::], np.float32),
            "strength": 1,
        }
        template[f"{trg}AXISNAME[axis_{dim}]/@units"] = "nm"
        template[f"{trg}AXISNAME[axis_{dim}]/@long_name"] = f"{dim} (nm)"
        col += 1
    logger.debug(
        f"Default plot naive discretization 3D {NAIVE_GRID_DEFAULT_VOXEL_SIZE} nm^3."
    )
    return template


def create_default_plot_mass_spectrum(template: dict, entry_id: int) -> dict:
    """Compute on-the-fly, add, and give path to discretized reconstruction."""
    trg = f"/ENTRY[entry{entry_id}]/atom_probeID[atom_probe]/mass_to_charge_conversion/"
    m_z = template[f"{trg}mass_to_charge"]["compress"]

    logger.debug(f"\tEnter mass spectrum computation, np.shape(m_z) {np.shape(m_z)}")
    # the next three in u
    mqmin = 0.0
    mqincr = MASS_SPECTRUM_DEFAULT_BINNING
    mqmax = np.ceil(np.max(m_z[:]))
    nmqchrg = int(np.ceil((mqmax - mqmin) / mqincr)) + 1

    hist1d = np.histogram(
        m_z[:],
        np.linspace(mqmin, mqmax, num=nmqchrg, endpoint=True),
    )
    del m_z
    if isinstance(hist1d[0], np.ndarray) is False:
        raise ValueError("Hist1d computation from the mass spectrum failed!")
    if len(np.shape(hist1d[0])) != 1:
        raise ValueError("Hist1d computation from the mass spectrum failed!")
    for idx in np.arange(0, 1):
        if np.shape(hist1d[0])[idx] == 0:
            raise ValueError(f"Dimensions {idx} has no length!")

    trg = f"/ENTRY[entry{entry_id}]/atom_probeID[atom_probe]/ranging/mass_to_charge_distribution/"
    template[f"{trg}programID[program1]/program"] = NX_APM_EXEC_NAME
    template[f"{trg}programID[program1]/program/@version"] = NX_APM_EXEC_VERSION

    template[f"{trg}min_mass_to_charge"] = np.float32(mqmin)
    template[f"{trg}min_mass_to_charge/@units"] = "Da"
    template[f"{trg}max_mass_to_charge"] = np.float32(mqmax)
    template[f"{trg}max_mass_to_charge/@units"] = "Da"
    template[f"{trg}n_mass_to_charge"] = np.uint32(nmqchrg)
    trg = (
        f"/ENTRY[entry{entry_id}]/atom_probeID[atom_probe]/ranging/"
        f"mass_to_charge_distribution/mass_spectrum/"
    )
    template[f"{trg}title"] = (
        f"Mass spectrum ({MASS_SPECTRUM_DEFAULT_BINNING} Da binning)"
    )
    template[f"{trg}@signal"] = "intensity"
    template[f"{trg}@axes"] = "axis_mass_to_charge"
    template[f"{trg}@AXISNAME_indices[@axis_mass_to_charge_indices]"] = np.uint32(0)
    template[f"{trg}DATA[intensity]"] = {
        "compress": np.asarray(hist1d[0], np.uint32),
        "strength": 1,
    }
    template[f"{trg}DATA[intensity]/@long_name"] = "Intensity (1)"  # Counts (1)"
    template[f"{trg}AXISNAME[axis_mass_to_charge]"] = {
        "compress": np.asarray(hist1d[1][1::], np.float32),
        "strength": 1,
    }
    del hist1d
    template[f"{trg}AXISNAME[axis_mass_to_charge]/@units"] = "Da"
    template[f"{trg}AXISNAME[axis_mass_to_charge]/@long_name"] = (
        "Mass-to-charge-state-ratio (Da)"
    )
    logger.debug(
        f"Plot mass spectrum at {MASS_SPECTRUM_DEFAULT_BINNING} Da binning was created."
    )
    return template


def apm_default_plot_generator(template: dict, entry_id: int) -> dict:
    """Copy data from self into template the appdef instance."""
    logger.debug("Create default plots on-the-fly...")
    # default plot is histogram of mass-to-charge-state-ratio values (aka mass spectrum)
    # naively discretized 3D reconstruction as a fallback

    has_valid_m_z = False
    trg = f"/ENTRY[entry{entry_id}]/atom_probeID[atom_probe]/mass_to_charge_conversion/mass_to_charge"
    if trg in template:
        if isinstance(template[trg], dict):
            if "compress" in template[trg]:
                if isinstance(template[trg]["compress"], np.ndarray):
                    has_valid_m_z = True
    has_valid_xyz = False
    trg = f"/ENTRY[entry{entry_id}]/atom_probeID[atom_probe]/reconstruction/reconstructed_positions"
    if trg in template:
        if isinstance(template[trg], dict):
            if "compress" in template[trg]:
                if isinstance(template[trg]["compress"], np.ndarray):
                    has_valid_xyz = True
    logger.debug(f"m_z, xyz: {has_valid_m_z}, {has_valid_xyz}")

    if (has_valid_m_z is False) and (has_valid_xyz is False):
        # NEW ISSUE: fall-back solution to plot something else, however
        # currently POS, EPOS and APT provide always xyz, and m_z data
        return template

    # generate default plottable and add path
    if has_valid_m_z:
        create_default_plot_mass_spectrum(template, entry_id)
        decorate_path_to_default_plot(
            template,
            f"/ENTRY[entry{entry_id}]/atom_probeID[atom_probe]/ranging/"
            f"mass_to_charge_distribution/mass_spectrum",
        )

    if has_valid_xyz:
        create_default_plot_reconstruction(template, entry_id)
        if has_valid_m_z is False:
            decorate_path_to_default_plot(
                template,
                f"/ENTRY[entry{entry_id}]/atom_probeID[atom_probe]/reconstruction/"
                f"naive_discretization/DATA[data]",
            )
    return template
