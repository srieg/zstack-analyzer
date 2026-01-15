from sqlalchemy import Column, String, DateTime, Integer, JSON, LargeBinary, Boolean, Float
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from api.models.base import Base

def generate_uuid():
    return str(uuid.uuid4())

class ImageStack(Base):
    __tablename__ = "image_stacks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # Image properties
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    depth = Column(Integer, nullable=False)
    channels = Column(Integer, nullable=False)
    bit_depth = Column(Integer, nullable=False)
    
    # Physical properties
    pixel_size_x = Column(Float, nullable=True)
    pixel_size_y = Column(Float, nullable=True)
    pixel_size_z = Column(Float, nullable=True)
    
    # Acquisition metadata
    acquisition_date = Column(DateTime, nullable=True)
    microscope_id = Column(String, nullable=True)
    objective_info = Column(JSON, nullable=True)
    channel_config = Column(JSON, nullable=True)
    
    # Processing status
    processing_status = Column(String, default="uploaded")  # uploaded, processing, completed, failed
    upload_date = Column(DateTime, default=func.now())
    
    # Full metadata as JSON
    image_metadata = Column(JSON, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "filename": self.filename,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "width": self.width,
            "height": self.height,
            "depth": self.depth,
            "channels": self.channels,
            "bit_depth": self.bit_depth,
            "pixel_size_x": self.pixel_size_x,
            "pixel_size_y": self.pixel_size_y,
            "pixel_size_z": self.pixel_size_z,
            "acquisition_date": self.acquisition_date.isoformat() if self.acquisition_date else None,
            "microscope_id": self.microscope_id,
            "objective_info": self.objective_info,
            "channel_config": self.channel_config,
            "processing_status": self.processing_status,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "metadata": self.image_metadata,
        }