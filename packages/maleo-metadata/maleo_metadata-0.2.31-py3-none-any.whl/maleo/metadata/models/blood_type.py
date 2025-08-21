from sqlalchemy import Column, Integer, String
from maleo.soma.models.table import DataTable
from maleo.metadata.db import MaleoMetadataBase


class BloodTypesMixin:
    order = Column(name="order", type_=Integer)
    key = Column(name="key", type_=String(2), unique=True, nullable=False)
    name = Column(name="name", type_=String(2), unique=True, nullable=False)


class BloodTypesTable(BloodTypesMixin, DataTable, MaleoMetadataBase):
    __tablename__ = "blood_types"
