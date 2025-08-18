import uuid
from sqlalchemy import Column, Integer, Text, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from ..base import Base
from enum import Enum

class InventoryLogStatus(Enum):
    ERP_UPDATE = "ERP_UPDATE"

class InventoryLog(Base):
    __tablename__ = 'inventory_log'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(Text, nullable=False)
    warehouse_id = Column(Text, nullable=False)
    quantity = Column(Integer, nullable=False)
    event = Column(SAEnum(InventoryLogStatus), default=InventoryLogStatus.ERP_UPDATE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    
    def __repr__(self):
        return f"<InventoryLog(id={self.id}, sku={self.sku}, warehouse_id={self.warehouse_id}, quantity={self.quantity}, event={self.event.value})"