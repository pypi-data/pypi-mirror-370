from pydantic import BaseModel, Field
from maleo.soma.types.base import OptionalString


class Key(BaseModel):
    key: str = Field(..., max_length=20, description="Organization type's key")


class Name(BaseModel):
    name: str = Field(..., max_length=20, description="Organization type's name")


class OptionalName(BaseModel):
    name: OptionalString = Field(
        None, max_length=20, description="Organization type's name. (Optional)"
    )
