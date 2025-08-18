from sqlalchemy import Column, Integer, Text, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..base import Base
from .enums import DeliveryModeEnum

class WarehouseDeliveryModePincode(Base):
    __tablename__ = "warehouse_delivery_mode_pincodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    delivery_mode = Column(SQLEnum(DeliveryModeEnum, name="delivery_mode_enum"), nullable=False)
    pincode = Column(Text, nullable=False)
    estimated_tat_days = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)