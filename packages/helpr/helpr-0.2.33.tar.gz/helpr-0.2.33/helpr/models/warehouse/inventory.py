import uuid
from sqlalchemy import Column, String, Text, DateTime, Enum as SAEnum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..base import Base


class ProductInventory(Base):
    __tablename__ = "product_inventory"
    __table_args__ = (
        UniqueConstraint('sku', 'warehouse_id', name='_warehouse_sku_uc'),
    )
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String, nullable=False)
    warehouse_id = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    
    def __repr__(self):
        return f"<ProductInventory(id={self.id}, warehouse_id={self.warehouse_id}), sku={self.sku}, quantity={self.quantity}>"