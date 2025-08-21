# Copyright (c) 2023 Qumulo, Inc.
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

from typing import Callable, Mapping, Optional

TenantId = int
EntryId = int


def get_entry_id_from_entries(
    entry_id: Optional[int],
    entry_name: Optional[str],
    tenant_id: Optional[int],
    entry_type: str,
    get_entries_matching_name: Callable[[str], Mapping[Optional[TenantId], EntryId]],
) -> int:
    if entry_id:
        return entry_id

    # Each tenant may have an entry with the given entry name. First find all the matching entries.
    assert entry_name is not None
    potential_entries = get_entries_matching_name(entry_name)

    if tenant_id:
        # If a tenant id was provided, use it to determine which entry to use.
        if tenant_id in potential_entries:
            return potential_entries[tenant_id]
        else:
            raise ValueError(
                f'{entry_type} matching {entry_name} and tenant {tenant_id} does not exist'
            )
    else:
        # If a tenant id was not provided, see if we can assume which entry to use.
        if len(potential_entries) == 0:
            raise ValueError(f'{entry_type} matching {entry_name} does not exist')
        elif len(potential_entries) == 1:
            return list(potential_entries.values())[0]
        else:
            raise ValueError(
                f'{entry_type} matching {entry_name} is ambiguous, must specify --tenant-id. '
                f'Tenants with matching entry: {potential_entries.keys()}'
            )
