#!/usr/bin/env python3
"""
UMAT Profile Update API
Specialized API client for updating profile information using discovered endpoints
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from api.base_client import BaseAPIClient, APIResponse
from utils.logger import get_logger
from utils.terminal_colors import colored_output

class ProfileUpdateAPI(BaseAPIClient):
    """Specialized API client for profile updates"""

    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        super().__init__(base_url)
        self._auth_token = auth_token
        self.logger = get_logger(self.__class__.__name__)

        # Profile update endpoints discovered
        self.profile_endpoints = {
            # Profile update endpoints
            'profile_update_profile': '/api/Profile/UpdateProfile',
            'users_profile_update': '/api/Users/Profile/Update',
            'students_profile_update': '/api/Students/Profile/Update',
            'profiles_profile_update': '/api/Profiles/Profile/Update',

            # Profile modification endpoints
            'profile_modify_profile': '/api/Profile/Modify/Profile',
            'user_modify_profile': '/api/User/Modify/Profile',
            'users_modify_profile': '/api/Users/modifyprofile',
            'profiles_modify_profile': '/api/Profiles/ModifyProfile',
            'students_modify_profile': '/api/Students/ModifyProfile',
            'student_modify_profile': '/api/Student/ModifyProfile',

            # Profile change endpoints
            'user_profile_change': '/api/User/Profile/Change',
            'student_profile_change': '/api/Student/Profile/Change',

            # Profile edit endpoints
            'student_edit_profile': '/api/Student/Edit/Profile',
            'users_edit_profile': '/api/Users/EditProfile',

            # Profile PUT endpoints
            'users_profile_put': '/api/Users/Profile/Put',
            'profile_put_info': '/api/Profile/Put/Info',
            'profile_put_information': '/api/Profile/Put/Information',
            'profile_put_contactinfo': '/api/Profile/Put/ContactInfo',
            'profile_put_preferences': '/api/Profile/Put/Preferences',

            # Profile PATCH endpoints
            'student_patch_profile': '/api/Student/patchprofile',
            'students_profile_patch': '/api/Students/Profile/Patch',
            'profiles_patch_profile': '/api/Profiles/PatchProfile',
            'profile_patch_profile': '/api/Profile/Patch/Profile',
            'profile_patch_details': '/api/Profile/PatchDetails',
            'profile_patch_info': '/api/Profile/PatchInfo',

            # Profile POST endpoints
            'profile_post_profile': '/api/Profile/PostProfile',
            'profile_post_information': '/api/Profile/Post/Information',
            'users_post_profile': '/api/Users/postprofile',

            # Profile SET endpoints
            'profiles_profile_set': '/api/Profiles/Profile/Set',
            'profiles_set_profile': '/api/Profiles/Set/Profile',
            'profile_set_details': '/api/Profile/Set/Details',

            # Generic profile endpoints
            'api_profiles': '/api/profiles',
            'student_profile': '/api/Student/profile',
            'v1_profile': '/v1/profile',
            'v1_profiles': '/v1/profiles',
            'api_v1_profile': '/api/v1/Profile',
            'api_v1_profile_caps': '/api/v1/PROFILE',
        }

    def set_auth_token(self, token: str) -> None:
        """Set authentication token"""
        self._auth_token = token
        self.headers['Authorization'] = f'Bearer {token}'

    def update_profile_comprehensive(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Try all available profile update endpoints

        Args:
            profile_data: Dictionary containing profile fields to update

        Returns:
            Dictionary with results from all attempted endpoints
        """
        colored_output.print_header("📝 Comprehensive Profile Update")
        colored_output.print_info(f"Attempting to update profile fields: {list(profile_data.keys())}")

        if not self._auth_token:
            colored_output.print_error("❌ Authentication token required")
            return {'error': 'Authentication required'}

        results = {
            'profile_data': profile_data,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'attempts': [],
            'successful_endpoints': [],
            'failed_endpoints': [],
            'error_endpoints': []
        }

        # Try each endpoint with different HTTP methods
        for endpoint_name, endpoint_path in self.profile_endpoints.items():
            colored_output.print_info(f"Testing {endpoint_name}: {endpoint_path}")

            # Try POST method
            post_result = self._try_profile_update_post(endpoint_path, profile_data, endpoint_name)
            results['attempts'].append(post_result)

            # Try PUT method
            put_result = self._try_profile_update_put(endpoint_path, profile_data, endpoint_name)
            results['attempts'].append(put_result)

            # Try PATCH method
            patch_result = self._try_profile_update_patch(endpoint_path, profile_data, endpoint_name)
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
        colored_output.print_header("📊 Profile Update Results Summary")
        colored_output.print_success(f"✅ Successful updates: {len(results['successful_endpoints'])}")
        colored_output.print_warning(f"⚠️  Errors (non-404): {len(results['error_endpoints'])}")
        colored_output.print_error(f"❌ Not found (404): {len(results['failed_endpoints'])}")

        if results['successful_endpoints']:
            colored_output.print_success("🎉 Profile update successful via:")
            for result in results['successful_endpoints']:
                colored_output.print_success(f"  • {result['method']} {result['endpoint']} ({result['status_code']})")

        return results

    def _try_profile_update_post(self, endpoint: str, profile_data: Dict[str, Any], endpoint_name: str) -> Dict[str, Any]:
        """Try POST method for profile update"""
        try:
            response = self.post(endpoint, payload=profile_data)

            result = {
                'endpoint': endpoint,
                'endpoint_name': endpoint_name,
                'method': 'POST',
                'payload': profile_data,
                'status_code': response.status_code,
                'success': response.is_success,
                'response_data': response.data if hasattr(response, 'data') else None,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

            if response.is_success:
                colored_output.print_success(f"✅ POST {endpoint} succeeded")
            elif response.status_code not in [404, 400]:
                colored_output.print_warning(f"⚠️  POST {endpoint} returned {response.status_code}")

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

    def _try_profile_update_put(self, endpoint: str, profile_data: Dict[str, Any], endpoint_name: str) -> Dict[str, Any]:
        """Try PUT method for profile update"""
        try:
            response = self.put(endpoint, payload=profile_data)

            result = {
                'endpoint': endpoint,
                'endpoint_name': endpoint_name,
                'method': 'PUT',
                'payload': profile_data,
                'status_code': response.status_code,
                'success': response.is_success,
                'response_data': response.data if hasattr(response, 'data') else None,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

            if response.is_success:
                colored_output.print_success(f"✅ PUT {endpoint} succeeded")
            elif response.status_code not in [404, 400]:
                colored_output.print_warning(f"⚠️  PUT {endpoint} returned {response.status_code}")

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

    def _try_profile_update_patch(self, endpoint: str, profile_data: Dict[str, Any], endpoint_name: str) -> Dict[str, Any]:
        """Try PATCH method for profile update"""
        try:
            response = self.patch(endpoint, payload=profile_data)

            result = {
                'endpoint': endpoint,
                'endpoint_name': endpoint_name,
                'method': 'PATCH',
                'payload': profile_data,
                'status_code': response.status_code,
                'success': response.is_success,
                'response_data': response.data if hasattr(response, 'data') else None,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

            if response.is_success:
                colored_output.print_success(f"✅ PATCH {endpoint} succeeded")
            elif response.status_code not in [404, 400]:
                colored_output.print_warning(f"⚠️  PATCH {endpoint} returned {response.status_code}")

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

    def test_profile_endpoints(self) -> Dict[str, Any]:
        """
        Test all profile endpoints to see which ones are available

        Returns:
            Dictionary with endpoint availability results
        """
        colored_output.print_header("🧪 Testing Profile Endpoints Availability")

        results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'available_endpoints': [],
            'unavailable_endpoints': [],
            'error_endpoints': []
        }

        for endpoint_name, endpoint_path in self.profile_endpoints.items():
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

        return results