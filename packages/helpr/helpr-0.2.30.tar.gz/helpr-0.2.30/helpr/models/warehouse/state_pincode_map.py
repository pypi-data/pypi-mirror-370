from sqlalchemy import Column, Text, String, UniqueConstraint, Enum as SQLEnum, Float, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..base import Base
from .enums import StateCodeEnum

class StatePincodeMap(Base):
    __tablename__ = "state_pincode_map"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pincode = Column(Text, unique=True, nullable=False, index=True)
    city = Column(Text, nullable=False, index=True)
    state_code = Column(SQLEnum(StateCodeEnum, name="state_code_enum"), nullable=False, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    __table_args__ = (
        UniqueConstraint('pincode', name='uq_state_pincode_map_pincode'),
        Index('idx_state_pincode_map_pincode_state', 'pincode', 'state_code'),
        Index('idx_state_pincode_map_pincode_city', 'pincode', 'city'),
        Index('idx_state_pincode_map_state_city', 'state_code', 'city'),
    )