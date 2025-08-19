from sqlalchemy import Column, Integer, UUID, String, Enum
from uuid import uuid4
from maleo.soma.enums.service import ServiceType, Category
from maleo.soma.models.table import DataTable
from maleo.metadata.db import MaleoMetadataBase


class ServicesMixin:
    order = Column(name="order", type_=Integer)
    type = Column(
        name="type",
        type_=Enum(ServiceType, name="service_type"),
        nullable=False,
    )
    category = Column(
        name="category",
        type_=Enum(Category, name="service_category"),
        nullable=False,
    )
    key = Column(name="key", type_=String(20), unique=True, nullable=False)
    name = Column(name="name", type_=String(20), unique=True, nullable=False)
    secret = Column(
        name="secret", type_=UUID, default=uuid4, unique=True, nullable=False
    )


class ServicesTable(ServicesMixin, DataTable, MaleoMetadataBase):
    __tablename__ = "services"
