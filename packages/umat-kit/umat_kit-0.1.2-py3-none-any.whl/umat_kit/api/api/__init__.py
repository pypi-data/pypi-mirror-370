"""
UMAT API Testing Framework
Advanced API client and testing utilities for UMAT student portal
"""

# Use relative imports within the packaged module
from .base_client import BaseAPIClient, APIResponse
from .login_api import LoginAPI
from .userinfo_api import UserInfoAPI
from .api_manager import APIManager

__all__ = [
    'BaseAPIClient',
    'APIResponse',
    'LoginAPI',
    'UserInfoAPI',
    'APIManager'
]