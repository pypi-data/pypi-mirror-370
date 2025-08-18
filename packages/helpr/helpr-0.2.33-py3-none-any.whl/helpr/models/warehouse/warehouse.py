from sqlalchemy import Column, Text, DateTime, Enum as SAEnum, Boolean, Integer
from sqlalchemy.sql import func

from ..base import Base
from .enums import WarehouseStatus


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    medusa_location_id = Column(Text, unique=True)
    erp_warehouse_id = Column(Text, unique=True)
    name = Column(Text)
    city = Column(Text)
    is_mother_warehouse = Column(Boolean, default=False)
    status = Column(SAEnum(WarehouseStatus), default=WarehouseStatus.inactive)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    
    def __repr__(self):
        return f"<Warehouse(id={self.id}, name={self.name}, city={self.city}, status={self.status.value}>"