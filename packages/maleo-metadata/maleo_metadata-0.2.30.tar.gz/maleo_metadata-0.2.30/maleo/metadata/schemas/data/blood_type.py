from pydantic import BaseModel, Field
from typing import List, Optional
from maleo.soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo.metadata.dtos.data.blood_type import BloodTypeDataDTO
from maleo.metadata.enums.blood_type import BloodType


class BloodTypeDataSchema(
    BloodTypeDataDTO,
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    pass


class SimpleBloodTypeMixin(BaseModel):
    blood_type: BloodType = Field(..., description="Single Blood Type")


class OptionalSimpleBloodTypeMixin(BaseModel):
    blood_type: Optional[BloodType] = Field(
        None, description="Single Blood Type. (Optional)"
    )


class ListOfSimpleBloodTypesMixinMixin(BaseModel):
    blood_types: List[BloodType] = Field(..., description="Multiple Blood Types")


class OptionalListOfSimpleBloodTypesMixin(BaseModel):
    blood_types: Optional[List[BloodType]] = Field(
        None, description="Multiple Blood Types. (Optional)"
    )


class ExpandedBloodTypeMixin(BaseModel):
    blood_type_details: BloodTypeDataSchema = Field(
        ..., description="Single Blood Type Data"
    )


class OptionalExpandedBloodTypeMixin(BaseModel):
    blood_type_details: Optional[BloodTypeDataSchema] = Field(
        None, description="Single Blood Type Data. (Optional)"
    )


class ListOfExpandedBloodTypesMixin(BaseModel):
    blood_types_details: List[BloodTypeDataSchema] = Field(
        ..., description="Multiple Blood Types Data"
    )


class OptionalListOfExpandedBloodTypesMixin(BaseModel):
    blood_types_details: Optional[List[BloodTypeDataSchema]] = Field(
        None, description="Multiple Blood Types Data. (Optional)"
    )
