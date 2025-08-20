from typing import List, Optional
from maleo.metadata.enums.medical_role import MedicalRole
from maleo.metadata.schemas.data.medical_role import MedicalRoleDataSchema


# Simple medical role
SimpleMedicalRole = MedicalRole
OptionalSimpleMedicalRole = Optional[SimpleMedicalRole]
ListOfSimpleMedicalRoles = List[SimpleMedicalRole]
OptionalListOfSimpleMedicalRoles = Optional[List[SimpleMedicalRole]]

# Expanded medical role
ExpandedMedicalRole = MedicalRoleDataSchema
OptionalExpandedMedicalRole = Optional[ExpandedMedicalRole]
ListOfExpandedMedicalRoles = List[ExpandedMedicalRole]
OptionalListOfExpandedMedicalRoles = Optional[List[ExpandedMedicalRole]]
