#!/usr/bin/env python3
"""
UMAT Admin API
Specialized API client for admin endpoints and privileged operations
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from api.base_client import BaseAPIClient, APIResponse
from utils.logger import get_logger
from utils.terminal_colors import colored_output

class AdminAPI(BaseAPIClient):
    """Specialized API client for admin operations"""

    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        super().__init__(base_url)
        self._auth_token = auth_token
        self.logger = get_logger(self.__class__.__name__)

        # Admin endpoints discovered
        self.admin_endpoints = {
            # Direct admin endpoints
            'users_admin': '/api/Users/Admin',
            'student_admin': '/api/Student/Admin',
            'students_admin': '/api/Students/Admin',

            # Administration endpoints
            'v1_administration': '/api/v1/Administration',
            'v2_administration': '/api/v2/Administration',

            # Management endpoints
            'rest_management': '/rest/management',
            'webapi_management': '/webapi/Management',

            # Control endpoints
            'api_control': '/api/control',

            # System endpoints
            'api_modify': '/api/Modify',
            'v2_modify': '/api/v2/Modify',
            'v2_modify_caps': '/api/v2/MODIFY',
            'api_update': '/api/Update',
            'v2_update': '/v2/update',
            'v2_updates': '/api/v2/Updates',
            'api_v1_updates': '/api/v1/UPDATES',
            'rest_update': '/rest/UPDATE',

            # Authentication admin endpoints
            'v1_authentication': '/api/v1/authentication',
            'rest_auth': '/rest/AUTH',
            'v2_auth': '/v2/AUTH',
            'v2_auth_alt': '/api/v2/Auth',
            'webapi_auth': '/webapi/auth',

            # Configuration endpoints
            'v1_configuration': '/v1/configuration',
            'api_v1_configuration': '/api/v1/configuration',
            'webapi_config': '/webapi/CONFIG',
            'rest_config': '/rest/Config',

            # Settings endpoints
            'v1_settings': '/v1/SETTINGS',
            'v2_settings': '/v2/SETTINGS',
            'v2_settings_alt': '/v2/Settings',

            # User management endpoints
            'webapi_user': '/webapi/USER',
            'webapi_modify': '/webapi/modify',

            # Account management endpoints
            'v1_accounts': '/v1/accounts',
            'api_v1_accounts': '/api/v1/accounts',

            # Information management endpoints
            'v2_information': '/v2/Information',
            'api_v2_information': '/api/v2/INFORMATION',

            # Personal info management
            'v2_personal': '/v2/Personal',
            'v2_personal_caps': '/v2/PERSONAL',
            'api_v2_personal': '/api/v2/PERSONAL',
            'services_personal': '/services/PERSONAL',
            'rest_personal': '/rest/Personal',
            'v1_personal': '/v1/personal',

            # Student management
            'v2_students': '/v2/Students',
            'v2_students_caps': '/v2/STUDENTS',
            'v1_students': '/v1/students',
            'api_v1_students': '/api/v1/Students',
            'api_students': '/api/Students',
            'api_student': '/api/Student',
            'services_student': '/services/STUDENT',

            # Profile management
            'services_profile': '/services/PROFILE',

            # Session management
            'services_session': '/services/SESSION',
            'v2_session': '/v2/session',

            # Token management
            'rest_token': '/rest/Token',
            'v1_token': '/v1/token',
            'v2_token': '/v2/Token',
            'services_token': '/services/token',
            'rest_token_alt': '/rest/token',

            # Email management
            'services_emails': '/services/emails',
            'api_v2_emails': '/api/v2/emails',

            # Edit capabilities
            'v1_edit': '/v1/edit',
            'v2_edit': '/v2/edit',
            'api_v2_edit': '/api/v2/edit',
            'v2_edit_caps': '/v2/Edit',

            # Login management
            'v1_login': '/v1/login',
            'api_v2_login': '/api/v2/login',
            'v2_login': '/api/v2/Login',
            'v2_login_caps': '/v2/LOGIN',

            # Logout management
            'v1_logout': '/v1/LOGOUT',
            'v2_logout': '/v2/logout',
            'v2_logout_caps': '/v2/Logout',

            # User management
            'v2_users': '/v2/Users',

            # Preferences management
            'webapi_preferences': '/webapi/PREFERENCES',
            'api_v1_preferences': '/api/v1/PREFERENCES',
            'api_v2_preferences': '/api/v2/preferences',
        }

    def set_auth_token(self, token: str) -> None:
        """Set authentication token"""
        self._auth_token = token
        self.headers['Authorization'] = f'Bearer {token}'

    def test_admin_access(self) -> Dict[str, Any]:
        """
        Test admin endpoints to see which ones are accessible

        Returns:
            Dictionary with admin access test results
        """
        colored_output.print_header("👑 Testing Admin Access")

        if not self._auth_token:
            colored_output.print_error("❌ Authentication token required")
            return {'error': 'Authentication required'}

        results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'accessible_endpoints': [],
            'forbidden_endpoints': [],
            'unauthorized_endpoints': [],
            'not_found_endpoints': [],
            'error_endpoints': []
        }

        for endpoint_name, endpoint_path in self.admin_endpoints.items():
            colored_output.print_info(f"Testing admin access: {endpoint_name} -> {endpoint_path}")

            try:
                # Try GET first
                response = self.get(endpoint_path)

                endpoint_result = {
                    'name': endpoint_name,
                    'path': endpoint_path,
                    'method': 'GET',
                    'status_code': response.status_code,
                    'response_data': response.data if hasattr(response, 'data') else None
                }

                if response.status_code == 200:
                    results['accessible_endpoints'].append(endpoint_result)
                    colored_output.print_success(f"✅ {endpoint_name} accessible (200)")
                elif response.status_code == 401:
                    results['unauthorized_endpoints'].append(endpoint_result)
                    colored_output.print_warning(f"🔐 {endpoint_name} unauthorized (401)")
                elif response.status_code == 403:
                    results['forbidden_endpoints'].append(endpoint_result)
                    colored_output.print_warning(f"🚫 {endpoint_name} forbidden (403)")
                elif response.status_code == 404:
                    results['not_found_endpoints'].append(endpoint_result)
                elif response.status_code == 405:
                    # Method not allowed - try POST
                    colored_output.print_info(f"GET not allowed for {endpoint_name}, trying POST...")
                    post_response = self.post(endpoint_path, payload={})

                    post_result = {
                        'name': endpoint_name,
                        'path': endpoint_path,
                        'method': 'POST',
                        'status_code': post_response.status_code,
                        'response_data': post_response.data if hasattr(post_response, 'data') else None
                    }

                    if post_response.status_code == 200:
                        results['accessible_endpoints'].append(post_result)
                        colored_output.print_success(f"✅ {endpoint_name} accessible via POST (200)")
                    elif post_response.status_code == 401:
                        results['unauthorized_endpoints'].append(post_result)
                        colored_output.print_warning(f"🔐 {endpoint_name} unauthorized via POST (401)")
                    elif post_response.status_code == 403:
                        results['forbidden_endpoints'].append(post_result)
                        colored_output.print_warning(f"🚫 {endpoint_name} forbidden via POST (403)")
                    else:
                        results['error_endpoints'].append(post_result)
                        colored_output.print_info(f"ℹ️  {endpoint_name} POST returned {post_response.status_code}")
                else:
                    results['error_endpoints'].append(endpoint_result)
                    colored_output.print_info(f"ℹ️  {endpoint_name} returned {response.status_code}")

            except Exception as e:
                error_result = {
                    'name': endpoint_name,
                    'path': endpoint_path,
                    'error': str(e)
                }
                results['error_endpoints'].append(error_result)
                colored_output.print_error(f"❌ Error testing {endpoint_name}: {str(e)}")

        # Summary
        colored_output.print_header("📊 Admin Access Test Summary")
        colored_output.print_success(f"✅ Accessible endpoints: {len(results['accessible_endpoints'])}")
        colored_output.print_warning(f"🚫 Forbidden endpoints: {len(results['forbidden_endpoints'])}")
        colored_output.print_warning(f"🔐 Unauthorized endpoints: {len(results['unauthorized_endpoints'])}")
        colored_output.print_error(f"❌ Not found endpoints: {len(results['not_found_endpoints'])}")
        colored_output.print_info(f"ℹ️  Error endpoints: {len(results['error_endpoints'])}")

        if results['accessible_endpoints']:
            colored_output.print_success("🎉 Accessible admin endpoints found:")
            for result in results['accessible_endpoints']:
                colored_output.print_success(f"  • {result['method']} {result['path']} ({result['status_code']})")

        if results['forbidden_endpoints']:
            colored_output.print_warning("🚫 Forbidden endpoints (may require higher privileges):")
            for result in results['forbidden_endpoints']:
                colored_output.print_warning(f"  • {result['method']} {result['path']} ({result['status_code']})")

        return results

    def try_admin_email_update(self, email: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Try to update email using admin endpoints

        Args:
            email: New email address
            user_id: Optional user ID (if updating another user's email)

        Returns:
            Dictionary with admin update results
        """
        colored_output.print_header("👑 Admin Email Update Attempt")

        if not self._auth_token:
            colored_output.print_error("❌ Authentication token required")
            return {'error': 'Authentication required'}

        results = {
            'email': email,
            'user_id': user_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'attempts': [],
            'successful_updates': [],
            'failed_updates': []
        }

        # Admin endpoints that might allow email updates
        admin_update_endpoints = [
            '/api/Users/Admin',
            '/api/Student/Admin',
            '/api/Students/Admin',
            '/api/v1/Administration',
            '/api/v2/Administration',
            '/api/control',
            '/api/Modify',
            '/api/v2/Modify',
            '/api/Update',
            '/rest/management',
            '/webapi/Management',
        ]

        # Different payload formats to try
        payloads = [
            {'email': email},
            {'Email': email},
            {'emailAddress': email},
            {'EmailAddress': email},
            {'newEmail': email},
            {'NewEmail': email},
        ]

        if user_id:
            for payload in payloads:
                payload['userId'] = user_id
                payload['UserId'] = user_id
                payload['studentId'] = user_id
                payload['StudentId'] = user_id

        for endpoint in admin_update_endpoints:
            colored_output.print_info(f"Trying admin endpoint: {endpoint}")

            for payload in payloads:
                # Try POST
                try:
                    response = self.post(endpoint, payload=payload)

                    attempt = {
                        'endpoint': endpoint,
                        'method': 'POST',
                        'payload': payload,
                        'status_code': response.status_code,
                        'success': response.is_success,
                        'response_data': response.data if hasattr(response, 'data') else None
                    }

                    results['attempts'].append(attempt)

                    if response.is_success:
                        results['successful_updates'].append(attempt)
                        colored_output.print_success(f"✅ Admin email update successful via POST {endpoint}")
                        return results
                    elif response.status_code not in [404, 400, 405]:
                        colored_output.print_warning(f"⚠️  POST {endpoint} returned {response.status_code}")

                except Exception as e:
                    colored_output.print_error(f"❌ Error with POST {endpoint}: {str(e)}")

                # Try PUT
                try:
                    response = self.put(endpoint, payload=payload)

                    attempt = {
                        'endpoint': endpoint,
                        'method': 'PUT',
                        'payload': payload,
                        'status_code': response.status_code,
                        'success': response.is_success,
                        'response_data': response.data if hasattr(response, 'data') else None
                    }

                    results['attempts'].append(attempt)

                    if response.is_success:
                        results['successful_updates'].append(attempt)
                        colored_output.print_success(f"✅ Admin email update successful via PUT {endpoint}")
                        return results
                    elif response.status_code not in [404, 400, 405]:
                        colored_output.print_warning(f"⚠️  PUT {endpoint} returned {response.status_code}")

                except Exception as e:
                    colored_output.print_error(f"❌ Error with PUT {endpoint}: {str(e)}")

        colored_output.print_error("❌ Admin email update failed - no accessible admin endpoints found")
        return results

    def get_admin_capabilities(self) -> Dict[str, Any]:
        """
        Get information about admin capabilities

        Returns:
            Dictionary with admin capabilities information
        """
        colored_output.print_header("🔍 Discovering Admin Capabilities")

        capabilities = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'admin_info': {},
            'management_info': {},
            'system_info': {},
            'user_management': {},
            'errors': []
        }

        # Try to get admin information
        admin_info_endpoints = [
            '/api/Users/Admin',
            '/api/Student/Admin',
            '/api/v1/Administration',
            '/api/v2/Administration',
        ]

        for endpoint in admin_info_endpoints:
            try:
                response = self.get(endpoint)
                if response.is_success and hasattr(response, 'data') and response.data:
                    capabilities['admin_info'][endpoint] = response.data
                    colored_output.print_success(f"✅ Got admin info from {endpoint}")
            except Exception as e:
                capabilities['errors'].append(f"Error getting admin info from {endpoint}: {str(e)}")

        return capabilities