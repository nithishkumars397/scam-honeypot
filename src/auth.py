"""
Authentication module for API key validation.

This module handles validating the x-api-key header
in incoming requests against our stored secret key.
"""

from flask import Request
import os


def validate_api_key(request: Request) -> bool:
    """
    Validates the API key from request header.
    
    Args:
        request: Flask request object
    
    Returns:
        True if API key is valid, False otherwise
    
    Usage in routes:
        if not validate_api_key(request):
            return {"status": "error", "message": "Unauthorized"}, 401
    
    Expected header format:
        x-api-key: YOUR_SECRET_API_KEY
    """
    
    # Step 1: Get API key from request header
    provided_key = request.headers.get('x-api-key')
    
    # Step 2: If no key provided, return False
    if not provided_key:
        return False
    
    # Step 3: Get our secret key from environment
    secret_key = os.getenv('API_SECRET_KEY')
    
    # Step 4: If secret key not configured, return False
    if not secret_key:
        return False
    
    # Step 5: Compare keys (case-sensitive)
    return provided_key == secret_key