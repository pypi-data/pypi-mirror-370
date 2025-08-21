from sqlalchemy import Column, Integer, String
from maleo.soma.models.table import DataTable
from maleo.metadata.db import MaleoMetadataBase


class UserTypesMixin:
    order = Column(name="order", type_=Integer)
    key = Column(name="key", type_=String(20), unique=True, nullable=False)
    name = Column(name="name", type_=String(20), unique=True, nullable=False)


class UserTypesTable(UserTypesMixin, DataTable, MaleoMetadataBase):
    __tablename__ = "user_types"
