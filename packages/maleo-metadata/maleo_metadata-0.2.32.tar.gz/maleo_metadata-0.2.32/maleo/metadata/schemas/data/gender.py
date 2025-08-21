from pydantic import BaseModel, Field
from typing import List, Optional
from maleo.soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo.metadata.dtos.data.gender import GenderDataDTO
from maleo.metadata.enums.gender import Gender


class GenderDataSchema(
    GenderDataDTO,
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    pass


class SimpleGenderMixin(BaseModel):
    gender: Gender = Field(..., description="Single Gender")


class OptionalSimpleGenderMixin(BaseModel):
    gender: Optional[Gender] = Field(None, description="Single Gender. (Optional)")


class ListOfSimpleGendersMixin(BaseModel):
    genders: List[Gender] = Field(..., description="Multiple Genders")


class OptionalListOfSimpleGendersMixin(BaseModel):
    genders: Optional[List[Gender]] = Field(
        None, description="Multiple Genders. (Optional)"
    )


class ExpandedGenderMixin(BaseModel):
    gender_details: GenderDataSchema = Field(..., description="Single Gender Data")


class OptionalExpandedGenderMixin(BaseModel):
    gender_details: Optional[GenderDataSchema] = Field(
        None, description="Single Gender Data. (Optional)"
    )


class ListOfExpandedGendersMixin(BaseModel):
    genders_details: List[GenderDataSchema] = Field(
        ..., description="Multiple Genders Data"
    )


class OptionalListOfExpandedGendersMixin(BaseModel):
    genders_details: Optional[List[GenderDataSchema]] = Field(
        None, description="Multiple Genders Data. (Optional)"
    )
