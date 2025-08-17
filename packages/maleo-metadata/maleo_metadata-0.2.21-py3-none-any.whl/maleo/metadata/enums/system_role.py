from enum import StrEnum


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"
    KEY = "key"
    NAME = "name"


class SystemRole(StrEnum):
    ADMINISTRATOR = "administrator"
    USER = "user"
