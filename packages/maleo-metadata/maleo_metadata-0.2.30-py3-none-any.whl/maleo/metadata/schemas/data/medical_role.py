from pydantic import BaseModel, Field
from typing import List, Optional
from maleo.soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo.metadata.dtos.data.medical_role import MedicalRoleDataDTO
from maleo.metadata.enums.medical_role import MedicalRole


class MedicalRoleDataSchema(
    MedicalRoleDataDTO,
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    pass


class SimpleMedicalRoleMixin(BaseModel):
    medical_role: MedicalRole = Field(..., description="Single Medical Role")


class OptionalSimpleMedicalRoleMixin(BaseModel):
    medical_role: Optional[MedicalRole] = Field(
        None, description="Single Medical Role. (Optional)"
    )


class ListOfSimpleMedicalRolesMixin(BaseModel):
    medical_roles: List[MedicalRole] = Field(..., description="Multiple Medical Roles")


class OptionalListOfSimpleMedicalRolesMixin(BaseModel):
    medical_roles: Optional[List[MedicalRole]] = Field(
        None, description="Multiple Medical Roles. (Optional)"
    )


class ExpandedMedicalRoleMixin(BaseModel):
    medical_role_details: MedicalRoleDataSchema = Field(
        ..., description="Single Medical Role Data"
    )


class OptionalExpandedMedicalRoleMixin(BaseModel):
    medical_role_details: Optional[MedicalRoleDataSchema] = Field(
        None, description="Single Medical Role Data. (Optional)"
    )


class ListOfExpandedMedicalRolesMixin(BaseModel):
    medical_roles_details: List[MedicalRoleDataSchema] = Field(
        ..., description="Multiple Medical Roles Data"
    )


class OptionalListOfExpandedMedicalRolesMixin(BaseModel):
    medical_roles_details: Optional[List[MedicalRoleDataSchema]] = Field(
        None, description="Multiple Medical Roles Data. (Optional)"
    )
