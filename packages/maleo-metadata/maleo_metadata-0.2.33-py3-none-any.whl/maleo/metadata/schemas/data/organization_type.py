from pydantic import BaseModel, Field
from typing import List, Optional
from maleo.soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo.metadata.dtos.data.organization_type import OrganizationTypeDataDTO
from maleo.metadata.enums.organization_type import OrganizationType


class OrganizationTypeDataSchema(
    OrganizationTypeDataDTO,
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    pass


class SimpleOrganizationTypeMixin(BaseModel):
    organization_type: OrganizationType = Field(
        ..., description="Single Organization Type"
    )


class OptionalSimpleOrganizationTypeMixin(BaseModel):
    organization_type: Optional[OrganizationType] = Field(
        None, description="Single Organization Type. (Optional)"
    )


class ListOfSimpleOrganizationTypesMixin(BaseModel):
    organization_types: List[OrganizationType] = Field(
        ..., description="Multiple Organization Types"
    )


class OptionalListOfSimpleOrganizationTypesMixin(BaseModel):
    organization_types: Optional[List[OrganizationType]] = Field(
        None, description="Multiple Organization Types. (Optional)"
    )


class ExpandedOrganizationTypeMixin(BaseModel):
    organization_type_details: OrganizationTypeDataSchema = Field(
        ..., description="Single Organization Type Data"
    )


class OptionalExpandedOrganizationTypeMixin(BaseModel):
    organization_type_details: Optional[OrganizationTypeDataSchema] = Field(
        None, description="Single Organization Type Data. (Optional)"
    )


class ListOfExpandedOrganizationTypesMixin(BaseModel):
    organization_types_details: List[OrganizationTypeDataSchema] = Field(
        ..., description="Multiple Organization Types Data"
    )


class OptionalListOfExpandedOrganizationTypesMixin(BaseModel):
    organization_types_details: Optional[List[OrganizationTypeDataSchema]] = Field(
        None, description="Multiple Organization Types Data. (Optional)"
    )
