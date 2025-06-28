from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

from app.models.user import ServiceBranch, ServiceStatus, DeploymentStatus


class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    service_branch: Optional[ServiceBranch] = None
    service_status: Optional[ServiceStatus] = None
    rank: Optional[str] = None
    unit: Optional[str] = None
    base_location: Optional[str] = None
    deployment_status: Optional[DeploymentStatus] = None
    years_of_service: Optional[int] = None
    mos_code: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    service_branch: Optional[ServiceBranch] = None
    service_status: Optional[ServiceStatus] = None
    rank: Optional[str] = None
    unit: Optional[str] = None
    base_location: Optional[str] = None
    deployment_status: Optional[DeploymentStatus] = None
    years_of_service: Optional[int] = None
    mos_code: Optional[str] = None
    profile_picture: Optional[str] = None


class UserPrivacyUpdate(BaseModel):
    show_unit: Optional[bool] = None
    show_location: Optional[bool] = None
    show_deployment_status: Optional[bool] = None


class UserInDBBase(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    profile_picture: Optional[str] = None
    verification_date: Optional[datetime] = None
    show_unit: bool
    show_location: bool
    show_deployment_status: bool

    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str


class UserPublic(BaseModel):
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_picture: Optional[str] = None
    service_branch: Optional[ServiceBranch] = None
    service_status: Optional[ServiceStatus] = None
    rank: Optional[str] = None
    unit: Optional[str] = None
    base_location: Optional[str] = None
    deployment_status: Optional[DeploymentStatus] = None
    is_verified: bool

    class Config:
        from_attributes = True


class MilitaryVerification(BaseModel):
    document_type: str  # DD214, CAC, etc.
    document_data: str  # Base64 encoded document or verification code
    additional_info: Optional[dict] = None