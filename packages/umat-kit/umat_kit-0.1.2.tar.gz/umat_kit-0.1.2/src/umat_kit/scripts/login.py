#!/usr/bin/env python3
"""
Advanced UMAT Login Testing Application
Comprehensive authentication testing with terminal interface
"""

import sys
import os
import argparse
from typing import Optional

# Package-aware imports
from ..api.api import LoginAPI, APIManager
from ..utils.utils.terminal_colors import colored_output, terminal_colors
from ..utils.utils.logger import setup_logger, get_logger
from ..config import config, config_manager

class LoginTester:
    """Advanced login testing application"""

    def __init__(self):
        self.logger = setup_logger('LoginTester')
        self.login_api = LoginAPI()
        self.api_manager = APIManager()

        # Display startup banner
        self._display_banner()

    def _display_banner(self) -> None:
        """Display application banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    UMAT LOGIN TESTER                         ║
║              Advanced Authentication Testing                 ║
║                                                              ║
║  🔐 Comprehensive login flow testing                        ║
║  🧪 Token validation and management                         ║
║  📊 Performance monitoring                                   ║
║  🎨 Rich terminal interface                                  ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(terminal_colors.highlight(banner))
        colored_output.print_info(f"Base URL: {config.api.base_url}")
        colored_output.print_separator()

    def interactive_login(self) -> None:
        """Interactive login process"""
        colored_output.print_header("🔐 Interactive Login")

        try:
            # Always prompt for credentials (do not use .env)
            username = input(terminal_colors.info("Enter username (student number): ")).strip()
            if not username:
                colored_output.print_error("Username cannot be empty")
                return

            password = input(terminal_colors.info("Enter password: ")).strip()
            if not password:
                colored_output.print_error("Password cannot be empty")
                return

            # Perform login
            colored_output.print_info("Attempting login...")
            response = self.login_api.login(username, password)

            if response.is_success:
                colored_output.print_success("Login successful!")

                # Display session information
                self.login_api.print_session_info()

                # Ask if user wants to test other operations
                self._post_login_menu()
            else:
                colored_output.print_error("Login failed!")
                if response.data:
                    colored_output.print_json(response.data, "Error Details")

        except KeyboardInterrupt:
            colored_output.print_warning("\nOperation cancelled by user")
        except Exception as e:
            colored_output.print_error(f"Login error: {str(e)}")
            self.logger.error(f"Interactive login error: {str(e)}")

    def test_login_credentials(self, username: str, password: str) -> bool:
        """Test specific login credentials"""
        colored_output.print_header("🧪 Login Credentials Test", f"Testing: {username}")

        try:
            response = self.login_api.login(username, password, validate_credentials=True)

            if response.is_success:
                colored_output.print_success("✅ Login test passed")

                # Display token information
                if response.data and 'token' in response.data:
                    token_validation = self.login_api.validate_current_token()
                    colored_output.print_info(f"Token validation: {token_validation}")

                # Test logout
                colored_output.print_info("Testing logout...")
                logout_response = self.login_api.logout()

                if logout_response.is_success:
                    colored_output.print_success("✅ Logout test passed")
                else:
                    colored_output.print_warning("⚠️ Logout test failed")

                return True
            else:
                colored_output.print_error("❌ Login test failed")
                return False

        except Exception as e:
            colored_output.print_error(f"Test error: {str(e)}")
            self.logger.error(f"Login test error: {str(e)}")
            return False

    def run_comprehensive_login_test(self, username: str, password: str) -> None:
        """Run comprehensive login testing suite"""
        colored_output.print_header("🔬 Comprehensive Login Test Suite")

        try:
            # Run the comprehensive test
            test_results = self.login_api.test_authentication_flow(username, password)

            # Display detailed results
            colored_output.print_separator()
            colored_output.print_header("📊 Test Results Analysis")

            # Analyze results
            if test_results.get('overall_success'):
                colored_output.print_success("🎉 All login tests passed!")
            else:
                colored_output.print_error("❌ Some login tests failed")

            # Display performance metrics
            login_test = test_results.get('login_test', {})
            if login_test:
                response_time = login_test.get('response_time', 0)
                if response_time > 0:
                    if response_time < 1.0:
                        colored_output.print_success(f"⚡ Fast response time: {response_time:.3f}s")
                    elif response_time < 3.0:
                        colored_output.print_info(f"⏱️ Normal response time: {response_time:.3f}s")
                    else:
                        colored_output.print_warning(f"🐌 Slow response time: {response_time:.3f}s")

            # Show request history
            colored_output.print_info("\n📈 Request History:")
            self.login_api.print_history_summary()

        except Exception as e:
            colored_output.print_error(f"Comprehensive test error: {str(e)}")
            self.logger.error(f"Comprehensive login test error: {str(e)}")

    def _post_login_menu(self) -> None:
        """Display post-login menu options"""
        colored_output.print_header("🎯 Post-Login Options")

        options = [
            "1. View session information",
            "2. Test token validation",
            "3. Test token refresh",
            "4. View request history",
            "5. Test user info endpoints",
            "6. Logout",
            "7. Exit"
        ]

        for option in options:
            colored_output.print_info(f"  {option}")

        while True:
            try:
                choice = input(terminal_colors.info("\nSelect option (1-7): ")).strip()

                if choice == '1':
                    self.login_api.print_session_info()
                elif choice == '2':
                    validation_result = self.login_api.validate_current_token()
                    colored_output.print_info(f"Token validation: {validation_result}")
                elif choice == '3':
                    colored_output.print_info("Testing token refresh...")
                    refresh_response = self.login_api.refresh_token()
                    if refresh_response.is_success:
                        colored_output.print_success("Token refreshed successfully")
                    else:
                        colored_output.print_error("Token refresh failed")
                elif choice == '4':
                    self.login_api.print_history_summary()
                elif choice == '5':
                    self._test_user_info_integration()
                elif choice == '6':
                    self.login_api.logout()
                    colored_output.print_success("Logged out successfully")
                    break
                elif choice == '7':
                    colored_output.print_info("Exiting...")
                    break
                else:
                    colored_output.print_warning("Invalid option. Please select 1-7.")

            except KeyboardInterrupt:
                colored_output.print_warning("\nOperation cancelled")
                break
            except Exception as e:
                colored_output.print_error(f"Menu error: {str(e)}")

    def _test_user_info_integration(self) -> None:
        """Test integration with user info endpoints"""
        colored_output.print_info("Testing user info integration...")

        try:
            # Share token with API manager
            if self.login_api._auth_token:
                self.api_manager.userinfo_api.set_auth_token(self.login_api._auth_token)

                # Test user info retrieval
                profile = self.api_manager.get_complete_user_profile()

                if profile.get('consolidated_data'):
                    colored_output.print_success("✅ User info integration successful")
                else:
                    colored_output.print_warning("⚠️ User info integration failed")
            else:
                colored_output.print_error("No authentication token available")

        except Exception as e:
            colored_output.print_error(f"Integration test error: {str(e)}")

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="Advanced UMAT Login Testing Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python login.py                           # Interactive mode
  python login.py -u 9012562822 -p password # Direct login test
  python login.py -u 9012562822 -p password --comprehensive # Full test suite
        """
    )

    parser.add_argument('-u', '--username', help='Username (student number)')
    parser.add_argument('-p', '--password', help='Password')
    parser.add_argument('--comprehensive', action='store_true',
                       help='Run comprehensive test suite')
    parser.add_argument('--test-only', action='store_true',
                       help='Test credentials without interactive session')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')

    args = parser.parse_args()

    # Configure logging level
    if args.debug:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
        colored_output.print_info("Debug logging enabled")

    # Validate configuration
    if not config_manager.validate_config():
        colored_output.print_error("Configuration validation failed")
        sys.exit(1)

    # Initialize login tester
    login_tester = LoginTester()

    try:
        # Determine credentials: CLI args preferred; otherwise, interactive prompt
        username = args.username
        password = args.password

        if username and password:
            # Direct credential testing
            if args.comprehensive:
                login_tester.run_comprehensive_login_test(username, password)
            elif args.test_only:
                success = login_tester.test_login_credentials(username, password)
                sys.exit(0 if success else 1)
            else:
                # Login and enter interactive mode
                response = login_tester.login_api.login(username, password)
                if response.is_success:
                    login_tester._post_login_menu()
                else:
                    colored_output.print_error("Login failed")
                    sys.exit(1)
        else:
            # Interactive mode (prompts inside)
            login_tester.interactive_login()

    except KeyboardInterrupt:
        colored_output.print_warning("\nApplication terminated by user")
    except Exception as e:
        colored_output.print_error(f"Application error: {str(e)}")
        sys.exit(1)

    colored_output.print_info("Application finished")

if __name__ == "__main__":
    main()