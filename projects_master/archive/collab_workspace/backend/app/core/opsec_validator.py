import re
from typing import List, Dict, Tuple
from enum import Enum
import exifread
from PIL import Image
import io

class OPSECViolationType(str, Enum):
    LOCATION = "location"
    UNIT_MOVEMENT = "unit_movement"
    DEPLOYMENT_INFO = "deployment_info"
    OPERATIONAL_DETAILS = "operational_details"
    PERSONNEL_COUNT = "personnel_count"
    EQUIPMENT_DETAILS = "equipment_details"
    SCHEDULE_INFO = "schedule_info"
    CLASSIFIED_TERM = "classified_term"

class OPSECValidator:
    """
    Validates content for Operational Security (OPSEC) violations
    Critical for protecting service members and operations
    """
    
    def __init__(self):
        # Patterns that may indicate OPSEC violations
        self.sensitive_patterns = {
            OPSECViolationType.LOCATION: [
                r'\b\d{1,2}°\s*\d{1,2}[\'′]\s*\d{1,2}[\"″]?\s*[NS]\s*\d{1,3}°\s*\d{1,2}[\'′]\s*\d{1,2}[\"″]?\s*[EW]\b',  # Coordinates
                r'\b(?:FOB|COP|firebase|outpost)\s+\w+\b',  # Forward bases
                r'\bgrid\s+(?:reference|ref)?\s*:?\s*\w+\d+\b',  # Military grid references
                r'\b\d{6,8}\b(?:\s*\d{6,8}\b)?',  # MGRS coordinates
            ],
            OPSECViolationType.UNIT_MOVEMENT: [
                r'\b(?:deploy|deployment|deploying|redeploying)\s+(?:to|from|on|in)\s+\w+',
                r'\b(?:moving|movement|convoy|patrol)\s+(?:to|from|through)\s+\w+',
                r'\bRIP/TOA\b',  # Relief in Place/Transfer of Authority
                r'\b(?:arriving|departing|leaving)\s+(?:on|at|in)\s+\d{1,2}',
            ],
            OPSECViolationType.DEPLOYMENT_INFO: [
                r'\b(?:deploy|deployment)\s+(?:date|time|schedule)',
                r'\breturn(?:ing)?\s+(?:date|home|from)\s+\w+',
                r'\b\d+\s*(?:month|week|day)s?\s+(?:left|remaining|until)',
            ],
            OPSECViolationType.OPERATIONAL_DETAILS: [
                r'\b(?:mission|operation|op)\s+\w+\s+(?:at|on|in)\s+\d{2,4}',
                r'\b(?:patrol|convoy)\s+(?:route|schedule|timing)',
                r'\bROE\b',  # Rules of Engagement
                r'\b(?:attack|assault|raid)\s+(?:planned|scheduled)',
            ],
            OPSECViolationType.PERSONNEL_COUNT: [
                r'\b\d+\s*(?:soldier|marine|airman|sailor|guardian)s?\b',
                r'\b(?:company|platoon|squad)\s+(?:strength|size)',
                r'\b\d+\s*(?:KIA|WIA|MIA)\b',  # Casualty numbers
            ],
            OPSECViolationType.EQUIPMENT_DETAILS: [
                r'\b\d+\s*(?:MRAP|Humvee|Stryker|Bradley|Abrams|Apache|Blackhawk)s?\b',
                r'\b(?:weapon|equipment)\s+(?:malfunction|shortage|issue)',
                r'\b(?:armor|armament)\s+(?:upgrade|modification)',
            ],
            OPSECViolationType.SCHEDULE_INFO: [
                r'\b(?:guard|watch|duty)\s+(?:schedule|rotation|shift)',
                r'\b(?:PT|formation|inspection)\s+(?:at|time)',
                r'\b\d{2}:\d{2}\s*(?:hours|hrs|zulu)',
            ],
            OPSECViolationType.CLASSIFIED_TERM: [
                r'\b(?:SECRET|TOP SECRET|CLASSIFIED|FOUO|NOFORN)\b',
                r'\b(?:SCI|SAP|SIPR|JWICS)\b',
                r'\bTS/SCI\b',
            ]
        }
        
        # Terms that require warning but not blocking
        self.warning_terms = [
            r'\b(?:base|post|camp|fort)\s+\w+',
            r'\bunit\s+(?:name|designation)',
            r'\b(?:commander|CO|XO)\s+name',
        ]
    
    def validate_text(self, text: str) -> Tuple[bool, List[Dict[str, str]]]:
        """
        Validate text content for OPSEC violations
        Returns: (is_safe, list_of_violations)
        """
        violations = []
        text_lower = text.lower()
        
        for violation_type, patterns in self.sensitive_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    violations.append({
                        "type": violation_type,
                        "text": match.group(0),
                        "position": match.span(),
                        "severity": "high" if violation_type in [
                            OPSECViolationType.LOCATION,
                            OPSECViolationType.CLASSIFIED_TERM,
                            OPSECViolationType.OPERATIONAL_DETAILS
                        ] else "medium"
                    })
        
        # Check for warning terms
        warnings = []
        for pattern in self.warning_terms:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                warnings.append({
                    "type": "warning",
                    "text": match.group(0),
                    "position": match.span(),
                    "severity": "low"
                })
        
        is_safe = len(violations) == 0
        return is_safe, violations + warnings
    
    def scrub_metadata(self, image_data: bytes) -> bytes:
        """
        Remove EXIF data and GPS coordinates from images
        Critical for preventing location disclosure
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_data))
            
            # Remove EXIF data
            data = list(image.getdata())
            image_without_exif = Image.new(image.mode, image.size)
            image_without_exif.putdata(data)
            
            # Save to bytes
            output = io.BytesIO()
            image_without_exif.save(output, format=image.format or 'PNG')
            return output.getvalue()
        except Exception as e:
            # If unable to process, reject the image for safety
            raise ValueError(f"Unable to process image safely: {str(e)}")
    
    def check_deployment_blackout(self, user_deployment_status: str, user_unit: str) -> bool:
        """
        Check if content should be blocked due to deployment blackout
        """
        # In production, this would check against actual deployment blackout lists
        blackout_units = []  # Would be populated from secure database
        blackout_statuses = ["deployed", "combat_zone"]
        
        return (user_deployment_status in blackout_statuses or 
                user_unit in blackout_units)
    
    def generate_opsec_warning(self, violations: List[Dict[str, str]]) -> str:
        """
        Generate user-friendly OPSEC warning message
        """
        if not violations:
            return ""
        
        high_severity = [v for v in violations if v["severity"] == "high"]
        medium_severity = [v for v in violations if v["severity"] == "medium"]
        
        message = "⚠️ OPSEC WARNING: Your post may contain sensitive information:\n\n"
        
        if high_severity:
            message += "🚨 HIGH RISK:\n"
            for v in high_severity[:3]:  # Show max 3
                message += f"- {self._get_violation_message(v['type'])}\n"
        
        if medium_severity:
            message += "\n⚠️ MEDIUM RISK:\n"
            for v in medium_severity[:3]:
                message += f"- {self._get_violation_message(v['type'])}\n"
        
        message += "\nPlease review and remove sensitive information before posting."
        message += "\nRemember: OPSEC saves lives!"
        
        return message
    
    def _get_violation_message(self, violation_type: OPSECViolationType) -> str:
        """Get user-friendly message for violation type"""
        messages = {
            OPSECViolationType.LOCATION: "Location information detected",
            OPSECViolationType.UNIT_MOVEMENT: "Unit movement information detected",
            OPSECViolationType.DEPLOYMENT_INFO: "Deployment details detected",
            OPSECViolationType.OPERATIONAL_DETAILS: "Operational information detected",
            OPSECViolationType.PERSONNEL_COUNT: "Personnel numbers detected",
            OPSECViolationType.EQUIPMENT_DETAILS: "Equipment details detected",
            OPSECViolationType.SCHEDULE_INFO: "Schedule information detected",
            OPSECViolationType.CLASSIFIED_TERM: "Potentially classified terms detected"
        }
        return messages.get(violation_type, "Sensitive information detected")

# Global OPSEC validator instance
opsec_validator = OPSECValidator()