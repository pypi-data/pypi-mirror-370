import uuid
from sqlalchemy import Column, Integer, Text, DateTime, Enum as SAEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from ..base import Base
from enum import Enum

class BulkOperationType(Enum):
    PINCODE_API_SYNC = "PINCODE_API_SYNC"
    PINCODE_RANGE_IMPORT = "PINCODE_RANGE_IMPORT" 
    DELIVERY_SLA_UPLOAD = "DELIVERY_SLA_UPLOAD"
    MANUAL_CSV_UPLOAD = "MANUAL_CSV_UPLOAD"
    SINGLE_PINCODE_LOOKUP = "SINGLE_PINCODE_LOOKUP"

class BulkOperationStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"

class BulkUploadLog(Base):
    __tablename__ = 'bulk_upload_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    operation_type = Column(SAEnum(BulkOperationType), nullable=False)
    status = Column(SAEnum(BulkOperationStatus), default=BulkOperationStatus.PENDING, nullable=False)
    
    # File/Source information
    filename = Column(Text, nullable=True)  # For file uploads
    source_info = Column(Text, nullable=True)  # API endpoint, pincode range, etc.
    
    # Processing statistics
    total_records = Column(Integer, default=0, nullable=False)
    success_count = Column(Integer, default=0, nullable=False)
    error_count = Column(Integer, default=0, nullable=False)
    
    # Error details (JSON format)
    errors = Column(JSON, nullable=True)
    
    # Processing metadata
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    processing_time_seconds = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<BulkUploadLog(id={self.id}, type={self.operation_type.value}, status={self.status.value}, success={self.success_count}, errors={self.error_count})>"