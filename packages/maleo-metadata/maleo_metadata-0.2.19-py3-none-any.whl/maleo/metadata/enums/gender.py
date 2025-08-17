from enum import StrEnum


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"
    KEY = "key"
    NAME = "name"


class Gender(StrEnum):
    UNDISCLOSED = "undisclosed"
    FEMALE = "female"
    MALE = "male"
