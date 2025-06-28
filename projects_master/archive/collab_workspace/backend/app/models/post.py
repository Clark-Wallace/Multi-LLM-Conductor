from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class PostType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    LINK = "link"
    POLL = "poll"


class PostPrivacy(str, enum.Enum):
    PUBLIC = "public"
    CONNECTIONS_ONLY = "connections"
    UNIT_ONLY = "unit"
    PRIVATE = "private"


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Content
    content = Column(Text, nullable=False)
    post_type = Column(Enum(PostType), default=PostType.TEXT)
    media_url = Column(String)  # For images/videos
    link_url = Column(String)  # For shared links
    link_preview = Column(Text)  # JSON data for link preview
    
    # Privacy and Visibility
    privacy = Column(Enum(PostPrivacy), default=PostPrivacy.PUBLIC)
    is_anonymous = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    edited = Column(Boolean, default=False)
    
    # Engagement Metrics
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    
    # Location (optional)
    location = Column(String)
    
    # Tags
    hashtags = Column(Text)  # JSON array of hashtags
    mentioned_users = Column(Text)  # JSON array of mentioned user IDs
    
    # Relationships
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    shares = relationship("PostShare", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"))
    
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    edited = Column(Boolean, default=False)
    
    # Relationships
    post = relationship("Post", back_populates="comments")
    author = relationship("User")
    replies = relationship("Comment", backref="parent", remote_side=[id])
    likes = relationship("CommentLike", cascade="all, delete-orphan")


class PostLike(Base):
    __tablename__ = "post_likes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    post = relationship("Post", back_populates="likes")
    user = relationship("User")


class CommentLike(Base):
    __tablename__ = "comment_likes"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    comment = relationship("Comment", back_populates="likes")
    user = relationship("User")


class PostShare(Base):
    __tablename__ = "post_shares"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text)  # Optional message when sharing
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    post = relationship("Post", back_populates="shares")
    user = relationship("User")