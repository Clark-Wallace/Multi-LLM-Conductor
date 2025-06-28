from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class SupportCategory(str, enum.Enum):
    MENTAL_HEALTH = "mental_health"
    FINANCIAL = "financial"
    CAREER = "career"
    FAMILY = "family"
    MEDICAL = "medical"
    LEGAL = "legal"
    HOUSING = "housing"
    EDUCATION = "education"
    TRANSITION = "transition"  # Military to civilian transition
    OTHER = "other"


class SupportRequestStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ResourceType(str, enum.Enum):
    ARTICLE = "article"
    VIDEO = "video"
    DOCUMENT = "document"
    CONTACT = "contact"
    WEBSITE = "website"
    HOTLINE = "hotline"
    SERVICE = "service"


class SupportRequest(Base):
    __tablename__ = "support_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Request details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(SupportCategory), nullable=False)
    urgency = Column(String)  # low, medium, high, critical
    
    # Status
    status = Column(Enum(SupportRequestStatus), default=SupportRequestStatus.OPEN)
    is_anonymous = Column(Boolean, default=False)
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.id"))
    assigned_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    resolved_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="support_requests")
    assignee = relationship("User", foreign_keys=[assigned_to])
    responses = relationship("SupportResponse", back_populates="request", cascade="all, delete-orphan")


class SupportResponse(Base):
    __tablename__ = "support_responses"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("support_requests.id"), nullable=False)
    responder_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    content = Column(Text, nullable=False)
    is_official = Column(Boolean, default=False)  # From verified support personnel
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    request = relationship("SupportRequest", back_populates="responses")
    responder = relationship("User")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    
    # Resource info
    title = Column(String, nullable=False)
    description = Column(Text)
    resource_type = Column(Enum(ResourceType), nullable=False)
    category = Column(Enum(SupportCategory), nullable=False)
    
    # Content
    url = Column(String)
    phone_number = Column(String)
    email = Column(String)
    content = Column(Text)  # For articles or embedded content
    
    # Metadata
    author_id = Column(Integer, ForeignKey("users.id"))
    is_official = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Location specific
    available_locations = Column(Text)  # JSON array of locations
    service_branches = Column(Text)  # JSON array of applicable branches
    
    # Engagement
    views_count = Column(Integer, default=0)
    saves_count = Column(Integer, default=0)
    rating = Column(Integer)  # Average rating 1-5
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    author = relationship("User", back_populates="resources")
    saves = relationship("ResourceSave", cascade="all, delete-orphan")


class ResourceSave(Base):
    __tablename__ = "resource_saves"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    saved_at = Column(DateTime, server_default=func.now())
    notes = Column(Text)  # Personal notes about the resource
    
    # Relationships
    resource = relationship("Resource", back_populates="saves")
    user = relationship("User")