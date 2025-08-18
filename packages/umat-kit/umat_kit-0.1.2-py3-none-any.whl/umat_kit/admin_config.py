"""
Admin Configuration for UMAT Student Portal
This file contains admin credentials and should NOT be pushed to GitHub
"""

import os
from typing import Optional

class AdminConfig:
    """Admin configuration management"""

    def __init__(self):
        # Default admin credentials (can be overridden by environment variables)
        self.ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', '9012562822')
        self.ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '9012562822')

    def is_admin(self, username: str, password: str) -> bool:
        """Check if the provided credentials are admin credentials"""
        return (username == self.ADMIN_USERNAME and
                password == self.ADMIN_PASSWORD)

    def get_admin_username(self) -> str:
        """Get admin username"""
        return self.ADMIN_USERNAME

# Global admin config instance
admin_config = AdminConfig()