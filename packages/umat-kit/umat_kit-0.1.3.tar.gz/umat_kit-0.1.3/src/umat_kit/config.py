"""
Advanced Configuration Management for UMAT Project
Handles environment variables, database connections, and application settings
"""

import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    postgresql_url: str = field(default_factory=lambda: os.getenv('DATABASE_URL', ''))
    mongodb_url: str = field(default_factory=lambda: os.getenv('MONGODB_URL', ''))
    redis_url: str = field(default_factory=lambda: os.getenv('REDIS_URL', ''))
    migration_batch_size: int = field(default_factory=lambda: int(os.getenv('MIGRATION_BATCH_SIZE', '1000')))
    migration_delay: float = field(default_factory=lambda: float(os.getenv('MIGRATION_DELAY', '0.1')))

@dataclass
class APIConfig:
    """API configuration settings"""
    base_url: str = field(default_factory=lambda: os.getenv('UMAT_BASE_URL', 'https://student.umat.edu.gh'))
    api_version: str = field(default_factory=lambda: os.getenv('UMAT_API_VERSION', 'api'))
    timeout: int = field(default_factory=lambda: int(os.getenv('REQUEST_TIMEOUT', '30')))
    max_retries: int = field(default_factory=lambda: int(os.getenv('MAX_RETRIES', '3')))

    @property
    def api_base_url(self) -> str:
        """Get the complete API base URL"""
        return f"{self.base_url}/{self.api_version}"

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    jwt_secret: str = field(default_factory=lambda: os.getenv('JWT_SECRET_KEY', ''))
    encryption_key: str = field(default_factory=lambda: os.getenv('ENCRYPTION_KEY', ''))

    def __post_init__(self):
        if not self.jwt_secret:
            raise ValueError("JWT_SECRET_KEY must be set in environment variables")

@dataclass
class TestConfig:
    """Test configuration settings"""
    username: str = ''
    password: str = ''

    @property
    def has_credentials(self) -> bool:
        """Check if test credentials are available"""
        return bool(self.username and self.password)

@dataclass
class AppConfig:
    """Main application configuration"""
    debug: bool = field(default_factory=lambda: os.getenv('DEBUG', 'False').lower() == 'true')
    log_level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))

    # Sub-configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    api: APIConfig = field(default_factory=APIConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    test: TestConfig = field(default_factory=TestConfig)

    def __post_init__(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('umat_migration.log')
            ]
        )

# Global configuration instance
config = AppConfig()

class ConfigManager:
    """Advanced configuration management with validation and caching"""

    def __init__(self):
        self._config_cache: Dict[str, Any] = {}
        self._logger = logging.getLogger(__name__)

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value with caching"""
        if key in self._config_cache:
            return self._config_cache[key]

        value = os.getenv(key, default)
        self._config_cache[key] = value
        return value

    def validate_config(self) -> bool:
        """Validate all required configuration values"""
        required_configs = [
            'UMAT_BASE_URL',
            'JWT_SECRET_KEY'
        ]

        missing_configs = []
        for config_key in required_configs:
            if not os.getenv(config_key):
                missing_configs.append(config_key)

        if missing_configs:
            self._logger.error(f"Missing required configurations: {missing_configs}")
            return False

        self._logger.info("Configuration validation passed")
        return True

    def get_database_url(self, db_type: str = 'postgresql') -> Optional[str]:
        """Get database URL for specified database type"""
        db_urls = {
            'postgresql': config.database.postgresql_url,
            'mongodb': config.database.mongodb_url,
            'redis': config.database.redis_url
        }
        return db_urls.get(db_type)

    def get_api_endpoint(self, endpoint: str) -> str:
        """Construct full API endpoint URL"""
        return f"{config.api.api_base_url}/{endpoint.lstrip('/')}"

# Global configuration manager instance
config_manager = ConfigManager()