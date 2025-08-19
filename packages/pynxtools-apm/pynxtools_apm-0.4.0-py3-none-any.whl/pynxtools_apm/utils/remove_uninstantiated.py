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
"""Remove uninstantiated concepts that were added by the "use" functor."""

import re


def remove_uninstantiated_sensors(template: dict, entry_id: int = 1) -> dict:
    """Deletes sensors that have been added by the use functor but have no values."""
    for key in template:
        if not key.endswith("/measurement"):
            continue
        for rgx in [
            r"/ENTRY\[entry[0-9]+\]/measurement/eventID\[event[0-9]+\]/instrument/analysis_chamber/pressure_sensor/measurement",
            r"/ENTRY\[entry[0-9]+\]/measurement/eventID\[event[0-9]+\]/instrument/stage/temperature_sensor/measurement",
        ]:
            match = re.search(rgx, key)
            if match and key.replace("/measurement", "/value") not in template:
                del template[key]
    return template
