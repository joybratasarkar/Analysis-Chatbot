"""
Custom actions for NeMo Guardrails in the AI Data Analysis Chatbot
"""
import re
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Sensitive data patterns
SENSITIVE_PATTERNS = [
    r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
    r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email (basic)
    r'\bpassword\s*[:=]\s*\S+\b',  # Password
    r'\bapi[_\s]?key\s*[:=]\s*\S+\b',  # API key
    r'\btoken\s*[:=]\s*\S+\b',  # Token
]

# Dangerous code patterns
DANGEROUS_CODE_PATTERNS = [
    r'import\s+os',
    r'import\s+subprocess',
    r'import\s+sys',
    r'__import__\s*\(',
    r'exec\s*\(',
    r'eval\s*\(',
    r'open\s*\(',
    r'file\s*\(',
    r'input\s*\(',
    r'raw_input\s*\(',
]

async def validate_data_request(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate data analysis requests for safety and appropriateness
    """
    user_message = context.get("user_message", "")
    
    # Check for sensitive data in the request
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, user_message, re.IGNORECASE):
            logger.warning(f"Sensitive data detected in user request")
            return {
                "is_safe": False,
                "reason": "sensitive_data",
                "message": "I detected potentially sensitive information in your request. Please remove any personal identifiers and try again."
            }
    
    # Check for malicious intent
    malicious_keywords = [
        "hack", "exploit", "bypass", "inject", "malicious", "virus", 
        "steal", "unauthorized", "breach", "crack"
    ]
    
    for keyword in malicious_keywords:
        if keyword in user_message.lower():
            logger.warning(f"Potentially malicious keyword detected: {keyword}")
            return {
                "is_safe": False,
                "reason": "malicious_intent",
                "message": "I can only help with legitimate data analysis tasks. Please rephrase your request."
            }
    
    return {"is_safe": True}

async def sanitize_code_output(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize generated code before execution to ensure safety
    """
    generated_code = context.get("generated_code", "")
    
    if not generated_code:
        return {"is_safe": True, "sanitized_code": generated_code}
    
    # Check for dangerous patterns
    for pattern in DANGEROUS_CODE_PATTERNS:
        if re.search(pattern, generated_code, re.IGNORECASE):
            logger.warning(f"Dangerous code pattern detected: {pattern}")
            return {
                "is_safe": False,
                "reason": "unsafe_code",
                "message": "The generated code contains potentially unsafe operations. I'll create a safer version.",
                "sanitized_code": _sanitize_dangerous_code(generated_code)
            }
    
    # Additional safety checks
    if any(keyword in generated_code.lower() for keyword in ["rm -rf", "del ", "remove", "delete"]):
        logger.warning("File manipulation detected in generated code")
        return {
            "is_safe": False,
            "reason": "file_manipulation",
            "message": "File manipulation operations are not allowed for security reasons.",
            "sanitized_code": ""
        }
    
    return {"is_safe": True, "sanitized_code": generated_code}

async def check_data_compliance(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure data processing complies with privacy regulations
    """
    data_info = context.get("data_info", {})
    user_message = context.get("user_message", "")
    
    # Check for requests that might violate privacy
    privacy_concerns = [
        "identify individuals",
        "personal information",
        "private data",
        "confidential",
        "sensitive"
    ]
    
    for concern in privacy_concerns:
        if concern in user_message.lower():
            logger.info(f"Privacy concern detected: {concern}")
            return {
                "compliance_check": "warning",
                "message": "I'll ensure that any analysis respects privacy and doesn't expose individual information."
            }
    
    return {"compliance_check": "passed"}

def _sanitize_dangerous_code(code: str) -> str:
    """
    Remove or replace dangerous code patterns with safe alternatives
    """
    # Remove dangerous imports
    for pattern in DANGEROUS_CODE_PATTERNS:
        code = re.sub(pattern, "# Unsafe operation removed", code, flags=re.IGNORECASE)
    
    # Ensure only safe data operations
    safe_code_template = """
# Safe data analysis code
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# Original code has been sanitized for security
# Only safe data visualization and analysis operations are allowed
"""
    
    return safe_code_template

# Register actions for NeMo Guardrails
def register_actions():
    """
    Register custom actions with NeMo Guardrails
    """
    return {
        "validate_data_request": validate_data_request,
        "sanitize_code_output": sanitize_code_output,
        "check_data_compliance": check_data_compliance,
    }