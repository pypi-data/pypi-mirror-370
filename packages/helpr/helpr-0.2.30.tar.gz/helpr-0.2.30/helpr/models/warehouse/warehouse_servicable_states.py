from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..base import Base
from .enums import DeliveryModeEnum
from .enums import StateCodeEnum 

class WarehouseServiceableState(Base):
    __tablename__ = "warehouse_serviceable_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    state_code = Column(SQLEnum(StateCodeEnum, name="state_code_enum"), nullable=False)
    delivery_mode = Column(SQLEnum(DeliveryModeEnum, name="delivery_mode_enum"), nullable=False)
    is_full_state_serviceable = Column(Boolean, default=False, nullable=False)