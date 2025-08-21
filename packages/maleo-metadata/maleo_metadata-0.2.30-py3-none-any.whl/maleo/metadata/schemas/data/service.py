from pydantic import BaseModel, Field
from typing import List, Optional
from maleo.soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo.metadata.dtos.data.service import ServiceDataDTO, FullServiceDataDTO
from maleo.metadata.enums.service import Service


class ServiceDataSchema(
    ServiceDataDTO,
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    pass


class FullServiceDataSchema(
    FullServiceDataDTO,
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    pass


class SimpleServiceMixin(BaseModel):
    service: Service = Field(..., description="Single Service")


class OptionalSimpleServiceMixin(BaseModel):
    service: Optional[Service] = Field(None, description="Single Service. (Optional)")


class ListOfSimpleServicesMixin(BaseModel):
    services: List[Service] = Field(..., description="Multiple Services")


class OptionalListOfSimpleServicesMixin(BaseModel):
    services: Optional[List[Service]] = Field(
        None, description="Multiple Services. (Optional)"
    )


class ExpandedServiceMixin(BaseModel):
    service_details: ServiceDataSchema = Field(..., description="Single Service Data")


class OptionalExpandedServiceMixin(BaseModel):
    service_details: Optional[ServiceDataSchema] = Field(
        None, description="Single Service Data. (Optional)"
    )


class ListOfExpandedServicesMixin(BaseModel):
    services_details: List[ServiceDataSchema] = Field(
        ..., description="Multiple Services Data"
    )


class OptionalListOfExpandedServicesMixin(BaseModel):
    services_details: Optional[List[ServiceDataSchema]] = Field(
        None, description="Multiple Services Data. (Optional)"
    )


class ExpandedFullServiceMixin(BaseModel):
    full_service: FullServiceDataSchema = Field(
        ..., description="Single Full Service Data"
    )


class OptionalExpandedFullServiceMixin(BaseModel):
    full_service: Optional[FullServiceDataSchema] = Field(
        None, description="Single Full Service Data. (Optional)"
    )


class ListOfExpandedFullServicesMixin(BaseModel):
    full_services: List[FullServiceDataSchema] = Field(
        ..., description="Multiple Full Services Data"
    )


class OptionalListOfExpandedFullServicesMixin(BaseModel):
    full_services: Optional[List[FullServiceDataSchema]] = Field(
        None, description="Multiple Full Services Data. (Optional)"
    )
