from pydantic import BaseModel, Field
from typing import List, Optional
from maleo.soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo.metadata.dtos.data.system_role import SystemRoleDataDTO
from maleo.metadata.enums.system_role import SystemRole


class SystemRoleDataSchema(
    SystemRoleDataDTO,
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    pass


class SimpleSystemRoleMixin(BaseModel):
    system_role: SystemRole = Field(..., description="Single System Role")


class OptionalSimpleSystemRoleMixin(BaseModel):
    system_role: Optional[SystemRole] = Field(
        None, description="Single System Role. (Optional)"
    )


class ListOfSimpleSystemRolesMixin(BaseModel):
    system_roles: List[SystemRole] = Field(..., description="Multiple System Roles")


class OptionalListOfSimpleSystemRolesMixin(BaseModel):
    system_roles: Optional[List[SystemRole]] = Field(
        None, description="Multiple System Roles. (Optional)"
    )


class ExpandedSystemRoleMixin(BaseModel):
    system_role_details: SystemRoleDataSchema = Field(
        ..., description="Single System Role Data"
    )


class OptionalExpandedSystemRoleMixin(BaseModel):
    system_role_details: Optional[SystemRoleDataSchema] = Field(
        None, description="Single System Role Data. (Optional)"
    )


class ListOfExpandedSystemRolesMixin(BaseModel):
    system_roles_details: List[SystemRoleDataSchema] = Field(
        ..., description="Multiple System Roles Data"
    )


class OptionalListOfExpandedSystemRolesMixin(BaseModel):
    system_roles_details: Optional[List[SystemRoleDataSchema]] = Field(
        None, description="Multiple System Roles Data. (Optional)"
    )
