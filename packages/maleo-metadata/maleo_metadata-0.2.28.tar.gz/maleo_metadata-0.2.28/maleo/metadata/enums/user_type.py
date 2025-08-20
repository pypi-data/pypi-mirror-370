from enum import StrEnum


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"
    KEY = "key"
    NAME = "name"


class UserType(StrEnum):
    REGULAR = "regular"
    PROXY = "proxy"
    SERVICE = "service"
