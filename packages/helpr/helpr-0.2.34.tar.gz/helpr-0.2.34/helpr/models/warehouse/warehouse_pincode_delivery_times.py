from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
import uuid
from ..base import Base

class WarehousePincodeDeliveryTimes(Base):
    __tablename__ = "warehouse_pincode_delivery_times"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    pincode = Column(String(6), nullable=False)
    delivery_hours = Column(Integer, nullable=False)  # 46 for AKAB-GGN→560095, 17 for AKAB-BLR→560095
    estimated_tat_days = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("NOW()"))

    __table_args__ = (
        UniqueConstraint('warehouse_id', 'pincode', name='uq_warehouse_pincode_delivery_times'),
        Index('idx_warehouse_pincode_delivery_times_warehouse', 'warehouse_id'),
        Index('idx_warehouse_pincode_delivery_times_pincode', 'pincode'),
        Index('idx_warehouse_pincode_delivery_times_warehouse_pincode', 'warehouse_id', 'pincode'),
    )
