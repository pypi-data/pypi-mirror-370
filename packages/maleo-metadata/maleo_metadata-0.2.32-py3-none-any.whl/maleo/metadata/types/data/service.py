from typing import List, Optional
from maleo.metadata.enums.service import Service
from maleo.metadata.schemas.data.service import ServiceDataSchema, FullServiceDataSchema


# Simple service
SimpleService = Service
OptionalSimpleService = Optional[SimpleService]
ListOfSimpleServices = List[SimpleService]
OptionalListOfSimpleServices = Optional[List[SimpleService]]

# Expanded service
ExpandedService = ServiceDataSchema
OptionalExpandedService = Optional[ExpandedService]
ListOfExpandedServices = List[ExpandedService]
OptionalListOfExpandedServices = Optional[List[ExpandedService]]

# Expanded full service
ExpandedFullService = FullServiceDataSchema
OptionalExpandedFullService = Optional[ExpandedFullService]
ListOfExpandedFullServices = List[ExpandedFullService]
OptionalListOfExpandedFullServices = Optional[List[ExpandedFullService]]
