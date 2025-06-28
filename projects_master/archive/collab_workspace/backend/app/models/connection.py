from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum, Boolean, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ConnectionStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    BLOCKED = "blocked"
    DECLINED = "declined"


class Connection(Base):
    __tablename__ = "connections"
    __table_args__ = (
        UniqueConstraint('user_id', 'connected_user_id', name='unique_connection'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    connected_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.PENDING)
    connection_message = Column(Text)  # Optional message when sending connection request
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Track who initiated the connection
    initiated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="connections")
    connected_user = relationship("User", foreign_keys=[connected_user_id], back_populates="connected_users")
    initiator = relationship("User", foreign_keys=[initiated_by])