# Copyright (c) 2022 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import dataclasses

from typing import Any, Dict


def dataclass_to_dict_omit_none_fields(obj: object) -> Dict[str, Any]:
    """
    Convert dataclass to dictionary omitting fields that are None. Useful for implementing to_dict()
    in dataclasses representing API structures with optional fields.
    """
    out = {}
    for field in dataclasses.fields(obj):  # type: ignore[arg-type]
        value = getattr(obj, field.name)
        if value is not None:
            to_dict_op = getattr(value, 'to_dict', None)
            if callable(to_dict_op):
                # If the value has a to_dict method, recurse into this.
                out[field.name] = value.to_dict()
            else:
                out[field.name] = value
    return out
