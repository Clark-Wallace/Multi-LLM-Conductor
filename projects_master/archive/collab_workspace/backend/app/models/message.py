from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    VOICE = "voice"


class MessageStatus(str, enum.Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Content
    content = Column(Text)
    message_type = Column(Enum(MessageType), default=MessageType.TEXT)
    media_url = Column(String)  # For images/files/voice
    
    # Status
    status = Column(Enum(MessageStatus), default=MessageStatus.SENT)
    read_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    edited = Column(Boolean, default=False)
    edited_at = Column(DateTime)
    
    # Encryption (for future implementation)
    is_encrypted = Column(Boolean, default=False)
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_messages")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Last message info (denormalized for performance)
    last_message_id = Column(Integer, ForeignKey("messages.id"))
    last_message_at = Column(DateTime)
    
    # Unread counts
    user1_unread_count = Column(Integer, default=0)
    user2_unread_count = Column(Integer, default=0)
    
    # Archive/Mute status
    user1_archived = Column(Boolean, default=False)
    user2_archived = Column(Boolean, default=False)
    user1_muted = Column(Boolean, default=False)
    user2_muted = Column(Boolean, default=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    user1 = relationship("User", foreign_keys=[user1_id])
    user2 = relationship("User", foreign_keys=[user2_id])
    last_message = relationship("Message", foreign_keys=[last_message_id])