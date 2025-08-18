"""
Advanced Data Validation System for UMAT API Testing
Provides comprehensive validation for API requests, responses, and data integrity
"""

import re
import json
import jwt
from typing import Dict, Any, List, Optional, Union, Callable, Type
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, ValidationError, validator
from email_validator import validate_email, EmailNotValidError

class ValidationResult:
    """Result of a validation operation"""

    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []

    def add_error(self, error: str) -> None:
        """Add an error message"""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Add a warning message"""
        self.warnings.append(warning)

    def __bool__(self) -> bool:
        """Return validation status"""
        return self.is_valid

    def __str__(self) -> str:
        """String representation of validation result"""
        if self.is_valid:
            status = "✅ Valid"
        else:
            status = "❌ Invalid"

        result = [status]

        if self.errors:
            result.append(f"Errors: {', '.join(self.errors)}")

        if self.warnings:
            result.append(f"Warnings: {', '.join(self.warnings)}")

        return " | ".join(result)

class StudentDataModel(BaseModel):
    """Pydantic model for student data validation"""
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    otherName: Optional[str] = None
    studentNumber: Optional[str] = None
    indexNumber: Optional[str] = None
    phoneNumber: Optional[str] = None
    address: Optional[str] = None
    dateOfBirth: Optional[str] = None
    photoUrl: Optional[str] = None
    programme: Optional[str] = None
    department: Optional[str] = None
    campus: Optional[str] = None
    fullName: Optional[str] = None
    email: Optional[str] = None
    yearGroup: Optional[int] = 0
    level: Optional[int] = 0

    @validator('studentNumber')
    def validate_student_number(cls, v):
        if v is not None and v != "" and not re.match(r'^\d{10}$', v):
            raise ValueError('Student number must be 10 digits')
        return v

    @validator('indexNumber')
    def validate_index_number(cls, v):
        if v is not None and v != "" and not re.match(r'^[A-Z]{3}\.\d{2}\.\d{3}\.\d{3}\.\d{2}$', v):
            raise ValueError('Invalid index number format')
        return v

    @validator('phoneNumber')
    def validate_phone_number(cls, v):
        if v is not None and v != "" and not re.match(r'^0\d{9}$', v):
            raise ValueError('Phone number must be 10 digits starting with 0')
        return v

    @validator('email')
    def validate_email_format(cls, v):
        if v is not None and v != "":
            try:
                validate_email(v)
            except EmailNotValidError:
                raise ValueError('Invalid email format')
        return v

    @validator('dateOfBirth')
    def validate_date_of_birth(cls, v):
        if v is not None and v != "":
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('Invalid date format')
        return v

    @validator('yearGroup')
    def validate_year_group(cls, v):
        if v is not None and v != 0:
            current_year = datetime.now().year
            if v < 1990 or v > current_year:
                raise ValueError(f'Year group must be between 1990 and {current_year}')
        return v

    @validator('level')
    def validate_level(cls, v):
        if v is not None and v != 0 and v not in [100, 200, 300, 400]:
            raise ValueError('Level must be 100, 200, 300, or 400')
        return v

class LoginDataModel(BaseModel):
    """Pydantic model for login data validation"""
    username: str
    password: str

    @validator('username')
    def validate_username(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Username cannot be empty')
        return v.strip()

    @validator('password')
    def validate_password(cls, v):
        if not v or len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

class TokenDataModel(BaseModel):
    """Pydantic model for JWT token validation"""
    token: str

    @validator('token')
    def validate_token_format(cls, v):
        if not v or not v.startswith('eyJ'):
            raise ValueError('Invalid JWT token format')
        return v

class DataValidator:
    """Advanced data validation system"""

    def __init__(self):
        self.patterns = {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone_gh': r'^0\d{9}$',
            'student_number': r'^\d{10}$',
            'index_number': r'^[A-Z]{3}\.\d{2}\.\d{3}\.\d{3}\.\d{2}$',
            'jwt_token': r'^eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$'
        }

    def validate_pattern(self, value: str, pattern_name: str) -> ValidationResult:
        """Validate value against a predefined pattern"""
        result = ValidationResult(True)

        if pattern_name not in self.patterns:
            result.add_error(f"Unknown pattern: {pattern_name}")
            return result

        pattern = self.patterns[pattern_name]
        if not re.match(pattern, value):
            result.add_error(f"Value '{value}' does not match {pattern_name} pattern")

        return result

    def validate_student_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate student data using Pydantic model"""
        result = ValidationResult(True)

        try:
            StudentDataModel(**data)
        except ValidationError as e:
            result.is_valid = False
            for error in e.errors():
                field = error['loc'][0] if error['loc'] else 'unknown'
                message = error['msg']
                result.add_error(f"{field}: {message}")

        return result

    def validate_login_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate login data"""
        result = ValidationResult(True)

        try:
            LoginDataModel(**data)
        except ValidationError as e:
            result.is_valid = False
            for error in e.errors():
                field = error['loc'][0] if error['loc'] else 'unknown'
                message = error['msg']
                result.add_error(f"{field}: {message}")

        return result

    def validate_jwt_token(self, token: str, verify_signature: bool = False,
                          secret_key: Optional[str] = None) -> ValidationResult:
        """Validate JWT token structure and optionally verify signature"""
        result = ValidationResult(True)

        # Basic format validation
        format_result = self.validate_pattern(token, 'jwt_token')
        if not format_result:
            result.errors.extend(format_result.errors)
            return result

        try:
            # Decode without verification first
            header = jwt.get_unverified_header(token)
            payload = jwt.decode(token, options={"verify_signature": False})

            # Check token structure
            if 'exp' in payload:
                exp_timestamp = payload['exp']
                exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

                if exp_datetime < datetime.now(timezone.utc):
                    result.add_error("Token has expired")
                else:
                    result.add_warning(f"Token expires at {exp_datetime}")

            # Verify signature if requested
            if verify_signature and secret_key:
                try:
                    jwt.decode(token, secret_key, algorithms=["HS256"])
                except jwt.exceptions.DecodeError:
                    result.add_error("Invalid token signature or decode error")

        except jwt.exceptions.DecodeError:
            result.add_error("Invalid JWT token structure")
        except Exception as e:
            result.add_error(f"Token validation error: {str(e)}")

        return result

    def validate_api_response(self, response_data: Dict[str, Any],
                            expected_fields: List[str]) -> ValidationResult:
        """Validate API response contains expected fields"""
        result = ValidationResult(True)

        missing_fields = []
        for field in expected_fields:
            if field not in response_data:
                missing_fields.append(field)

        if missing_fields:
            result.add_error(f"Missing required fields: {', '.join(missing_fields)}")

        # Check for null values in critical fields
        critical_fields = ['firstName', 'lastName', 'studentNumber', 'programme']
        null_critical_fields = []

        for field in critical_fields:
            if field in response_data and response_data[field] is None:
                null_critical_fields.append(field)

        if null_critical_fields:
            result.add_warning(f"Critical fields with null values: {', '.join(null_critical_fields)}")

        return result

    def validate_http_status(self, status_code: int, expected_codes: List[int] = None) -> ValidationResult:
        """Validate HTTP status code"""
        result = ValidationResult(True)

        if expected_codes is None:
            expected_codes = [200, 201, 202, 204]

        if status_code not in expected_codes:
            result.add_error(f"Unexpected status code: {status_code}")

        # Add warnings for specific status codes
        if status_code == 401:
            result.add_warning("Authentication required")
        elif status_code == 403:
            result.add_warning("Access forbidden")
        elif status_code == 404:
            result.add_warning("Resource not found")
        elif status_code >= 500:
            result.add_warning("Server error")

        return result

    def validate_response_time(self, response_time: float, max_time: float = 5.0) -> ValidationResult:
        """Validate API response time"""
        result = ValidationResult(True)

        if response_time > max_time:
            result.add_error(f"Response time {response_time:.2f}s exceeds maximum {max_time}s")
        elif response_time > max_time * 0.8:
            result.add_warning(f"Response time {response_time:.2f}s is approaching limit")

        return result

    def validate_json_structure(self, json_data: str) -> ValidationResult:
        """Validate JSON structure"""
        result = ValidationResult(True)

        try:
            parsed_data = json.loads(json_data)
            if not isinstance(parsed_data, (dict, list)):
                result.add_warning("JSON root is not an object or array")
        except json.JSONDecodeError as e:
            result.add_error(f"Invalid JSON: {str(e)}")

        return result

    def create_custom_validator(self, validation_func: Callable[[Any], bool],
                              error_message: str) -> Callable[[Any], ValidationResult]:
        """Create a custom validator function"""
        def validator(value: Any) -> ValidationResult:
            result = ValidationResult(True)
            try:
                if not validation_func(value):
                    result.add_error(error_message)
            except Exception as e:
                result.add_error(f"Validation error: {str(e)}")
            return result

        return validator

    def batch_validate(self, validations: List[tuple]) -> ValidationResult:
        """Run multiple validations and combine results"""
        combined_result = ValidationResult(True)

        for validation_func, *args in validations:
            result = validation_func(*args)
            if not result.is_valid:
                combined_result.is_valid = False
            combined_result.errors.extend(result.errors)
            combined_result.warnings.extend(result.warnings)

        return combined_result

# Global validator instance
data_validator = DataValidator()