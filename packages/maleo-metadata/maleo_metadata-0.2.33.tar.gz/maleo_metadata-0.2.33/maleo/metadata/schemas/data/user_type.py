from pydantic import BaseModel, Field
from typing import List, Optional
from maleo.soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo.metadata.dtos.data.user_type import UserTypeDataDTO
from maleo.metadata.enums.user_type import UserType


class UserTypeDataSchema(
    UserTypeDataDTO,
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    pass


class SimpleUserTypeMixin(BaseModel):
    user_type: UserType = Field(..., description="Single User Type")


class OptionalSimpleUserTypeMixin(BaseModel):
    user_type: Optional[UserType] = Field(
        None, description="Single User Type. (Optional)"
    )


class ListOfSimpleUserTypesMixin(BaseModel):
    user_types: List[UserType] = Field(..., description="Multiple User Types")


class OptionalListOfSimpleUserTypesMixin(BaseModel):
    user_types: Optional[List[UserType]] = Field(
        None, description="Multiple User Types. (Optional)"
    )


class ExpandedUserTypeMixin(BaseModel):
    user_type_details: UserTypeDataSchema = Field(
        ..., description="Single User Type Data"
    )


class OptionalExpandedUserTypeMixin(BaseModel):
    user_type_details: Optional[UserTypeDataSchema] = Field(
        None, description="Single User Type Data. (Optional)"
    )


class ListOfExpandedUserTypesMixin(BaseModel):
    user_types_details: List[UserTypeDataSchema] = Field(
        ..., description="Multiple User Types Data"
    )


class OptionalListOfExpandedUserTypesMixin(BaseModel):
    user_types_details: Optional[List[UserTypeDataSchema]] = Field(
        None, description="Multiple User Types Data. (Optional)"
    )
