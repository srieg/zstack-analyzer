from sqlalchemy import Column, String, DateTime, Integer, JSON, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from api.models.base import Base

def generate_uuid():
    return str(uuid.uuid4())

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    stack_id = Column(String(36), ForeignKey("image_stacks.id"), nullable=False)
    
    # Analysis metadata
    algorithm_name = Column(String, nullable=False)
    algorithm_version = Column(String, nullable=False)
    gpu_device = Column(String, nullable=True)
    processing_time_ms = Column(Integer, nullable=False)
    
    # Results
    results = Column(JSON, nullable=False)
    confidence_score = Column(Float, nullable=True)
    
    # Human validation
    human_validated = Column(Boolean, default=False)
    validation_timestamp = Column(DateTime, nullable=True)
    validator_id = Column(String, nullable=True)
    validation_notes = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship
    image_stack = relationship("ImageStack", backref="analysis_results")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "stack_id": str(self.stack_id),
            "algorithm_name": self.algorithm_name,
            "algorithm_version": self.algorithm_version,
            "gpu_device": self.gpu_device,
            "processing_time_ms": self.processing_time_ms,
            "results": self.results,
            "confidence_score": self.confidence_score,
            "human_validated": self.human_validated,
            "validation_timestamp": self.validation_timestamp.isoformat() if self.validation_timestamp else None,
            "validator_id": self.validator_id,
            "validation_notes": self.validation_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }