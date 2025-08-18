from typing import List, Optional
from maleo.metadata.enums.system_role import SystemRole
from maleo.metadata.schemas.data.system_role import SystemRoleDataSchema


# Simple system role
SimpleSystemRole = SystemRole
OptionalSimpleSystemRole = Optional[SimpleSystemRole]
ListOfSimpleSystemRoles = List[SimpleSystemRole]
OptionalListOfSimpleSystemRoles = Optional[List[SimpleSystemRole]]

# Expanded system role
ExpandedSystemRole = SystemRoleDataSchema
OptionalExpandedSystemRole = Optional[ExpandedSystemRole]
ListOfExpandedSystemRoles = List[ExpandedSystemRole]
OptionalListOfExpandedSystemRoles = Optional[List[ExpandedSystemRole]]
