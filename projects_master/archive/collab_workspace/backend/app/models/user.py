from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class ServiceBranch(str, enum.Enum):
    ARMY = "army"
    NAVY = "navy"
    AIR_FORCE = "air_force"
    MARINES = "marines"
    COAST_GUARD = "coast_guard"
    SPACE_FORCE = "space_force"


class ServiceStatus(str, enum.Enum):
    ACTIVE = "active"
    RESERVE = "reserve"
    NATIONAL_GUARD = "national_guard"
    VETERAN = "veteran"
    RETIRED = "retired"


class DeploymentStatus(str, enum.Enum):
    DEPLOYED = "deployed"
    STATESIDE = "stateside"
    TRAINING = "training"
    LEAVE = "leave"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Profile Information
    first_name = Column(String)
    last_name = Column(String)
    profile_picture = Column(String)  # URL to profile picture
    bio = Column(Text)
    
    # Military Information
    service_branch = Column(Enum(ServiceBranch))
    service_status = Column(Enum(ServiceStatus))
    rank = Column(String)
    unit = Column(String)
    base_location = Column(String)
    deployment_status = Column(Enum(DeploymentStatus))
    years_of_service = Column(Integer)
    mos_code = Column(String)  # Military Occupational Specialty
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime)
    verification_document = Column(String)  # URL to verification document
    
    # Account Status
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_login = Column(DateTime)
    
    # Privacy Settings
    show_unit = Column(Boolean, default=True)
    show_location = Column(Boolean, default=True)
    show_deployment_status = Column(Boolean, default=False)
    
    # Relationships
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.recipient_id", back_populates="recipient")
    group_memberships = relationship("GroupMember", back_populates="user", cascade="all, delete-orphan")
    created_groups = relationship("Group", back_populates="creator")
    connections = relationship("Connection", foreign_keys="Connection.user_id", back_populates="user")
    connected_users = relationship("Connection", foreign_keys="Connection.connected_user_id", back_populates="connected_user")
    support_requests = relationship("SupportRequest", back_populates="user")
    resources = relationship("Resource", back_populates="author")