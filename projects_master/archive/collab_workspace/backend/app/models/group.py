from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class GroupType(str, enum.Enum):
    UNIT = "unit"
    BASE = "base"
    SUPPORT = "support"
    HOBBY = "hobby"
    DEPLOYMENT = "deployment"
    VETERAN = "veteran"
    FAMILY = "family"
    PROFESSIONAL = "professional"


class GroupPrivacy(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    SECRET = "secret"


class MemberRole(str, enum.Enum):
    MEMBER = "member"
    MODERATOR = "moderator"
    ADMIN = "admin"


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    group_type = Column(Enum(GroupType), nullable=False)
    privacy = Column(Enum(GroupPrivacy), default=GroupPrivacy.PUBLIC)
    
    # Group Details
    cover_image = Column(String)
    icon = Column(String)
    rules = Column(Text)  # JSON array of group rules
    
    # Location/Unit specific
    base_location = Column(String)
    unit_affiliation = Column(String)
    
    # Settings
    requires_approval = Column(Boolean, default=False)
    allow_member_posts = Column(Boolean, default=True)
    
    # Metadata
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Member counts (denormalized for performance)
    member_count = Column(Integer, default=0)
    post_count = Column(Integer, default=0)
    
    # Relationships
    creator = relationship("User", back_populates="created_groups")
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    posts = relationship("GroupPost", back_populates="group", cascade="all, delete-orphan")


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    role = Column(Enum(MemberRole), default=MemberRole.MEMBER)
    joined_at = Column(DateTime, server_default=func.now())
    
    # Notification preferences
    notify_posts = Column(Boolean, default=True)
    notify_announcements = Column(Boolean, default=True)
    
    # Relationships
    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="group_memberships")


class GroupPost(Base):
    __tablename__ = "group_posts"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    
    # Pinning functionality
    is_pinned = Column(Boolean, default=False)
    is_announcement = Column(Boolean, default=False)
    pinned_at = Column(DateTime)
    pinned_by = Column(Integer, ForeignKey("users.id"))
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    group = relationship("Group", back_populates="posts")
    post = relationship("Post")
    pinner = relationship("User", foreign_keys=[pinned_by])