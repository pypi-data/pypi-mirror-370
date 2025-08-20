from pydantic import BaseModel, Field
from maleo.soma.types.base import OptionalString


class Code(BaseModel):
    code: str = Field(..., max_length=20, description="Medical role's code")


class OptionalCode(BaseModel):
    code: OptionalString = Field(
        None, max_length=20, description="Medical role's code. (Optional)"
    )


class Key(BaseModel):
    key: str = Field(..., max_length=255, description="Medical role's key")


class Name(BaseModel):
    name: str = Field(..., max_length=255, description="Medical role's name")


class OptionalName(BaseModel):
    name: OptionalString = Field(
        None, max_length=255, description="Medical role's name. (Optional)"
    )


class MedicalRoleId(BaseModel):
    medical_role_id: int = Field(..., ge=1, description="Medical role's id")
