from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.config import Base  # Base is assumed to be the declarative base class for SQLAlchemy models.


class UserUploaded(Base):
    __tablename__ = "user_uploads"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="uploaded_files")
