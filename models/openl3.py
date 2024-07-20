from pydantic import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.config import Base


class OpenL3ComputationLog(Base):
    __tablename__ = "openl3_computation_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    datetime = Column(DateTime(timezone=True), server_default=func.now())
    file_path = Column(String, nullable=False)
    model_version = Column(String)
    response_time_ms = Column(Float, nullable=False)
    error_message = Column(Text, nullable=True)

    user = relationship("User")


class SongList(BaseModel):
    songs: list


class EmbeddingResponse(BaseModel):
    file_name: str
    embedding: list
