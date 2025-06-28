from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict
import asyncio
from fastapi import HTTPException, Request
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

class RateLimiter:
    """
    Rate limiter for API endpoints with military-specific considerations
    """
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.failed_logins: Dict[str, int] = defaultdict(int)
        self.locked_accounts: Dict[str, datetime] = {}
        
    async def check_rate_limit(
        self, 
        request: Request, 
        calls: int = 10, 
        period: int = 60
    ) -> None:
        """Check if request exceeds rate limit"""
        client_ip = request.client.host
        now = datetime.now()
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > now - timedelta(seconds=period)
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= calls:
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Please try again in {period} seconds."
            )
        
        # Record request
        self.requests[client_ip].append(now)
    
    async def check_login_attempts(self, identifier: str) -> None:
        """Check if account is locked due to failed login attempts"""
        now = datetime.now()
        
        # Check if account is locked
        if identifier in self.locked_accounts:
            lockout_end = self.locked_accounts[identifier]
            if now < lockout_end:
                remaining = int((lockout_end - now).total_seconds() / 60)
                raise HTTPException(
                    status_code=HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Account locked due to multiple failed login attempts. Try again in {remaining} minutes."
                )
            else:
                # Unlock account
                del self.locked_accounts[identifier]
                self.failed_logins[identifier] = 0
    
    async def record_failed_login(self, identifier: str, max_attempts: int = 5, lockout_minutes: int = 30) -> None:
        """Record failed login attempt and lock account if necessary"""
        self.failed_logins[identifier] += 1
        
        if self.failed_logins[identifier] >= max_attempts:
            self.locked_accounts[identifier] = datetime.now() + timedelta(minutes=lockout_minutes)
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Account locked due to {max_attempts} failed login attempts. Try again in {lockout_minutes} minutes."
            )
    
    async def clear_failed_attempts(self, identifier: str) -> None:
        """Clear failed login attempts on successful login"""
        self.failed_logins[identifier] = 0
        if identifier in self.locked_accounts:
            del self.locked_accounts[identifier]

# Global rate limiter instance
rate_limiter = RateLimiter()