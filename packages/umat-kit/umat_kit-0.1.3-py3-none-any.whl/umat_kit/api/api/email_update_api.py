#!/usr/bin/env python3
"""
UMAT Email Update API
Specialized API client for updating email addresses using discovered endpoints
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from api.base_client import BaseAPIClient, APIResponse
from utils.logger import get_logger
from utils.terminal_colors import colored_output

class EmailUpdateAPI(BaseAPIClient):
    """Specialized API client for email updates"""

    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        super().__init__(base_url)
        self._auth_token = auth_token
        self.logger = get_logger(self.__class__.__name__)

        # Email-specific endpoints discovered
        self.email_endpoints = {
            # Primary email update endpoints
            'account_update_email': '/api/Account/UpdateEmail',
            'user_update_email': '/api/User/UpdateEmail',
            'profile_update_email': '/api/Profile/UpdateEmail',

            # Email change endpoints
            'student_email_change': '/api/Student/Email/Change',
            'user_change_email': '/api/User/Change/Email',
            'student_change_email': '/api/Student/Change/Email',

            # Email modification endpoints
            'user_email_modify': '/api/User/Email/Modify',
            'students_email_modify': '/api/Students/Email/Modify',
            'users_email_modify': '/api/Users/Email/Modify',

            # Email PUT endpoints
            'users_put_email': '/api/Users/PutEmail',
            'profiles_put_email': '/api/Profiles/putemail',

            # Email PATCH endpoints
            'student_email_patch': '/api/Student/Email/Patch',
            'profiles_patch_email': '/api/Profiles/PatchEmail',

            # Email POST endpoints
            'user_post_email': '/api/User/PostEmail',
            'profile_post_email': '/api/Profile/postemail',

            # Email SET endpoints
            'account_email_set': '/api/Account/Email/Set',
            'user_set_email': '/api/User/SetEmail',

            # Email EDIT endpoints
            'profile_email_edit': '/api/Profile/Email/Edit',

            # Generic email endpoints
            'profiles_email': '/api/Profiles/email',
            'student_email': '/api/Student/email',
        }

    def set_auth_token(self, token: str) -> None:
        """Set authentication token"""
        self._auth_token = token
        self.headers['Authorization'] = f'Bearer {token}'

    def update_email_comprehensive(self, email: str) -> Dict[str, Any]:
        """
        Try all available email update endpoints to update email

        Args:
            email: New email address

        Returns:
            Dictionary with results from all attempted endpoints
        """
        colored_output.print_header("📧 Comprehensive Email Update")
        colored_output.print_info(f"Attempting to update email to: {email}")

        if not self._auth_token:
            colored_output.print_error("❌ Authentication token required")
            return {'error': 'Authentication required'}

        results = {
            'email': email,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'attempts': [],
            'successful_endpoints': [],
            'failed_endpoints': [],
            'error_endpoints': []
        }

        # Try each endpoint with different HTTP methods
        for endpoint_name, endpoint_path in self.email_endpoints.items():
            colored_output.print_info(f"Testing {endpoint_name}: {endpoint_path}")

            # Try POST method
            post_result = self._try_email_update_post(endpoint_path, email, endpoint_name)
            results['attempts'].append(post_result)

            # Try PUT method
            put_result = self._try_email_update_put(endpoint_path, email, endpoint_name)
            results['attempts'].append(put_result)

            # Try PATCH method
            patch_result = self._try_email_update_patch(endpoint_path, email, endpoint_name)
            results['attempts'].append(patch_result)

            # Categorize results
            for result in [post_result, put_result, patch_result]:
                if result['success']:
                    results['successful_endpoints'].append(result)
                elif result['status_code'] in [404]:
                    results['failed_endpoints'].append(result)
                else:
                    results['error_endpoints'].append(result)

        # Summary
        colored_output.print_header("📊 Email Update Results Summary")
        colored_output.print_success(f"✅ Successful updates: {len(results['successful_endpoints'])}")
        colored_output.print_warning(f"⚠️  Errors (non-404): {len(results['error_endpoints'])}")
        colored_output.print_error(f"❌ Not found (404): {len(results['failed_endpoints'])}")

        if results['successful_endpoints']:
            colored_output.print_success("🎉 Email update successful via:")
            for result in results['successful_endpoints']:
                colored_output.print_success(f"  • {result['method']} {result['endpoint']} ({result['status_code']})")

        if results['error_endpoints']:
            colored_output.print_warning("⚠️  Endpoints that returned errors:")
            for result in results['error_endpoints']:
                colored_output.print_warning(f"  • {result['method']} {result['endpoint']} ({result['status_code']})")

        return results

    def _try_email_update_post(self, endpoint: str, email: str, endpoint_name: str) -> Dict[str, Any]:
        """Try POST method for email update"""
        try:
            # Try different payload formats
            payloads = [
                {'email': email},
                {'Email': email},
                {'emailAddress': email},
                {'EmailAddress': email},
                {'newEmail': email},
                {'NewEmail': email},
                {'userEmail': email},
                {'UserEmail': email},
                {'contactEmail': email},
                {'ContactEmail': email},
            ]

            for payload in payloads:
                response = self.post(endpoint, payload=payload)

                result = {
                    'endpoint': endpoint,
                    'endpoint_name': endpoint_name,
                    'method': 'POST',
                    'payload': payload,
                    'status_code': response.status_code,
                    'success': response.is_success,
                    'response_data': response.data if hasattr(response, 'data') else None,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }

                if response.is_success:
                    colored_output.print_success(f"✅ POST {endpoint} succeeded with payload: {payload}")
                    return result
                elif response.status_code not in [404, 400]:
                    colored_output.print_warning(f"⚠️  POST {endpoint} returned {response.status_code} with payload: {payload}")
                    return result

            # If all payloads failed, return the last result
            return result

        except Exception as e:
            return {
                'endpoint': endpoint,
                'endpoint_name': endpoint_name,
                'method': 'POST',
                'status_code': 500,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

    def _try_email_update_put(self, endpoint: str, email: str, endpoint_name: str) -> Dict[str, Any]:
        """Try PUT method for email update"""
        try:
            # Try different payload formats
            payloads = [
                {'email': email},
                {'Email': email},
                {'emailAddress': email},
                {'EmailAddress': email},
                {'newEmail': email},
                {'NewEmail': email},
            ]

            for payload in payloads:
                response = self.put(endpoint, payload=payload)

                result = {
                    'endpoint': endpoint,
                    'endpoint_name': endpoint_name,
                    'method': 'PUT',
                    'payload': payload,
                    'status_code': response.status_code,
                    'success': response.is_success,
                    'response_data': response.data if hasattr(response, 'data') else None,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }

                if response.is_success:
                    colored_output.print_success(f"✅ PUT {endpoint} succeeded with payload: {payload}")
                    return result
                elif response.status_code not in [404, 400]:
                    colored_output.print_warning(f"⚠️  PUT {endpoint} returned {response.status_code} with payload: {payload}")
                    return result

            return result

        except Exception as e:
            return {
                'endpoint': endpoint,
                'endpoint_name': endpoint_name,
                'method': 'PUT',
                'status_code': 500,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

    def _try_email_update_patch(self, endpoint: str, email: str, endpoint_name: str) -> Dict[str, Any]:
        """Try PATCH method for email update"""
        try:
            # Try different payload formats
            payloads = [
                {'email': email},
                {'Email': email},
                {'emailAddress': email},
                {'EmailAddress': email},
            ]

            for payload in payloads:
                response = self.patch(endpoint, payload=payload)

                result = {
                    'endpoint': endpoint,
                    'endpoint_name': endpoint_name,
                    'method': 'PATCH',
                    'payload': payload,
                    'status_code': response.status_code,
                    'success': response.is_success,
                    'response_data': response.data if hasattr(response, 'data') else None,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }

                if response.is_success:
                    colored_output.print_success(f"✅ PATCH {endpoint} succeeded with payload: {payload}")
                    return result
                elif response.status_code not in [404, 400]:
                    colored_output.print_warning(f"⚠️  PATCH {endpoint} returned {response.status_code} with payload: {payload}")
                    return result

            return result

        except Exception as e:
            return {
                'endpoint': endpoint,
                'endpoint_name': endpoint_name,
                'method': 'PATCH',
                'status_code': 500,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

    def quick_email_update(self, email: str) -> bool:
        """
        Quick email update using most promising endpoints

        Args:
            email: New email address

        Returns:
            True if successful
        """
        colored_output.print_header("⚡ Quick Email Update")

        # Most promising endpoints based on naming
        priority_endpoints = [
            ('account_update_email', 'POST'),
            ('user_update_email', 'POST'),
            ('profile_update_email', 'POST'),
            ('account_update_email', 'PUT'),
            ('user_update_email', 'PUT'),
            ('student_email_change', 'POST'),
            ('user_change_email', 'POST'),
        ]

        for endpoint_name, method in priority_endpoints:
            if endpoint_name in self.email_endpoints:
                endpoint_path = self.email_endpoints[endpoint_name]
                colored_output.print_info(f"Trying {method} {endpoint_path}")

                try:
                    if method == 'POST':
                        response = self.post(endpoint_path, payload={'email': email})
                    elif method == 'PUT':
                        response = self.put(endpoint_path, payload={'email': email})
                    elif method == 'PATCH':
                        response = self.patch(endpoint_path, payload={'email': email})
                    else:
                        continue

                    if response.is_success:
                        colored_output.print_success(f"✅ Email updated successfully via {method} {endpoint_path}")
                        return True
                    elif response.status_code not in [404, 400]:
                        colored_output.print_warning(f"⚠️  {method} {endpoint_path} returned {response.status_code}")

                except Exception as e:
                    colored_output.print_error(f"❌ Error with {method} {endpoint_path}: {str(e)}")

        colored_output.print_error("❌ Quick email update failed - try comprehensive update")
        return False

    def test_email_endpoints(self) -> Dict[str, Any]:
        """
        Test all email endpoints to see which ones are available

        Returns:
            Dictionary with endpoint availability results
        """
        colored_output.print_header("🧪 Testing Email Endpoints Availability")

        results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'available_endpoints': [],
            'unavailable_endpoints': [],
            'error_endpoints': []
        }

        for endpoint_name, endpoint_path in self.email_endpoints.items():
            colored_output.print_info(f"Testing {endpoint_name}: {endpoint_path}")

            try:
                # Try GET first to see if endpoint exists
                response = self.get(endpoint_path)

                endpoint_result = {
                    'name': endpoint_name,
                    'path': endpoint_path,
                    'status_code': response.status_code,
                    'available': response.status_code not in [404]
                }

                if response.status_code == 404:
                    results['unavailable_endpoints'].append(endpoint_result)
                    colored_output.print_error(f"❌ {endpoint_name} not found (404)")
                elif response.status_code in [200, 401, 403, 405]:
                    results['available_endpoints'].append(endpoint_result)
                    colored_output.print_success(f"✅ {endpoint_name} available ({response.status_code})")
                else:
                    results['error_endpoints'].append(endpoint_result)
                    colored_output.print_warning(f"⚠️  {endpoint_name} returned {response.status_code}")

            except Exception as e:
                endpoint_result = {
                    'name': endpoint_name,
                    'path': endpoint_path,
                    'error': str(e),
                    'available': False
                }
                results['error_endpoints'].append(endpoint_result)
                colored_output.print_error(f"❌ Error testing {endpoint_name}: {str(e)}")

        # Summary
        colored_output.print_header("📊 Email Endpoints Test Summary")
        colored_output.print_success(f"✅ Available endpoints: {len(results['available_endpoints'])}")
        colored_output.print_error(f"❌ Unavailable endpoints: {len(results['unavailable_endpoints'])}")
        colored_output.print_warning(f"⚠️  Error endpoints: {len(results['error_endpoints'])}")

        return results