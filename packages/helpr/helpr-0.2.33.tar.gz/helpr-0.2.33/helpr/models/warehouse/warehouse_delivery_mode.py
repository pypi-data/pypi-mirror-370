from sqlalchemy import Column, Boolean, Integer, Time, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..base import Base
from .enums import DeliveryModeEnum

class WarehouseDeliveryMode(Base):
    __tablename__ = "warehouse_delivery_modes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    delivery_mode = Column(SQLEnum(DeliveryModeEnum, name="delivery_mode_enum"), nullable=False)
    cutoff_time = Column(Time, nullable=True)
    estimated_tat_days = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)