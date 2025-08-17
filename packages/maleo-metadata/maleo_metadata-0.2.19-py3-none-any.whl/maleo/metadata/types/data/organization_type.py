from typing import List, Optional
from maleo.metadata.enums.organization_type import OrganizationType
from maleo.metadata.schemas.data.organization_type import OrganizationTypeDataSchema


# Simple organization type
SimpleOrganizationType = OrganizationType
OptionalSimpleOrganizationType = Optional[SimpleOrganizationType]
ListOfSimpleOrganizationTypes = List[SimpleOrganizationType]
OptionalListOfSimpleOrganizationTypes = Optional[List[SimpleOrganizationType]]

# Expanded organization type
ExpandedOrganizationType = OrganizationTypeDataSchema
OptionalExpandedOrganizationType = Optional[ExpandedOrganizationType]
ListOfExpandedOrganizationTypes = List[ExpandedOrganizationType]
OptionalListOfExpandedOrganizationTypes = Optional[List[ExpandedOrganizationType]]
