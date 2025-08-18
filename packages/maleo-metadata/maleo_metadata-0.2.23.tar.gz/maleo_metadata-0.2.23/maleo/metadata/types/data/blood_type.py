from typing import List, Optional
from maleo.metadata.enums.blood_type import BloodType
from maleo.metadata.schemas.data.blood_type import BloodTypeDataSchema


# Simple blood type
SimpleBloodType = BloodType
OptionalSimpleBloodType = Optional[SimpleBloodType]
ListOfSimpleBloodTypes = List[SimpleBloodType]
OptionalListOfSimpleBloodTypes = Optional[List[SimpleBloodType]]

# Expanded blood type
ExpandedBloodType = BloodTypeDataSchema
OptionalExpandedBloodType = Optional[ExpandedBloodType]
ListOfExpandedBloodTypes = List[ExpandedBloodType]
OptionalListOfExpandedBloodTypes = Optional[List[ExpandedBloodType]]
