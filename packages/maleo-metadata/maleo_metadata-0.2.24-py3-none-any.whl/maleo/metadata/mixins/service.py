from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from maleo.soma.enums.service import (
    ServiceType as ServiceTypeEnum,
    Category as CategoryEnum,
)
from maleo.soma.types.base import OptionalString


class ServiceType(BaseModel):
    type: ServiceTypeEnum = Field(..., description="Service's type")


class OptionalServiceType(BaseModel):
    type: Optional[ServiceTypeEnum] = Field(
        None, description="Service's type. (Optional)"
    )


class Category(BaseModel):
    category: CategoryEnum = Field(..., description="Service's category")


class OptionalCategory(BaseModel):
    category: Optional[CategoryEnum] = Field(
        None, description="Service's category. (Optional)"
    )


class Key(BaseModel):
    key: str = Field(..., max_length=20, description="Service's key")


class Name(BaseModel):
    name: str = Field(..., max_length=20, description="Service's name")


class OptionalName(BaseModel):
    name: OptionalString = Field(
        None, max_length=20, description="Service's name. (Optional)"
    )


class Secret(BaseModel):
    secret: UUID = Field(..., description="Service's secret")
