from typing import List, Optional
from maleo.metadata.enums.user_type import UserType
from maleo.metadata.schemas.data.user_type import UserTypeDataSchema


# Simple user type
SimpleUserType = UserType
OptionalSimpleUserType = Optional[SimpleUserType]
ListOfSimpleUserTypes = List[SimpleUserType]
OptionalListOfSimpleUserTypes = Optional[List[SimpleUserType]]

# Expanded user type
ExpandedUserType = UserTypeDataSchema
OptionalExpandedUserType = Optional[ExpandedUserType]
ListOfExpandedUserTypes = List[ExpandedUserType]
OptionalListOfExpandedUserTypes = Optional[List[ExpandedUserType]]
