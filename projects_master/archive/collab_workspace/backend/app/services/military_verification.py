from typing import Dict, Optional, Tuple
from datetime import datetime
from enum import Enum
import re
import hashlib
from fastapi import UploadFile, HTTPException
import PyPDF2
import io

class VerificationMethod(str, Enum):
    CAC_CARD = "cac_card"
    DD214 = "dd214"
    MILITARY_EMAIL = "military_email"
    MANUAL_REVIEW = "manual_review"
    DEERS_DATABASE = "deers_database"

class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"

class MilitaryVerificationService:
    """
    Service for verifying military service members, veterans, and dependents
    In production, this would integrate with:
    - DEERS (Defense Enrollment Eligibility Reporting System)
    - VA systems for veteran verification
    - CAC card readers
    - DoD email verification
    """
    
    def __init__(self):
        # Military email domains
        self.military_domains = [
            ".mil",
            "@army.mil",
            "@navy.mil",
            "@af.mil",
            "@usmc.mil",
            "@uscg.mil",
            "@ussf.mil",
            "@mail.mil",
            "@socom.mil",
            # Add more specific domains as needed
        ]
        
        # DD-214 common fields for validation
        self.dd214_fields = [
            "character of service",
            "type of separation",
            "reentry code",
            "separation code",
            "member-4 copy",
            "honorable",
            "general under honorable",
        ]
    
    async def verify_military_email(self, email: str) -> Tuple[bool, str]:
        """
        Verify military email address
        Returns: (is_valid, message)
        """
        email_lower = email.lower()
        
        # Check if email ends with military domain
        is_military = any(
            email_lower.endswith(domain) or f"@{domain}" in email_lower 
            for domain in self.military_domains
        )
        
        if is_military:
            # In production, would send verification email
            return True, "Military email detected. Verification email sent."
        
        return False, "Not a valid military email address"
    
    async def verify_dd214(self, file: UploadFile) -> Tuple[VerificationStatus, Dict[str, str]]:
        """
        Verify DD-214 discharge document
        Returns: (status, extracted_info)
        """
        try:
            # Read PDF content
            content = await file.read()
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            
            # Extract text from all pages
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text().lower()
            
            # Check for DD-214 indicators
            is_dd214 = "dd form 214" in text or "certificate of release" in text
            if not is_dd214:
                return VerificationStatus.REJECTED, {"error": "Document does not appear to be a DD-214"}
            
            # Extract key information
            extracted_info = {}
            
            # Service branch
            branches = ["army", "navy", "air force", "marine corps", "coast guard", "space force"]
            for branch in branches:
                if branch in text:
                    extracted_info["branch"] = branch.upper()
                    break
            
            # Character of service
            if "honorable" in text:
                extracted_info["character_of_service"] = "HONORABLE"
            elif "general under honorable" in text:
                extracted_info["character_of_service"] = "GENERAL_UNDER_HONORABLE"
            elif "other than honorable" in text:
                extracted_info["character_of_service"] = "OTHER_THAN_HONORABLE"
            
            # Check for required fields
            valid_fields_found = sum(1 for field in self.dd214_fields if field in text)
            
            if valid_fields_found >= 3:
                # Generate verification hash
                extracted_info["verification_hash"] = hashlib.sha256(content).hexdigest()
                extracted_info["verified_at"] = datetime.utcnow().isoformat()
                
                # Check character of service for eligibility
                if extracted_info.get("character_of_service") in ["HONORABLE", "GENERAL_UNDER_HONORABLE"]:
                    return VerificationStatus.VERIFIED, extracted_info
                else:
                    return VerificationStatus.MANUAL_REVIEW_REQUIRED, extracted_info
            
            return VerificationStatus.MANUAL_REVIEW_REQUIRED, extracted_info
            
        except Exception as e:
            return VerificationStatus.REJECTED, {"error": f"Unable to process document: {str(e)}"}
    
    async def verify_cac_card(self, certificate_data: bytes) -> Tuple[VerificationStatus, Dict[str, str]]:
        """
        Verify CAC (Common Access Card) certificate
        In production, this would validate the PKI certificate chain
        """
        try:
            # In production:
            # 1. Parse X.509 certificate
            # 2. Validate against DoD root certificates
            # 3. Check certificate revocation list (CRL)
            # 4. Extract user information from certificate
            
            # Placeholder implementation
            extracted_info = {
                "method": "CAC_CARD",
                "verified_at": datetime.utcnow().isoformat(),
                "placeholder": "CAC verification requires PKI infrastructure"
            }
            
            return VerificationStatus.MANUAL_REVIEW_REQUIRED, extracted_info
            
        except Exception as e:
            return VerificationStatus.REJECTED, {"error": f"Invalid certificate: {str(e)}"}
    
    async def check_deers_database(self, ssn_last_four: str, last_name: str) -> Tuple[bool, str]:
        """
        Check DEERS database (placeholder)
        In production, this would connect to the actual DEERS system
        """
        # Validate input
        if not re.match(r'^\d{4}$', ssn_last_four):
            return False, "Invalid SSN format"
        
        if not last_name or len(last_name) < 2:
            return False, "Invalid last name"
        
        # In production, would make secure API call to DEERS
        # For now, return manual review required
        return False, "DEERS verification requires manual review"
    
    async def verify_dependent(
        self, 
        sponsor_id: str, 
        relationship: str,
        verification_docs: Optional[UploadFile] = None
    ) -> Tuple[VerificationStatus, Dict[str, str]]:
        """
        Verify military dependents
        """
        valid_relationships = ["spouse", "child", "parent", "sibling"]
        
        if relationship.lower() not in valid_relationships:
            return VerificationStatus.REJECTED, {"error": "Invalid relationship type"}
        
        # In production, would verify:
        # 1. Sponsor's military status
        # 2. Dependent ID card
        # 3. Marriage certificate / birth certificate
        # 4. DEERS enrollment
        
        return VerificationStatus.MANUAL_REVIEW_REQUIRED, {
            "sponsor_id": sponsor_id,
            "relationship": relationship,
            "requires_manual_review": True
        }
    
    def generate_verification_token(self, user_id: int, method: VerificationMethod) -> str:
        """
        Generate secure verification token
        """
        data = f"{user_id}:{method}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    async def validate_service_details(
        self,
        branch: str,
        rank: str,
        mos_code: str
    ) -> Tuple[bool, str]:
        """
        Validate service details format
        """
        # Validate branch
        valid_branches = ["ARMY", "NAVY", "AIR_FORCE", "MARINES", "COAST_GUARD", "SPACE_FORCE"]
        if branch not in valid_branches:
            return False, "Invalid service branch"
        
        # Validate rank format (simplified)
        if not rank or len(rank) < 2:
            return False, "Invalid rank"
        
        # Validate MOS/Rating/AFSC code format
        # Army MOS: 2-3 digits + letter (e.g., "11B", "68W")
        # Navy Rating: 2-4 letters (e.g., "IT", "HM")
        # Air Force AFSC: digit + letter + digit + letter + digit (e.g., "3D0X2")
        # Marines MOS: 4 digits (e.g., "0311")
        
        mos_patterns = {
            "ARMY": r'^\d{2,3}[A-Z]$',
            "NAVY": r'^[A-Z]{2,4}$',
            "AIR_FORCE": r'^\d[A-Z]\d[A-Z]\d$',
            "MARINES": r'^\d{4}$',
            "COAST_GUARD": r'^[A-Z]{2,4}$',
            "SPACE_FORCE": r'^\d[A-Z]\d[A-Z]\d$'
        }
        
        pattern = mos_patterns.get(branch)
        if pattern and not re.match(pattern, mos_code):
            return False, f"Invalid MOS/Rating/AFSC format for {branch}"
        
        return True, "Service details validated"

# Global military verification service instance
military_verification_service = MilitaryVerificationService()