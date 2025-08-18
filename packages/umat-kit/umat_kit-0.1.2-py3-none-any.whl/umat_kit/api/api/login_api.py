"""
Advanced Login API Client for UMAT Student Portal
Handles authentication, token management, and login-related operations
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta, timezone

from .base_client import BaseAPIClient, APIResponse
from ...utils.utils.logger import get_logger
from ...utils.utils.validators import data_validator, ValidationResult
from ...utils.utils.crypto import JWTManager
from ...utils.utils.terminal_colors import colored_output
from ...config import config

class LoginAPI(BaseAPIClient):
    """Advanced login API client with comprehensive authentication features"""

    def __init__(self, base_url: Optional[str] = None):
        super().__init__(base_url)
        self.logger = get_logger(self.__class__.__name__)
        self.jwt_manager = JWTManager(config.security.jwt_secret) if config.security.jwt_secret else None

        # Login endpoints (logout endpoint not available in UMAT API)
        self.endpoints = {
            'login': '/api/UserAccount/login',
            'refresh': '/api/UserAccount/refresh',
            'validate': '/api/UserAccount/validate'
        }

        # Current session info
        self.current_user: Optional[Dict[str, Any]] = None
        self.login_time: Optional[datetime] = None
        self.token_expires_at: Optional[datetime] = None

    def login(self, username: str, password: str,
              validate_credentials: bool = True) -> APIResponse:
        """
        Authenticate user with username and password

        Args:
            username: Student number or username
            password: User password
            validate_credentials: Whether to validate input format

        Returns:
            APIResponse with authentication token
        """
        colored_output.print_header("🔐 User Authentication", f"Logging in user: {username}")

        # Validate input if requested
        if validate_credentials:
            login_data = {'username': username, 'password': password}
            validation_result = data_validator.validate_login_data(login_data)

            if not validation_result.is_valid:
                colored_output.print_error("Login validation failed", str(validation_result))
                # Create failed response
                response = APIResponse(
                    status_code=400,
                    headers={},
                    data={'error': 'Validation failed', 'details': validation_result.errors},
                    request_method='POST',
                    request_url=self._build_url(self.endpoints['login'])
                )
                response.validation_result = validation_result
                return response

        # Prepare login payload
        payload = {
            'username': username,
            'password': password
        }

        # Make login request
        response = self.post(
            self.endpoints['login'],
            payload=payload,
            expected_fields=['token']
        )

        # Process successful login
        if response.is_success and response.data and 'token' in response.data:
            token = response.data['token']

            # Validate token format
            token_validation = data_validator.validate_jwt_token(token)
            if not token_validation.is_valid:
                colored_output.print_warning("Token validation issues", str(token_validation))

            # Set authentication token
            self.set_auth_token(token)

            # Extract user info from token if possible
            if self.jwt_manager:
                try:
                    token_info = self.jwt_manager.get_token_info(token)
                    self.current_user = token_info['payload']
                    self.token_expires_at = token_info.get('expires_at')

                    colored_output.print_success(
                        "Login successful",
                        f"Token expires: {self.token_expires_at}"
                    )
                except Exception as e:
                    self.logger.warning(f"Could not parse token info: {str(e)}")

            self.login_time = datetime.now()

            # Log successful authentication
            self.logger.info(f"User {username} authenticated successfully")
            colored_output.print_success(f"✅ Authentication successful for {username}")

        else:
            # Handle different types of authentication failures with user-friendly messages
            if response.error_message:
                colored_output.print_error(f"❌ {response.error_message}")
            elif response.status_code == 401:
                colored_output.print_error("❌ Invalid username or password")
                colored_output.print_info("💡 Please check your student number and password")
            elif response.status_code == 502:
                colored_output.print_error("❌ Server is temporarily unavailable")
                colored_output.print_info("💡 The UMAT portal appears to be down. Please try again in a few minutes.")
            elif response.status_code == 503:
                colored_output.print_error("❌ Service temporarily unavailable")
                colored_output.print_info("💡 The server is experiencing high traffic. Please try again later.")
            elif response.status_code >= 500:
                colored_output.print_error("❌ Server error occurred")
                colored_output.print_info("💡 There's an issue with the UMAT server. Please try again later.")
            else:
                error_msg = response.data.get('message', 'Unknown error') if response.data else 'No response data'
                colored_output.print_error(f"❌ Authentication failed for {username}")
                colored_output.print_error(f"   {error_msg}")

            self.logger.error(f"Authentication failed for {username}: {response.status_code} - {response.error_message or 'Unknown error'}")

        return response

    def logout(self) -> APIResponse:
        """
        Logout current user and clear session (local only - UMAT API has no logout endpoint)

        Returns:
            APIResponse confirming logout
        """
        colored_output.print_header("🚪 User Logout")

        if not self._auth_token:
            colored_output.print_warning("No active session to logout")
            return APIResponse(
                status_code=400,
                headers={},
                data={'error': 'No active session'},
                request_method='LOCAL',
                request_url='local://logout'
            )

        # Clear session data locally (UMAT API doesn't have a logout endpoint)
        self._clear_session()

        # Create a successful response for local logout
        response = APIResponse(
            status_code=200,
            headers={},
            data={'message': 'Logged out successfully (local session cleared)'},
            request_method='LOCAL',
            request_url='local://logout'
        )

        colored_output.print_success("✅ Logout successful - session cleared locally")
        self.logger.info("User logged out successfully (local session cleared)")

        return response

    def refresh_token(self) -> APIResponse:
        """
        Refresh the current authentication token

        Returns:
            APIResponse with new token
        """
        colored_output.print_header("🔄 Token Refresh")

        if not self._auth_token:
            colored_output.print_error("No token to refresh")
            return APIResponse(
                status_code=401,
                headers={},
                data={'error': 'No active token'},
                request_method='POST',
                request_url=self._build_url(self.endpoints['refresh'])
            )

        # Make refresh request
        response = self.post(
            self.endpoints['refresh'],
            expected_fields=['token']
        )

        # Process successful refresh
        if response.is_success and response.data and 'token' in response.data:
            new_token = response.data['token']
            self.set_auth_token(new_token)

            # Update token expiration info
            if self.jwt_manager:
                try:
                    token_info = self.jwt_manager.get_token_info(new_token)
                    self.token_expires_at = token_info.get('expires_at')
                    colored_output.print_success(
                        "Token refreshed successfully",
                        f"New expiration: {self.token_expires_at}"
                    )
                except Exception as e:
                    self.logger.warning(f"Could not parse new token info: {str(e)}")

            self.logger.info("Authentication token refreshed successfully")
        else:
            colored_output.print_error("Token refresh failed")
            self.logger.error("Token refresh failed")

        return response

    def validate_current_token(self) -> ValidationResult:
        """
        Validate the current authentication token

        Returns:
            ValidationResult with token status
        """
        if not self._auth_token:
            result = ValidationResult(False)
            result.add_error("No authentication token available")
            return result

        return data_validator.validate_jwt_token(self._auth_token)

    def is_token_expired(self) -> bool:
        """
        Check if current token is expired

        Returns:
            True if token is expired or about to expire
        """
        if not self.token_expires_at:
            return False

        # Consider token expired if it expires within 5 minutes
        buffer_time = timedelta(minutes=5)
        return datetime.now(timezone.utc) < (self.token_expires_at - buffer_time)

    def get_session_info(self) -> Dict[str, Any]:
        """
        Get current session information

        Returns:
            Dictionary with session details
        """
        session_info = {
            'is_authenticated': bool(self._auth_token),
            'login_time': self.login_time.isoformat() if self.login_time else None,
            'token_expires_at': self.token_expires_at.isoformat() if self.token_expires_at else None,
            'current_user': self.current_user,
            'token_valid': self.validate_current_token().is_valid if self._auth_token else False
        }

        if self.token_expires_at:
            time_until_expiry = self.token_expires_at - datetime.now(timezone.utc)
            session_info['time_until_expiry'] = str(time_until_expiry)
            session_info['is_token_expired'] = time_until_expiry.total_seconds() <= 0

        return session_info

    def print_session_info(self) -> None:
        """Print current session information to terminal"""
        session_info = self.get_session_info()

        colored_output.print_header("🔐 Session Information")

        if session_info['is_authenticated']:
            colored_output.print_success("Status: Authenticated")

            if session_info['login_time']:
                colored_output.print_info(f"Login Time: {session_info['login_time']}")

            if session_info['token_expires_at']:
                colored_output.print_info(f"Token Expires: {session_info['token_expires_at']}")

                if session_info.get('time_until_expiry'):
                    if session_info.get('is_token_expired'):
                        colored_output.print_error(f"Token Status: EXPIRED")
                    else:
                        colored_output.print_success(f"Time Until Expiry: {session_info['time_until_expiry']}")

            if session_info['current_user']:
                colored_output.print_json(session_info['current_user'], "User Information")
        else:
            colored_output.print_warning("Status: Not Authenticated")

    def auto_refresh_if_needed(self) -> bool:
        """
        Automatically refresh token if it's about to expire

        Returns:
            True if refresh was successful or not needed, False if failed
        """
        if not self._auth_token:
            return False

        if self.is_token_expired():
            colored_output.print_info("Token expiring soon, attempting auto-refresh...")
            response = self.refresh_token()
            return response.is_success

        return True

    def _clear_session(self) -> None:
        """Clear all session data"""
        self.clear_auth_token()
        self.current_user = None
        self.login_time = None
        self.token_expires_at = None
        self.logger.info("Session data cleared")

    def test_authentication_flow(self, username: str, password: str) -> Dict[str, Any]:
        """
        Test complete authentication flow

        Args:
            username: Test username
            password: Test password

        Returns:
            Dictionary with test results
        """
        colored_output.print_header("🧪 Authentication Flow Test", f"Testing with user: {username}")

        test_results = {
            'login_test': None,
            'token_validation_test': None,
            'session_info_test': None,
            'logout_test': None,
            'overall_success': False
        }

        try:
            # Test login
            colored_output.print_info("Step 1: Testing login...")
            login_response = self.login(username, password)
            test_results['login_test'] = {
                'success': login_response.is_success,
                'status_code': login_response.status_code,
                'response_time': login_response.response_time,
                'has_token': bool(login_response.data and 'token' in login_response.data)
            }

            if login_response.is_success:
                # Test token validation
                colored_output.print_info("Step 2: Testing token validation...")
                token_validation = self.validate_current_token()
                test_results['token_validation_test'] = {
                    'is_valid': token_validation.is_valid,
                    'errors': token_validation.errors,
                    'warnings': token_validation.warnings
                }

                # Test session info
                colored_output.print_info("Step 3: Testing session info...")
                session_info = self.get_session_info()
                test_results['session_info_test'] = {
                    'has_session_info': bool(session_info),
                    'is_authenticated': session_info.get('is_authenticated', False),
                    'has_user_data': bool(session_info.get('current_user'))
                }

                # Test logout
                colored_output.print_info("Step 4: Testing logout...")
                logout_response = self.logout()
                test_results['logout_test'] = {
                    'success': logout_response.is_success,
                    'status_code': logout_response.status_code,
                    'session_cleared': not bool(self._auth_token)
                }

                test_results['overall_success'] = all([
                    test_results['login_test']['success'],
                    test_results['token_validation_test']['is_valid'],
                    test_results['session_info_test']['is_authenticated']
                ])

        except Exception as e:
            colored_output.print_error(f"Authentication flow test failed: {str(e)}")
            test_results['error'] = str(e)

        # Print test summary
        if test_results['overall_success']:
            colored_output.print_success("🎉 Authentication flow test completed successfully!")
        else:
            colored_output.print_error("❌ Authentication flow test failed")

        colored_output.print_json(test_results, "Test Results")

        return test_results