from sqlalchemy import Column, Integer, String
from maleo.soma.models.table import DataTable
from maleo.metadata.db import MaleoMetadataBase


class SystemRolesMixin:
    order = Column(name="order", type_=Integer)
    key = Column(name="key", type_=String(20), unique=True, nullable=False)
    name = Column(name="name", type_=String(20), unique=True, nullable=False)


class SystemRolesTable(SystemRolesMixin, DataTable, MaleoMetadataBase):
    __tablename__ = "system_roles"
