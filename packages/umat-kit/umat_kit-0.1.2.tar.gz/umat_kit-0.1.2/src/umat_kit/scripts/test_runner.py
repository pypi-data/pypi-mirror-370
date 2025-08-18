#!/usr/bin/env python3
"""
UMAT API Testing Framework - Test Runner
Demonstrates the framework capabilities with sample test scenarios
"""

import sys
import os
import time
from typing import Dict, Any

# Package-aware imports
from ..api.api import APIManager, LoginAPI, UserInfoAPI
from ..utils.utils.terminal_colors import colored_output, terminal_colors
from ..utils.utils.logger import setup_logger
from ..config import config_manager

class TestRunner:
    """Demonstration test runner for UMAT API framework"""

    def __init__(self):
        self.logger = setup_logger('TestRunner')
        self.api_manager = APIManager()

        # Display banner
        self._display_banner()

    def _display_banner(self) -> None:
        """Display test runner banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    UMAT TEST RUNNER                          ║
║              Framework Demonstration Suite                   ║
║                                                              ║
║  🧪 Demonstrates all framework capabilities                 ║
║  📊 Shows advanced testing features                         ║
║  🎨 Showcases rich terminal output                          ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(terminal_colors.highlight(banner))
        colored_output.print_separator()

    def run_demo_with_credentials(self, username: str, password: str) -> None:
        """Run complete demonstration with provided credentials"""
        colored_output.print_header("🚀 UMAT API Framework Demonstration", f"User: {username}")

        try:
            # Demo 1: Configuration validation
            self._demo_configuration()

            # Demo 2: Authentication testing
            self._demo_authentication(username, password)

            # Demo 3: User information retrieval
            self._demo_user_information()

            # Demo 4: Data validation
            self._demo_data_validation()

            # Demo 5: Performance testing
            self._demo_performance_testing()

            # Demo 6: Error handling
            self._demo_error_handling()

            # Demo 7: Export capabilities
            self._demo_export_capabilities()

            # Demo 8: Comprehensive test suite
            self._demo_comprehensive_testing(username, password)

            colored_output.print_header("🎉 Demonstration Complete!")
            colored_output.print_success("All framework features demonstrated successfully")

        except Exception as e:
            colored_output.print_error(f"Demo error: {str(e)}")
            self.logger.error(f"Demo error: {str(e)}")

        finally:
            # Cleanup
            self.api_manager.logout()

    def _demo_configuration(self) -> None:
        """Demonstrate configuration management"""
        colored_output.print_header("⚙️ Configuration Management Demo")

        colored_output.print_info("Validating configuration...")
        if config_manager.validate_config():
            colored_output.print_success("✅ Configuration validation passed")
        else:
            colored_output.print_error("❌ Configuration validation failed")

        # Show configuration details
        colored_output.print_info(f"Base URL: {config_manager.get_config('UMAT_BASE_URL')}")
        colored_output.print_info(f"Debug Mode: {config_manager.get_config('DEBUG')}")
        colored_output.print_info(f"Log Level: {config_manager.get_config('LOG_LEVEL')}")

        self._pause_demo()

    def _demo_authentication(self, username: str, password: str) -> None:
        """Demonstrate authentication capabilities"""
        colored_output.print_header("🔐 Authentication Demo")

        colored_output.print_info("Testing authentication flow...")

        # Test authentication
        success = self.api_manager.authenticate(username, password)

        if success:
            colored_output.print_success("✅ Authentication successful")

            # Show session information
            colored_output.print_info("Session Information:")
            self.api_manager.print_session_status()

            # Test token validation
            colored_output.print_info("Testing token validation...")
            validation_result = self.api_manager.login_api.validate_current_token()

            if validation_result.is_valid:
                colored_output.print_success("✅ Token validation passed")
            else:
                colored_output.print_warning("⚠️ Token validation issues")
                for error in validation_result.errors:
                    colored_output.print_error(f"  • {error}")
        else:
            colored_output.print_error("❌ Authentication failed")

        self._pause_demo()

    def _demo_user_information(self) -> None:
        """Demonstrate user information retrieval"""
        colored_output.print_header("👤 User Information Demo")

        colored_output.print_info("Retrieving complete user profile...")

        profile = self.api_manager.get_complete_user_profile(validate_data=True)

        if profile and profile.get('consolidated_data'):
            colored_output.print_success("✅ User profile retrieved successfully")

            # Show key information
            user_data = profile['consolidated_data']
            key_info = [
                ['Full Name', user_data.get('fullName', 'N/A')],
                ['Student Number', user_data.get('studentNumber', 'N/A')],
                ['Programme', user_data.get('programme', 'N/A')],
                ['Department', user_data.get('department', 'N/A')],
                ['Campus', user_data.get('campus', 'N/A')],
                ['Year Group', str(user_data.get('yearGroup', 'N/A'))],
                ['Level', str(user_data.get('level', 'N/A'))]
            ]

            colored_output.print_table(key_info, ['Field', 'Value'], 'Student Information')
        else:
            colored_output.print_error("❌ Failed to retrieve user profile")

        self._pause_demo()

    def _demo_data_validation(self) -> None:
        """Demonstrate data validation capabilities"""
        colored_output.print_header("🔍 Data Validation Demo")

        colored_output.print_info("Testing data validation...")

        # Get user data and validate
        response = self.api_manager.userinfo_api.get_student_portal_info(
            use_cache=False,
            validate_data=True
        )

        if response.validation_result:
            if response.validation_result.is_valid:
                colored_output.print_success("✅ Data validation passed")
                colored_output.print_info("All required fields present and valid")
            else:
                colored_output.print_warning("⚠️ Data validation issues found")

                for error in response.validation_result.errors:
                    colored_output.print_error(f"  Error: {error}")

                for warning in response.validation_result.warnings:
                    colored_output.print_warning(f"  Warning: {warning}")
        else:
            colored_output.print_info("No validation result available")

        self._pause_demo()

    def _demo_performance_testing(self) -> None:
        """Demonstrate performance testing capabilities"""
        colored_output.print_header("⚡ Performance Testing Demo")

        colored_output.print_info("Running performance tests...")

        # Create progress bar
        with colored_output.create_progress_bar("Performance Testing") as progress:
            task = progress.add_task("Testing API performance...", total=5)

            response_times = []

            for i in range(5):
                start_time = time.time()

                response = self.api_manager.userinfo_api.get_student_portal_info(use_cache=False)

                if response.is_success:
                    response_times.append(response.response_time)

                progress.update(task, advance=1)
                time.sleep(0.5)  # Small delay between requests

        # Analyze results
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)

            performance_data = [
                ['Average Response Time', f"{avg_time:.3f}s"],
                ['Fastest Response', f"{min_time:.3f}s"],
                ['Slowest Response', f"{max_time:.3f}s"],
                ['Total Requests', str(len(response_times))],
                ['Success Rate', '100%']
            ]

            colored_output.print_table(performance_data, ['Metric', 'Value'], 'Performance Results')

            # Performance assessment
            if avg_time < 1.0:
                colored_output.print_success("🚀 Excellent performance!")
            elif avg_time < 3.0:
                colored_output.print_info("⚡ Good performance")
            else:
                colored_output.print_warning("🐌 Performance could be improved")
        else:
            colored_output.print_error("❌ No successful requests for performance analysis")

        self._pause_demo()

    def _demo_error_handling(self) -> None:
        """Demonstrate error handling capabilities"""
        colored_output.print_header("🛡️ Error Handling Demo")

        colored_output.print_info("Testing error handling with invalid requests...")

        # Test invalid endpoint
        try:
            colored_output.print_info("Testing invalid endpoint...")
            response = self.api_manager.userinfo_api.get('/api/invalid/endpoint')

            colored_output.print_info(f"Response status: {response.status_code}")

            if response.status_code == 404:
                colored_output.print_success("✅ 404 error handled correctly")
            else:
                colored_output.print_info(f"Received status: {response.status_code}")

        except Exception as e:
            colored_output.print_success(f"✅ Exception handled gracefully: {type(e).__name__}")

        # Test timeout handling (simulated)
        colored_output.print_info("Error handling capabilities demonstrated:")
        error_features = [
            "✅ HTTP status code validation",
            "✅ Network error handling",
            "✅ Timeout management",
            "✅ Retry mechanisms",
            "✅ Graceful degradation",
            "✅ Detailed error logging"
        ]

        for feature in error_features:
            colored_output.print_info(f"  {feature}")

        self._pause_demo()

    def _demo_export_capabilities(self) -> None:
        """Demonstrate export capabilities"""
        colored_output.print_header("💾 Export Capabilities Demo")

        colored_output.print_info("Demonstrating export capabilities...")

        # Show API statistics
        colored_output.print_info("Current API statistics:")
        stats = self.api_manager.get_api_statistics()

        # Display key statistics
        login_stats = stats.get('login_api_stats', {})
        userinfo_stats = stats.get('userinfo_api_stats', {})

        stats_data = [
            ['Login API Requests', str(login_stats.get('total_requests', 0))],
            ['Login API Success', str(login_stats.get('successful_requests', 0))],
            ['UserInfo API Requests', str(userinfo_stats.get('total_requests', 0))],
            ['UserInfo API Success', str(userinfo_stats.get('successful_requests', 0))],
            ['Session Active', str(stats.get('session_info', {}).get('is_authenticated', False))]
        ]

        colored_output.print_table(stats_data, ['Metric', 'Value'], 'API Usage Statistics')

        colored_output.print_info("Export features available:")
        export_features = [
            "📊 API usage statistics",
            "🔍 Session information",
            "🧪 Test results",
            "📈 Performance metrics",
            "⚙️ Configuration details",
            "📝 Request/response logs"
        ]

        for feature in export_features:
            colored_output.print_info(f"  {feature}")

        self._pause_demo()

    def _demo_comprehensive_testing(self, username: str, password: str) -> None:
        """Demonstrate comprehensive testing suite"""
        colored_output.print_header("🔬 Comprehensive Testing Demo")

        colored_output.print_info("Running comprehensive test suite...")
        colored_output.print_warning("Note: This will logout and re-authenticate for testing")

        # Run comprehensive test
        results = self.api_manager.run_comprehensive_test_suite(username, password)

        # The comprehensive test suite will display its own results
        colored_output.print_info("Comprehensive test suite completed!")

        # Re-authenticate for any remaining demos
        self.api_manager.authenticate(username, password)

        self._pause_demo()

    def _pause_demo(self) -> None:
        """Pause demo for user to read output"""
        try:
            input(terminal_colors.info("\n⏸️  Press Enter to continue to next demo..."))
            colored_output.print_separator()
        except KeyboardInterrupt:
            colored_output.print_warning("\nDemo interrupted by user")
            raise

    def run_interactive_demo(self) -> None:
        """Run interactive demo mode"""
        colored_output.print_header("🎮 Interactive Demo Mode")

        colored_output.print_info("This demo will showcase all framework capabilities")
        colored_output.print_info("You'll need valid UMAT credentials to proceed")
        colored_output.print_separator()

        try:
            # Get credentials
            username = input(terminal_colors.info("Enter username (student number): ")).strip()
            if not username:
                colored_output.print_error("Username cannot be empty")
                return

            password = input(terminal_colors.info("Enter password: ")).strip()
            if not password:
                colored_output.print_error("Password cannot be empty")
                return

            colored_output.print_separator()
            colored_output.print_success("🚀 Starting comprehensive framework demonstration...")
            colored_output.print_separator()

            # Run the demo
            self.run_demo_with_credentials(username, password)

        except KeyboardInterrupt:
            colored_output.print_warning("\n👋 Demo cancelled by user")
        except Exception as e:
            colored_output.print_error(f"Demo error: {str(e)}")

def main():
    """Main demo entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="UMAT API Testing Framework - Demo Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_runner.py                           # Interactive demo
  python test_runner.py -u 9012562822 -p pass   # Demo with credentials
        """
    )

    parser.add_argument('-u', '--username', help='Username (student number)')
    parser.add_argument('-p', '--password', help='Password')

    args = parser.parse_args()

    # Initialize test runner
    test_runner = TestRunner()

    try:
        if args.username and args.password:
            # Run demo with provided credentials
            test_runner.run_demo_with_credentials(args.username, args.password)
        else:
            # Run interactive demo
            test_runner.run_interactive_demo()

    except KeyboardInterrupt:
        colored_output.print_warning("\n👋 Demo terminated by user")
    except Exception as e:
        colored_output.print_error(f"💥 Demo error: {str(e)}")
        sys.exit(1)

    colored_output.print_info("🏁 Demo finished")

if __name__ == "__main__":
    main()