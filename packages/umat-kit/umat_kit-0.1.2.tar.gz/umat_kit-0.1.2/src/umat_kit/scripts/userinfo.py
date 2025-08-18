#!/usr/bin/env python3
"""
Advanced UMAT User Information Testing Application
Comprehensive user data retrieval and validation with terminal interface
"""

import sys
import os
import argparse
from typing import Optional, Dict, Any

# Package-aware imports
from ..api.api import UserInfoAPI, LoginAPI, APIManager
from ..utils.utils.terminal_colors import colored_output, terminal_colors
from ..utils.utils.logger import setup_logger, get_logger
from ..config import config, config_manager

class UserInfoTester:
    """Advanced user information testing application"""

    def __init__(self):
        self.logger = setup_logger('UserInfoTester')
        self.login_api = LoginAPI()
        self.userinfo_api = UserInfoAPI()
        self.api_manager = APIManager()

        # Display startup banner
        self._display_banner()

    def _display_banner(self) -> None:
        """Display application banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                 UMAT USER INFO TESTER                        ║
║            Advanced User Data Testing & Validation          ║
║                                                              ║
║  👤 Comprehensive user profile retrieval                   ║
║  🔍 Data validation and integrity checks                   ║
║  📊 Multi-endpoint testing                                  ║
║  🎨 Rich data visualization                                 ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(terminal_colors.highlight(banner))
        colored_output.print_info(f"Base URL: {config.api.base_url}")
        colored_output.print_separator()

    def authenticate_user(self, username: Optional[str] = None,
                         password: Optional[str] = None) -> bool:
        """Authenticate user for API access"""
        colored_output.print_header("🔐 User Authentication Required")

        try:
            # Always prompt for credentials when not provided
            if not username:
                username = input(terminal_colors.info("Enter username (student number): ")).strip()
            if not password:
                password = input(terminal_colors.info("Enter password: ")).strip()

            if not username or not password:
                colored_output.print_error("Username and password are required")
                return False

            # Authenticate using API manager
            success = self.api_manager.authenticate(username, password)

            if success:
                # Share token with userinfo API
                if self.api_manager.login_api._auth_token:
                    self.userinfo_api.set_auth_token(self.api_manager.login_api._auth_token)
                colored_output.print_success("✅ Authentication successful")
                return True
            else:
                colored_output.print_error("❌ Authentication failed")
                return False

        except KeyboardInterrupt:
            colored_output.print_warning("\nAuthentication cancelled by user")
            return False
        except Exception as e:
            colored_output.print_error(f"Authentication error: {str(e)}")
            self.logger.error(f"Authentication error: {str(e)}")
            return False

    def get_student_portal_info(self, validate_data: bool = True) -> Optional[Dict[str, Any]]:
        """Get student portal information"""
        colored_output.print_header("👤 Student Portal Information")

        try:
            response = self.userinfo_api.get_student_portal_info(
                use_cache=False,
                validate_data=validate_data
            )

            if response.is_success:
                colored_output.print_success("✅ Student information retrieved successfully")

                # Display performance metrics
                colored_output.print_info(f"Response time: {response.response_time:.3f}s")

                # Display validation results
                if response.validation_result:
                    if response.validation_result.is_valid:
                        colored_output.print_success("✅ Data validation passed")
                    else:
                        colored_output.print_warning("⚠️ Data validation issues found")
                        for error in response.validation_result.errors:
                            colored_output.print_error(f"  • {error}")
                        for warning in response.validation_result.warnings:
                            colored_output.print_warning(f"  • {warning}")

                return response.data
            else:
                colored_output.print_error("❌ Failed to retrieve student information")
                if response.data:
                    colored_output.print_json(response.data, "Error Details")
                return None

        except Exception as e:
            colored_output.print_error(f"Error retrieving student info: {str(e)}")
            self.logger.error(f"Student info retrieval error: {str(e)}")
            return None

    def get_complete_user_profile(self, validate_data: bool = True) -> Optional[Dict[str, Any]]:
        """Get complete user profile from all endpoints"""
        colored_output.print_header("🔍 Complete User Profile Retrieval")

        try:
            profile = self.api_manager.get_complete_user_profile(validate_data=validate_data)

            if profile.get('consolidated_data'):
                colored_output.print_success("✅ Complete profile retrieved successfully")

                # Display data sources summary
                data_sources = profile.get('data_sources', {})
                successful_sources = [name for name, info in data_sources.items() if info.get('success')]
                failed_sources = [name for name, info in data_sources.items() if not info.get('success')]

                colored_output.print_info(f"Successful endpoints: {len(successful_sources)}")
                colored_output.print_info(f"Failed endpoints: {len(failed_sources)}")

                if failed_sources:
                    colored_output.print_warning(f"Failed endpoints: {', '.join(failed_sources)}")

                # Display validation summary
                validation_results = profile.get('validation_results', {})
                valid_endpoints = [name for name, result in validation_results.items() if result.get('is_valid')]
                invalid_endpoints = [name for name, result in validation_results.items() if not result.get('is_valid')]

                if validation_results:
                    colored_output.print_info(f"Valid data endpoints: {len(valid_endpoints)}")
                    if invalid_endpoints:
                        colored_output.print_warning(f"Invalid data endpoints: {len(invalid_endpoints)}")

                return profile
            else:
                colored_output.print_error("❌ Failed to retrieve complete profile")
                return None

        except Exception as e:
            colored_output.print_error(f"Error retrieving complete profile: {str(e)}")
            self.logger.error(f"Complete profile retrieval error: {str(e)}")
            return None

    def test_all_endpoints(self) -> Dict[str, Any]:
        """Test all user information endpoints"""
        colored_output.print_header("🧪 User Info Endpoints Testing")

        try:
            test_results = self.userinfo_api.test_user_info_endpoints()

            # Display test summary
            colored_output.print_separator()
            colored_output.print_header("📊 Test Results Summary")

            if test_results.get('overall_success'):
                colored_output.print_success("🎉 All endpoint tests passed!")
            else:
                colored_output.print_error("❌ Some endpoint tests failed")

            # Display endpoint-specific results
            endpoint_results = test_results.get('endpoint_results', {})
            for endpoint_name, result in endpoint_results.items():
                if result.get('success'):
                    response_time = result.get('response_time', 0)
                    colored_output.print_success(f"✅ {endpoint_name}: {response_time:.3f}s")
                else:
                    colored_output.print_error(f"❌ {endpoint_name}: Failed")
                    if 'error' in result:
                        colored_output.print_error(f"   Error: {result['error']}")

            # Display performance analysis
            self._analyze_performance(endpoint_results)

            return test_results

        except Exception as e:
            colored_output.print_error(f"Endpoint testing error: {str(e)}")
            self.logger.error(f"Endpoint testing error: {str(e)}")
            return {'error': str(e)}

    def interactive_mode(self) -> None:
        """Interactive user information exploration"""
        colored_output.print_header("🎯 Interactive User Info Mode")

        # First authenticate
        if not self.authenticate_user():
            return

        # Main menu loop
        while True:
            self._display_menu()

            try:
                choice = input(terminal_colors.info("\nSelect option (1-8): ")).strip()

                if choice == '1':
                    self.get_student_portal_info()
                elif choice == '2':
                    self.get_complete_user_profile()
                elif choice == '3':
                    self.test_all_endpoints()
                elif choice == '4':
                    self._display_cached_data()
                elif choice == '5':
                    self._validate_cached_data()
                elif choice == '6':
                    self._compare_data_sources()
                elif choice == '7':
                    self._display_api_statistics()
                elif choice == '8':
                    colored_output.print_info("Exiting interactive mode...")
                    break
                else:
                    colored_output.print_warning("Invalid option. Please select 1-8.")

                # Pause for user to read results
                if choice in ['1', '2', '3', '4', '5', '6', '7']:
                    input(terminal_colors.info("\nPress Enter to continue..."))

            except KeyboardInterrupt:
                colored_output.print_warning("\nOperation cancelled")
                break
            except Exception as e:
                colored_output.print_error(f"Menu error: {str(e)}")

    def _display_menu(self) -> None:
        """Display interactive menu options"""
        colored_output.print_separator()
        colored_output.print_header("📋 User Info Options")

        options = [
            "1. Get student portal information",
            "2. Get complete user profile",
            "3. Test all endpoints",
            "4. Display cached data",
            "5. Validate cached data",
            "6. Compare data sources",
            "7. Display API statistics",
            "8. Exit"
        ]

        for option in options:
            colored_output.print_info(f"  {option}")

    def _display_cached_data(self) -> None:
        """Display cached user data"""
        colored_output.print_header("💾 Cached User Data")

        if self.userinfo_api.cached_user_data:
            colored_output.print_json(self.userinfo_api.cached_user_data, "Cached Data")

            # Display cache info
            if self.userinfo_api.cache_timestamp:
                cache_age = (self.userinfo_api.cache_timestamp -
                           self.userinfo_api.cache_timestamp).total_seconds()
                colored_output.print_info(f"Cache age: {cache_age:.1f} seconds")
        else:
            colored_output.print_warning("No cached data available")

    def _validate_cached_data(self) -> None:
        """Validate cached user data"""
        colored_output.print_header("✅ Data Validation")

        if self.userinfo_api.cached_user_data:
            validation_result = self.userinfo_api.validate_user_data()

            if validation_result.is_valid:
                colored_output.print_success("✅ Cached data validation passed")
            else:
                colored_output.print_error("❌ Cached data validation failed")
                for error in validation_result.errors:
                    colored_output.print_error(f"  • {error}")
                for warning in validation_result.warnings:
                    colored_output.print_warning(f"  • {warning}")
        else:
            colored_output.print_warning("No cached data to validate")

    def _compare_data_sources(self) -> None:
        """Compare data from different sources"""
        colored_output.print_header("🔍 Data Source Comparison")

        # This would require multiple data sources to compare
        # For now, just show the concept
        colored_output.print_info("Data comparison feature - would compare multiple endpoint responses")
        colored_output.print_info("This helps identify inconsistencies between different API endpoints")

    def _display_api_statistics(self) -> None:
        """Display API usage statistics"""
        colored_output.print_header("📊 API Usage Statistics")

        stats = self.api_manager.get_api_statistics()
        colored_output.print_json(stats, "API Statistics")

    def _analyze_performance(self, endpoint_results: Dict[str, Any]) -> None:
        """Analyze endpoint performance"""
        colored_output.print_header("⚡ Performance Analysis")

        response_times = []
        for endpoint_name, result in endpoint_results.items():
            if result.get('success') and 'response_time' in result:
                response_times.append((endpoint_name, result['response_time']))

        if response_times:
            # Sort by response time
            response_times.sort(key=lambda x: x[1])

            colored_output.print_info("Endpoint performance ranking (fastest to slowest):")
            for i, (endpoint, time) in enumerate(response_times, 1):
                if time < 1.0:
                    status = terminal_colors.success("⚡ Fast")
                elif time < 3.0:
                    status = terminal_colors.info("⏱️ Normal")
                else:
                    status = terminal_colors.warning("🐌 Slow")

                colored_output.print_info(f"  {i}. {endpoint}: {time:.3f}s {status}")

            # Calculate average
            avg_time = sum(time for _, time in response_times) / len(response_times)
            colored_output.print_info(f"Average response time: {avg_time:.3f}s")

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="Advanced UMAT User Information Testing Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python userinfo.py                                    # Interactive mode
  python userinfo.py -u 9012562822 -p password        # Get user info
  python userinfo.py -u 9012562822 -p password --test # Test all endpoints
  python userinfo.py -u 9012562822 -p password --complete # Get complete profile
        """
    )

    parser.add_argument('-u', '--username', help='Username (student number)')
    parser.add_argument('-p', '--password', help='Password')
    parser.add_argument('--test', action='store_true',
                       help='Test all user info endpoints')
    parser.add_argument('--complete', action='store_true',
                       help='Get complete user profile')
    parser.add_argument('--no-validation', action='store_true',
                       help='Skip data validation')
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

    # Initialize user info tester
    userinfo_tester = UserInfoTester()

    try:
        # Use config credentials as fallback
        username = args.username or config.test.username
        password = args.password or config.test.password

        if username and password:
            # Authenticate first
            if not userinfo_tester.authenticate_user(username, password):
                sys.exit(1)

            validate_data = not args.no_validation

            if args.test:
                # Test all endpoints
                test_results = userinfo_tester.test_all_endpoints()
                success = test_results.get('overall_success', False)
                sys.exit(0 if success else 1)
            elif args.complete:
                # Get complete profile
                profile = userinfo_tester.get_complete_user_profile(validate_data=validate_data)
                sys.exit(0 if profile else 1)
            else:
                # Get basic student info
                student_info = userinfo_tester.get_student_portal_info(validate_data=validate_data)
                sys.exit(0 if student_info else 1)
        else:
            # Interactive mode
            userinfo_tester.interactive_mode()

    except KeyboardInterrupt:
        colored_output.print_warning("\nApplication terminated by user")
    except Exception as e:
        colored_output.print_error(f"Application error: {str(e)}")
        sys.exit(1)

    colored_output.print_info("Application finished")

if __name__ == "__main__":
    main()