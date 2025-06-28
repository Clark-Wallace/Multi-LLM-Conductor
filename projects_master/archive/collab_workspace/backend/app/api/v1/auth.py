from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash, verify_password

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(models.User).filter(
        (models.User.email == form_data.username) | 
        (models.User.username == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/register", response_model=schemas.User)
def register(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Create new user account
    """
    # Check if user exists
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists",
        )
    
    user = db.query(models.User).filter(models.User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this username already exists",
        )
    
    # Create user
    user = models.User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        bio=user_in.bio,
        service_branch=user_in.service_branch,
        service_status=user_in.service_status,
        rank=user_in.rank,
        unit=user_in.unit,
        base_location=user_in.base_location,
        deployment_status=user_in.deployment_status,
        years_of_service=user_in.years_of_service,
        mos_code=user_in.mos_code,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/verify-military", response_model=schemas.User)
async def verify_military_status(
    *,
    db: Session = Depends(deps.get_db),
    verification_data: schemas.MilitaryVerification,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Verify military status of the current user
    
    This is a placeholder endpoint. In production, this would integrate with
    actual military verification services or document verification systems.
    """
    # TODO: Implement actual military verification logic
    # This could involve:
    # - Verifying DD214 documents
    # - CAC card verification
    # - Integration with DoD systems
    # - Manual review process
    
    # For now, we'll simulate verification
    if verification_data.document_type in ["DD214", "CAC", "MILITARY_ID"]:
        current_user.is_verified = True
        current_user.verification_date = datetime.utcnow()
        current_user.verification_document = verification_data.document_type
        db.commit()
        db.refresh(current_user)
        return current_user
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid verification document type"
        )