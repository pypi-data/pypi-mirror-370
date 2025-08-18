"""
Advanced User Information API Client for UMAT Student Portal
Handles user profile data retrieval, validation, and management
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from .base_client import BaseAPIClient, APIResponse
from ...utils.utils.logger import get_logger
from ...utils.utils.validators import data_validator, ValidationResult
from ...utils.utils.terminal_colors import colored_output

class UserInfoAPI(BaseAPIClient):
    """Advanced user information API client with comprehensive data management"""

    def __init__(self, base_url: Optional[str] = None):
        super().__init__(base_url)
        self.logger = get_logger(self.__class__.__name__)

        # User info endpoints
        self.endpoints = {
            'student_portal': '/api/Account/UserInfo/StudentPortal',
            'profile': '/api/Account/Profile',
            'academic_info': '/api/Account/AcademicInfo',
            'personal_info': '/api/Account/PersonalInfo',
            'contact_info': '/api/Account/ContactInfo',
            # Update endpoints
            'update_profile': '/api/Account/Profile',
            'update_personal_info': '/api/Account/PersonalInfo',
            'update_contact_info': '/api/Account/ContactInfo'
        }

        # Expected fields for different endpoints
        self.expected_fields = {
            'student_portal': [
                'firstName', 'lastName', 'studentNumber', 'indexNumber',
                'programme', 'department', 'campus', 'yearGroup', 'level'
            ],
            'profile': ['firstName', 'lastName', 'fullName', 'email'],
            'academic_info': ['programme', 'department', 'yearGroup', 'level'],
            'personal_info': ['dateOfBirth', 'address', 'phoneNumber'],
            'contact_info': ['phoneNumber', 'email', 'address']
        }

        # Cached user data
        self.cached_user_data: Optional[Dict[str, Any]] = None
        self.cache_timestamp: Optional[datetime] = None
        self.cache_duration_minutes = 15  # Cache for 15 minutes

    def get_student_portal_info(self, use_cache: bool = True,
                               validate_data: bool = True, display_info: bool = True) -> APIResponse:
        """
        Get comprehensive student portal information

        Args:
            use_cache: Whether to use cached data if available
            validate_data: Whether to validate response data
            display_info: Whether to display the student information

        Returns:
            APIResponse with student information
        """
        # Only show header if displaying info
        if display_info:
            colored_output.print_header("👤 Student Portal Information", "Retrieving user data...")

        # Check cache if requested
        if use_cache and self._is_cache_valid():
            if display_info:
                colored_output.print_info("Using cached user data")
            response = APIResponse(
                status_code=200,
                headers={'Content-Type': 'application/json'},
                data=self.cached_user_data,
                response_time=0.001,
                request_method='GET',
                request_url=self._build_url(self.endpoints['student_portal'])
            )
            response.validation_result = ValidationResult(True)
            return response

        # Make API request
        response = self.get(
            self.endpoints['student_portal'],
            expected_fields=self.expected_fields['student_portal']
        )

        # Process response
        if response.is_success and response.data:
            # Cache the data
            self.cached_user_data = response.data
            self.cache_timestamp = datetime.now()

            # Validate student data if requested
            if validate_data:
                validation_result = data_validator.validate_student_data(response.data)
                response.validation_result = validation_result

                if validation_result.is_valid:
                    colored_output.print_success("✅ Student data validation passed")
                else:
                    colored_output.print_warning("⚠️ Student data validation issues")
                    colored_output.print_info("Note: Some fields may be empty or null from the API")
                    if validation_result.errors:
                        colored_output.print_info("Validation details:")
                        for error in validation_result.errors[:3]:  # Show only first 3 errors
                            colored_output.print_info(f"  • {error}")
                        if len(validation_result.errors) > 3:
                            colored_output.print_info(f"  • ... and {len(validation_result.errors) - 3} more issues")

            # Log user info (but don't display unless explicitly requested)
            self.logger.info(f"Retrieved student info for: {response.data.get('fullName', 'Unknown')}")
            # Only display if explicitly requested
            if display_info:
                self._display_student_info(response.data)

        else:
            # Handle different types of failures with user-friendly messages
            if response.error_message:
                colored_output.print_error(f"❌ {response.error_message}")
            elif response.status_code == 401:
                colored_output.print_error("❌ Authentication failed - please log in again")
            elif response.status_code == 403:
                colored_output.print_error("❌ Access denied - insufficient permissions")
            elif response.status_code == 404:
                colored_output.print_error("❌ Student information not found")
            elif response.status_code >= 500:
                colored_output.print_error("❌ Server error - please try again later")
            else:
                colored_output.print_error(f"❌ Failed to retrieve student information (Status: {response.status_code})")

            # Show additional context if available
            if response.status_code in [502, 503]:
                colored_output.print_info("💡 The server appears to be temporarily unavailable. Please try again in a few minutes.")
            elif response.status_code == 408:
                colored_output.print_info("💡 Request timed out. Check your internet connection and try again.")

            self.logger.error(f"Failed to get student info: {response.status_code} - {response.error_message or 'Unknown error'}")

        return response

    def get_profile_info(self) -> APIResponse:
        """
        Get user profile information

        Returns:
            APIResponse with profile data
        """
        colored_output.print_header("📋 Profile Information")

        response = self.get(
            self.endpoints['profile'],
            expected_fields=self.expected_fields['profile']
        )

        if response.is_success and response.data:
            colored_output.print_json(response.data, "Profile Information")
            self.logger.info("Profile information retrieved successfully")
        else:
            colored_output.print_error("Failed to retrieve profile information")

        return response

    def get_academic_info(self) -> APIResponse:
        """
        Get academic information

        Returns:
            APIResponse with academic data
        """
        colored_output.print_header("🎓 Academic Information")

        response = self.get(
            self.endpoints['academic_info'],
            expected_fields=self.expected_fields['academic_info']
        )

        if response.is_success and response.data:
            self._display_academic_info(response.data)
            self.logger.info("Academic information retrieved successfully")
        else:
            colored_output.print_error("Failed to retrieve academic information")

        return response

    def get_personal_info(self) -> APIResponse:
        """
        Get personal information

        Returns:
            APIResponse with personal data
        """
        colored_output.print_header("🏠 Personal Information")

        response = self.get(
            self.endpoints['personal_info'],
            expected_fields=self.expected_fields['personal_info']
        )

        if response.is_success and response.data:
            self._display_personal_info(response.data)
            self.logger.info("Personal information retrieved successfully")
        else:
            colored_output.print_error("Failed to retrieve personal information")

        return response

    def get_contact_info(self) -> APIResponse:
        """
        Get contact information

        Returns:
            APIResponse with contact data
        """
        colored_output.print_header("📞 Contact Information")

        response = self.get(
            self.endpoints['contact_info'],
            expected_fields=self.expected_fields['contact_info']
        )

        if response.is_success and response.data:
            self._display_contact_info(response.data)
            self.logger.info("Contact information retrieved successfully")
        else:
            colored_output.print_error("Failed to retrieve contact information")

        return response

    def get_all_user_info(self, validate_data: bool = True) -> Dict[str, APIResponse]:
        """
        Get all available user information from working endpoints

        Args:
            validate_data: Whether to validate response data

        Returns:
            Dictionary with responses from available endpoints
        """
        colored_output.print_header("🔍 Complete User Information Retrieval")

        responses = {}

        # Get student portal info (main and only working endpoint)
        colored_output.print_info("Fetching student portal information...")
        responses['student_portal'] = self.get_student_portal_info(validate_data=validate_data)

        # Note: Other endpoints (profile, academic_info, personal_info, contact_info)
        # return 404 Not Found, so we skip them to avoid unnecessary errors

        # Print summary
        successful_endpoints = [name for name, resp in responses.items() if resp.is_success]
        failed_endpoints = [name for name, resp in responses.items() if not resp.is_success]

        colored_output.print_success(f"Successfully retrieved data from {len(successful_endpoints)} endpoint(s)")
        if failed_endpoints:
            colored_output.print_warning(f"Failed endpoints: {', '.join(failed_endpoints)}")

        colored_output.print_info("Note: Only student portal endpoint is currently available")

        return responses

    def validate_user_data(self, user_data: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate user data comprehensively

        Args:
            user_data: User data to validate (uses cached data if None)

        Returns:
            ValidationResult with validation details
        """
        if user_data is None:
            user_data = self.cached_user_data

        if not user_data:
            result = ValidationResult(False)
            result.add_error("No user data available for validation")
            return result

        return data_validator.validate_student_data(user_data)

    def compare_user_data(self, data1: Dict[str, Any], data2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two sets of user data and identify differences

        Args:
            data1: First dataset
            data2: Second dataset

        Returns:
            Dictionary with comparison results
        """
        comparison = {
            'identical': True,
            'differences': {},
            'missing_in_data1': [],
            'missing_in_data2': [],
            'common_fields': []
        }

        all_keys = set(data1.keys()) | set(data2.keys())

        for key in all_keys:
            if key in data1 and key in data2:
                comparison['common_fields'].append(key)
                if data1[key] != data2[key]:
                    comparison['identical'] = False
                    comparison['differences'][key] = {
                        'data1': data1[key],
                        'data2': data2[key]
                    }
            elif key in data1:
                comparison['missing_in_data2'].append(key)
                comparison['identical'] = False
            else:
                comparison['missing_in_data1'].append(key)
                comparison['identical'] = False

        return comparison

    def clear_cache(self) -> None:
        """Clear cached user data"""
        self.cached_user_data = None
        self.cache_timestamp = None
        colored_output.print_info("User data cache cleared")
        self.logger.info("User data cache cleared")

    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if not self.cached_user_data or not self.cache_timestamp:
            return False

        cache_age = datetime.now() - self.cache_timestamp
        return cache_age.total_seconds() < (self.cache_duration_minutes * 60)

    def _display_student_info(self, data: Dict[str, Any]) -> None:
        """Display student information in a formatted way"""
        def format_value(value):
            """Format value for display, handling None/null values"""
            if value is None or value == "" or value == "null":
                return "Not Available"
            return str(value)

        full_name = format_value(data.get('fullName'))
        colored_output.print_success(f"Student: {full_name}")

        # Basic info with better formatting
        basic_info = [
            ['Student Number', format_value(data.get('studentNumber'))],
            ['Index Number', format_value(data.get('indexNumber'))],
            ['First Name', format_value(data.get('firstName'))],
            ['Last Name', format_value(data.get('lastName'))],
            ['Programme', format_value(data.get('programme'))],
            ['Department', format_value(data.get('department'))],
            ['Campus', format_value(data.get('campus'))],
            ['Year Group', format_value(data.get('yearGroup')) if data.get('yearGroup', 0) != 0 else "Not Available"],
            ['Level', format_value(data.get('level')) if data.get('level', 0) != 0 else "Not Available"],
            ['Phone Number', format_value(data.get('phoneNumber'))],
            ['Address', format_value(data.get('address'))],
            ['Date of Birth', format_value(data.get('dateOfBirth'))]
        ]

        colored_output.print_table(
            basic_info,
            ['Field', 'Value'],
            'Student Information'
        )

        # Display raw data for debugging if needed (commented out for production)
        # colored_output.print_info("Raw API Response:")
        # colored_output.print_json(data, "Student Portal Data")

    def _display_academic_info(self, data: Dict[str, Any]) -> None:
        """Display academic information"""
        academic_data = [
            ['Programme', data.get('programme', 'N/A')],
            ['Department', data.get('department', 'N/A')],
            ['Year Group', str(data.get('yearGroup', 'N/A'))],
            ['Level', str(data.get('level', 'N/A'))],
            ['Campus', data.get('campus', 'N/A')]
        ]

        colored_output.print_table(
            academic_data,
            ['Field', 'Value'],
            'Academic Information'
        )

    def _display_personal_info(self, data: Dict[str, Any]) -> None:
        """Display personal information"""
        personal_data = [
            ['Date of Birth', data.get('dateOfBirth', 'N/A')],
            ['Address', data.get('address', 'N/A')],
            ['Phone Number', data.get('phoneNumber', 'N/A')]
        ]

        colored_output.print_table(
            personal_data,
            ['Field', 'Value'],
            'Personal Information'
        )

    def _display_contact_info(self, data: Dict[str, Any]) -> None:
        """Display contact information"""
        contact_data = [
            ['Phone Number', data.get('phoneNumber', 'N/A')],
            ['Email', data.get('email', 'N/A')],
            ['Address', data.get('address', 'N/A')]
        ]

        colored_output.print_table(
            contact_data,
            ['Field', 'Value'],
            'Contact Information'
        )

    def test_user_info_endpoints(self) -> Dict[str, Any]:
        """
        Test available user information endpoints (only working ones)

        Returns:
            Dictionary with test results
        """
        colored_output.print_header("🧪 User Info Endpoints Test")

        test_results = {
            'endpoints_tested': 0,
            'successful_endpoints': 0,
            'failed_endpoints': 0,
            'endpoint_results': {},
            'overall_success': False,
            'data_validation_passed': False
        }

        # Test main student portal endpoint (the only working one)
        colored_output.print_info("Testing student portal endpoint...")
        student_response = self.get_student_portal_info(use_cache=False, validate_data=True)

        test_results['endpoints_tested'] += 1
        test_results['endpoint_results']['student_portal'] = {
            'success': student_response.is_success,
            'status_code': student_response.status_code,
            'response_time': student_response.response_time,
            'has_data': bool(student_response.data),
            'validation_passed': student_response.validation_result.is_valid if student_response.validation_result else False
        }

        if student_response.is_success:
            test_results['successful_endpoints'] += 1
            test_results['data_validation_passed'] = test_results['endpoint_results']['student_portal']['validation_passed']
        else:
            test_results['failed_endpoints'] += 1

        # Skip other endpoints as they return 404 - only test if explicitly requested
        # Note: profile, academic_info, personal_info, contact_info endpoints are not available

        # Calculate overall success
        test_results['overall_success'] = (
            test_results['successful_endpoints'] > 0 and
            test_results['endpoint_results']['student_portal']['success']
        )

        # Print test summary
        if test_results['overall_success']:
            colored_output.print_success("🎉 User info endpoints test completed successfully!")
        else:
            colored_output.print_error("❌ User info endpoints test failed")

        colored_output.print_info(
            f"Results: {test_results['successful_endpoints']}/{test_results['endpoints_tested']} endpoints successful"
        )

        colored_output.print_json(test_results, "Detailed Test Results")

        return test_results

    # ==================== UPDATE METHODS ====================

    def update_profile(self, profile_data: Dict[str, Any],
                      validate_data: bool = True) -> APIResponse:
        """
        Update user profile information

        Args:
            profile_data: Dictionary containing profile fields to update
            validate_data: Whether to validate the update data

        Returns:
            APIResponse object with update results
        """
        colored_output.print_header("📝 Updating Profile Information")

        if not self._auth_token:
            colored_output.print_error("❌ Authentication required for profile updates")
            return APIResponse(
                status_code=401,
                headers={},
                data={'error': 'Authentication required'}
            )

        # Validate update data if requested
        if validate_data:
            validation_result = self._validate_profile_update_data(profile_data)
            if not validation_result.is_valid:
                colored_output.print_error("❌ Profile update data validation failed")
                for error in validation_result.errors:
                    colored_output.print_error(f"  • {error}")
                return APIResponse(
                    status_code=400,
                    headers={},
                    data={'error': 'Validation failed', 'details': validation_result.errors}
                )

        colored_output.print_info(f"Updating profile with data: {list(profile_data.keys())}")

        try:
            response = self.put(
                self.endpoints['update_profile'],
                payload=profile_data,
                headers={'Content-Type': 'application/json'}
            )

            if response.is_success:
                colored_output.print_success("✅ Profile updated successfully")
                self.logger.info(f"Profile updated successfully: {list(profile_data.keys())}")
                # Clear cache to force refresh
                self.clear_cache()
            else:
                colored_output.print_error(f"❌ Profile update failed: {response.status_code}")
                self.logger.error(f"Profile update failed: {response.status_code} - {response.data}")

            return response

        except Exception as e:
            colored_output.print_error(f"❌ Profile update error: {str(e)}")
            self.logger.error(f"Profile update error: {str(e)}")
            return APIResponse(
                status_code=500,
                headers={},
                data={'error': str(e)}
            )

    def update_contact_info(self, contact_data: Dict[str, Any],
                           validate_data: bool = True) -> APIResponse:
        """
        Update user contact information

        Args:
            contact_data: Dictionary containing contact fields to update
            validate_data: Whether to validate the update data

        Returns:
            APIResponse object with update results
        """
        colored_output.print_header("📞 Updating Contact Information")

        if not self._auth_token:
            colored_output.print_error("❌ Authentication required for contact updates")
            return APIResponse(status_code=401, headers={}, data={'error': 'Authentication required'}
            )

        # Validate update data if requested
        if validate_data:
            validation_result = self._validate_contact_update_data(contact_data)
            if not validation_result.is_valid:
                colored_output.print_error("❌ Contact update data validation failed")
                for error in validation_result.errors:
                    colored_output.print_error(f"  • {error}")
                return APIResponse(status_code=400, headers={}, data={'error': 'Validation failed', 'details': validation_result.errors}
                )

        colored_output.print_info(f"Updating contact info with data: {list(contact_data.keys())}")

        try:
            response = self.put(
                self.endpoints['update_contact_info'],
                payload=contact_data,
                headers={'Content-Type': 'application/json'}
            )

            if response.is_success:
                colored_output.print_success("✅ Contact information updated successfully")
                self.logger.info(f"Contact info updated successfully: {list(contact_data.keys())}")
                # Clear cache to force refresh
                self.clear_cache()
            else:
                colored_output.print_error(f"❌ Contact update failed: {response.status_code}")
                self.logger.error(f"Contact update failed: {response.status_code} - {response.data}")

            return response

        except Exception as e:
            colored_output.print_error(f"❌ Contact update error: {str(e)}")
            self.logger.error(f"Contact update error: {str(e)}")
            return APIResponse(status_code=500, headers={}, data={'error': str(e)}
            )

    def update_personal_info(self, personal_data: Dict[str, Any],
                            validate_data: bool = True) -> APIResponse:
        """
        Update user personal information

        Args:
            personal_data: Dictionary containing personal fields to update
            validate_data: Whether to validate the update data

        Returns:
            APIResponse object with update results
        """
        colored_output.print_header("🏠 Updating Personal Information")

        if not self._auth_token:
            colored_output.print_error("❌ Authentication required for personal info updates")
            return APIResponse(status_code=401, headers={}, data={'error': 'Authentication required'}
            )

        # Validate update data if requested
        if validate_data:
            validation_result = self._validate_personal_update_data(personal_data)
            if not validation_result.is_valid:
                colored_output.print_error("❌ Personal info update data validation failed")
                for error in validation_result.errors:
                    colored_output.print_error(f"  • {error}")
                return APIResponse(status_code=400, headers={}, data={'error': 'Validation failed', 'details': validation_result.errors}
                )

        colored_output.print_info(f"Updating personal info with data: {list(personal_data.keys())}")

        try:
            response = self.put(
                self.endpoints['update_personal_info'],
                payload=personal_data,
                headers={'Content-Type': 'application/json'}
            )

            if response.is_success:
                colored_output.print_success("✅ Personal information updated successfully")
                self.logger.info(f"Personal info updated successfully: {list(personal_data.keys())}")
                # Clear cache to force refresh
                self.clear_cache()
            else:
                colored_output.print_error(f"❌ Personal info update failed: {response.status_code}")
                self.logger.error(f"Personal info update failed: {response.status_code} - {response.data}")

            return response

        except Exception as e:
            colored_output.print_error(f"❌ Personal info update error: {str(e)}")
            self.logger.error(f"Personal info update error: {str(e)}")
            return APIResponse(status_code=500, headers={}, data={'error': str(e)}
            )

    def update_email(self, email: str, validate_email: bool = True) -> APIResponse:
        """
        Convenience method to update just the email address

        Args:
            email: New email address
            validate_email: Whether to validate the email format

        Returns:
            APIResponse object with update results
        """
        colored_output.print_header("📧 Updating Email Address")

        if validate_email:
            # Simple email validation
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                colored_output.print_error("❌ Invalid email format")
                return APIResponse(status_code=400, headers={}, data={'error': 'Invalid email format'}
                )

        colored_output.print_info(f"Updating email to: {email}")

        # Try updating via profile endpoint first
        profile_response = self.update_profile({'email': email}, validate_data=False)

        if profile_response.is_success:
            return profile_response

        # If profile update fails, try contact info endpoint
        colored_output.print_info("Profile update failed, trying contact info endpoint...")
        contact_response = self.update_contact_info({'email': email}, validate_data=False)

        return contact_response

    # ==================== VALIDATION METHODS ====================

    def _validate_profile_update_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate profile update data"""
        result = ValidationResult(True)

        # Check for allowed fields
        allowed_fields = ['firstName', 'lastName', 'fullName', 'email', 'otherName']
        for field in data.keys():
            if field not in allowed_fields:
                result.add_warning(f"Field '{field}' may not be updatable via profile endpoint")

        # Validate email if present
        if 'email' in data and data['email']:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                result.add_error(f"Invalid email format: {data['email']}")

        # Validate names if present
        for name_field in ['firstName', 'lastName', 'fullName', 'otherName']:
            if name_field in data and data[name_field]:
                if not isinstance(data[name_field], str) or len(data[name_field].strip()) < 1:
                    result.add_error(f"Invalid {name_field}: must be a non-empty string")

        return result

    def _validate_contact_update_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate contact update data"""
        result = ValidationResult(True)

        # Check for allowed fields
        allowed_fields = ['email', 'phoneNumber', 'address']
        for field in data.keys():
            if field not in allowed_fields:
                result.add_warning(f"Field '{field}' may not be updatable via contact endpoint")

        # Validate email if present
        if 'email' in data and data['email']:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                result.add_error(f"Invalid email format: {data['email']}")

        # Validate phone number if present
        if 'phoneNumber' in data and data['phoneNumber']:
            phone = str(data['phoneNumber']).strip()
            if len(phone) < 10 or not phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
                result.add_error(f"Invalid phone number format: {data['phoneNumber']}")

        return result

    def _validate_personal_update_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate personal update data"""
        result = ValidationResult(True)

        # Check for allowed fields
        allowed_fields = ['dateOfBirth', 'address', 'phoneNumber']
        for field in data.keys():
            if field not in allowed_fields:
                result.add_warning(f"Field '{field}' may not be updatable via personal info endpoint")

        # Validate date of birth if present
        if 'dateOfBirth' in data and data['dateOfBirth']:
            try:
                from datetime import datetime
                if isinstance(data['dateOfBirth'], str):
                    datetime.fromisoformat(data['dateOfBirth'].replace('Z', '+00:00'))
            except ValueError:
                result.add_error(f"Invalid date format for dateOfBirth: {data['dateOfBirth']}")

        # Validate phone number if present
        if 'phoneNumber' in data and data['phoneNumber']:
            phone = str(data['phoneNumber']).strip()
            if len(phone) < 10 or not phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
                result.add_error(f"Invalid phone number format: {data['phoneNumber']}")

        return result