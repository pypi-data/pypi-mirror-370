"""
Advanced API Manager for UMAT Testing Framework
Orchestrates all API operations and provides unified interface
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from .login_api import LoginAPI
from .userinfo_api import UserInfoAPI
from .course_registration_api import CourseRegistrationAPI
from .academic_results_api import AcademicResultsAPI
from .bills_payment_api import BillsPaymentAPI
from .course_assessment_api import CourseAssessmentAPI
from ...utils.utils.logger import get_logger
from ...utils.utils.terminal_colors import colored_output
from ...config import config

class APIManager:
    """Comprehensive API management system for UMAT testing"""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or config.api.base_url
        self.logger = get_logger(self.__class__.__name__)

        # Initialize API clients
        self.login_api = LoginAPI(self.base_url)
        self.userinfo_api = UserInfoAPI(self.base_url)
        self.course_registration_api = CourseRegistrationAPI(self.base_url)
        self.academic_results_api = AcademicResultsAPI(self.base_url)
        self.bills_payment_api = BillsPaymentAPI(self.base_url)
        self.course_assessment_api = CourseAssessmentAPI(self.base_url)

        # Session management
        self.current_session: Optional[Dict[str, Any]] = None
        self.session_start_time: Optional[datetime] = None

        # Test results storage
        self.test_results: Dict[str, Any] = {}

        colored_output.print_header("🚀 UMAT API Manager Initialized", f"Base URL: {self.base_url}")

    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate user and establish session

        Args:
            username: Student number or username
            password: User password

        Returns:
            True if authentication successful
        """
        colored_output.print_header("🔐 Authentication Process", f"User: {username}")

        try:
            # Attempt login
            login_response = self.login_api.login(username, password)

            if login_response.is_success:
                # Share authentication token with other API clients
                if self.login_api._auth_token:
                    self.userinfo_api.set_auth_token(self.login_api._auth_token)
                    self.course_registration_api.set_auth_token(self.login_api._auth_token)
                    self.academic_results_api.set_auth_token(self.login_api._auth_token)
                    self.bills_payment_api.set_auth_token(self.login_api._auth_token)
                    self.course_assessment_api.set_auth_token(self.login_api._auth_token)

                # Establish session
                self.current_session = self.login_api.get_session_info()
                self.session_start_time = datetime.now(timezone.utc)

                colored_output.print_success("✅ Authentication successful - Session established")
                self.logger.info(f"User {username} authenticated and session established")
                return True
            else:
                colored_output.print_error("❌ Authentication failed")
                self.logger.error(f"Authentication failed for user {username}")
                return False

        except Exception as e:
            colored_output.print_error(f"Authentication error: {str(e)}")
            self.logger.error(f"Authentication error for {username}: {str(e)}")
            return False

    def get_complete_user_profile(self, validate_data: bool = True) -> Dict[str, Any]:
        """
        Get complete user profile from all available endpoints

        Args:
            validate_data: Whether to validate response data

        Returns:
            Dictionary with complete user profile
        """
        colored_output.print_header("👤 Complete User Profile Retrieval")

        if not self._check_authentication():
            return {'error': 'Not authenticated'}

        # Get all user information
        all_responses = self.userinfo_api.get_all_user_info(validate_data=validate_data)

        # Compile complete profile
        complete_profile = {
            'retrieval_timestamp': datetime.now().isoformat(),
            'data_sources': {},
            'consolidated_data': {},
            'validation_results': {},
            'errors': []
        }

        # Process each response
        for endpoint_name, response in all_responses.items():
            complete_profile['data_sources'][endpoint_name] = {
                'success': response.is_success,
                'status_code': response.status_code,
                'response_time': response.response_time,
                'has_data': bool(response.data)
            }

            if response.is_success and response.data:
                # Merge data into consolidated profile
                complete_profile['consolidated_data'].update(response.data)

                # Store validation results
                if response.validation_result:
                    complete_profile['validation_results'][endpoint_name] = {
                        'is_valid': response.validation_result.is_valid,
                        'errors': response.validation_result.errors,
                        'warnings': response.validation_result.warnings
                    }
            else:
                complete_profile['errors'].append(f"Failed to retrieve data from {endpoint_name}")

        # Display consolidated profile
        if complete_profile['consolidated_data']:
            colored_output.print_json(complete_profile['consolidated_data'], "Consolidated User Profile")

        return complete_profile

    def run_comprehensive_test_suite(self, username: str, password: str) -> Dict[str, Any]:
        """
        Run comprehensive test suite for all API endpoints

        Args:
            username: Test username
            password: Test password

        Returns:
            Dictionary with complete test results
        """
        colored_output.print_header("🧪 Comprehensive API Test Suite", f"Testing with user: {username}")

        test_suite_results = {
            'test_start_time': datetime.now().isoformat(),
            'test_end_time': None,
            'total_duration': None,
            'authentication_test': None,
            'user_info_test': None,
            'session_management_test': None,
            'overall_success': False,
            'summary': {}
        }

        start_time = datetime.now()

        try:
            # Test 1: Authentication Flow
            colored_output.print_info("🔐 Running authentication flow test...")
            auth_test_results = self.login_api.test_authentication_flow(username, password)
            test_suite_results['authentication_test'] = auth_test_results

            # Re-authenticate for subsequent tests
            if auth_test_results.get('overall_success'):
                colored_output.print_info("Re-authenticating for subsequent tests...")
                self.authenticate(username, password)

                # Test 2: User Information Endpoints
                colored_output.print_info("👤 Running user info endpoints test...")
                userinfo_test_results = self.userinfo_api.test_user_info_endpoints()
                test_suite_results['user_info_test'] = userinfo_test_results

                # Test 3: Session Management
                colored_output.print_info("🔄 Running session management test...")
                session_test_results = self._test_session_management()
                test_suite_results['session_management_test'] = session_test_results

            # Calculate overall success
            test_suite_results['overall_success'] = all([
                test_suite_results.get('authentication_test', {}).get('overall_success', False),
                test_suite_results.get('user_info_test', {}).get('overall_success', False),
                test_suite_results.get('session_management_test', {}).get('success', False)
            ])

        except Exception as e:
            colored_output.print_error(f"Test suite error: {str(e)}")
            test_suite_results['error'] = str(e)
            self.logger.error(f"Test suite error: {str(e)}")

        finally:
            # Clean up session
            self.logout()

        # Finalize results
        end_time = datetime.now()
        test_suite_results['test_end_time'] = end_time.isoformat()
        test_suite_results['total_duration'] = str(end_time - start_time)

        # Generate summary
        test_suite_results['summary'] = self._generate_test_summary(test_suite_results)

        # Store results
        self.test_results[f"comprehensive_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"] = test_suite_results

        # Display final results
        self._display_test_suite_results(test_suite_results)

        return test_suite_results

    def logout(self) -> bool:
        """
        Logout and clean up session

        Returns:
            True if logout successful
        """
        colored_output.print_header("🚪 Session Logout")

        try:
            # Logout from login API
            logout_response = self.login_api.logout()

            # Clear tokens from all API clients
            self.userinfo_api.clear_auth_token()
            self.course_registration_api.clear_auth_token()
            self.academic_results_api.clear_auth_token()
            self.bills_payment_api.clear_auth_token()
            self.course_assessment_api.clear_auth_token()

            # Clear session data
            self.current_session = None
            self.session_start_time = None

            if logout_response.is_success:
                colored_output.print_success("✅ Logout successful - Session terminated")
                return True
            else:
                colored_output.print_warning("⚠️ Logout request failed, but session cleared locally")
                return False

        except Exception as e:
            colored_output.print_error(f"Logout error: {str(e)}")
            self.logger.error(f"Logout error: {str(e)}")
            return False

    def get_session_status(self) -> Dict[str, Any]:
        """
        Get current session status

        Returns:
            Dictionary with session information
        """
        if not self.current_session:
            return {'status': 'No active session'}

        session_status = self.current_session.copy()

        if self.session_start_time:
            session_duration = datetime.now(timezone.utc) - self.session_start_time
            session_status['session_duration'] = str(session_duration)

        # Get updated session info from login API
        if hasattr(self.login_api, 'get_session_info'):
            updated_info = self.login_api.get_session_info()
            session_status.update(updated_info)

        return session_status

    def print_session_status(self) -> None:
        """Print current session status to terminal"""
        session_status = self.get_session_status()

        if 'status' in session_status and session_status['status'] == 'No active session':
            colored_output.print_warning("No active session")
        else:
            colored_output.print_json(session_status, "Current Session Status")

    def get_api_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive API usage statistics

        Returns:
            Dictionary with API statistics
        """
        stats = {
            'login_api_stats': {
                'total_requests': len(self.login_api.request_history),
                'successful_requests': len(self.login_api.get_successful_responses()),
                'failed_requests': len(self.login_api.get_failed_responses())
            },
            'userinfo_api_stats': {
                'total_requests': len(self.userinfo_api.request_history),
                'successful_requests': len(self.userinfo_api.get_successful_responses()),
                'failed_requests': len(self.userinfo_api.get_failed_responses())
            },
            'course_registration_api_stats': {
                'total_requests': len(self.course_registration_api.request_history),
                'successful_requests': len(self.course_registration_api.get_successful_responses()),
                'failed_requests': len(self.course_registration_api.get_failed_responses())
            },
            'academic_results_api_stats': {
                'total_requests': len(self.academic_results_api.request_history),
                'successful_requests': len(self.academic_results_api.get_successful_responses()),
                'failed_requests': len(self.academic_results_api.get_failed_responses())
            },
            'bills_payment_api_stats': {
                'total_requests': len(self.bills_payment_api.request_history),
                'successful_requests': len(self.bills_payment_api.get_successful_responses()),
                'failed_requests': len(self.bills_payment_api.get_failed_responses())
            },
            'course_assessment_api_stats': {
                'total_requests': len(self.course_assessment_api.request_history),
                'successful_requests': len(self.course_assessment_api.get_successful_responses()),
                'failed_requests': len(self.course_assessment_api.get_failed_responses())
            },
            'session_info': self.get_session_status(),
            'test_results_count': len(self.test_results)
        }

        # Calculate average response times
        if self.login_api.request_history:
            avg_login_time = sum(r.response_time for r in self.login_api.request_history) / len(self.login_api.request_history)
            stats['login_api_stats']['avg_response_time'] = avg_login_time

        if self.userinfo_api.request_history:
            avg_userinfo_time = sum(r.response_time for r in self.userinfo_api.request_history) / len(self.userinfo_api.request_history)
            stats['userinfo_api_stats']['avg_response_time'] = avg_userinfo_time

        if self.course_registration_api.request_history:
            avg_registration_time = sum(r.response_time for r in self.course_registration_api.request_history) / len(self.course_registration_api.request_history)
            stats['course_registration_api_stats']['avg_response_time'] = avg_registration_time

        if self.academic_results_api.request_history:
            avg_results_time = sum(r.response_time for r in self.academic_results_api.request_history) / len(self.academic_results_api.request_history)
            stats['academic_results_api_stats']['avg_response_time'] = avg_results_time

        if self.bills_payment_api.request_history:
            avg_bills_time = sum(r.response_time for r in self.bills_payment_api.request_history) / len(self.bills_payment_api.request_history)
            stats['bills_payment_api_stats']['avg_response_time'] = avg_bills_time

        if self.course_assessment_api.request_history:
            avg_assessment_time = sum(r.response_time for r in self.course_assessment_api.request_history) / len(self.course_assessment_api.request_history)
            stats['course_assessment_api_stats']['avg_response_time'] = avg_assessment_time

        return stats

    def print_api_statistics(self) -> None:
        """Print API usage statistics to terminal"""
        stats = self.get_api_statistics()
        colored_output.print_json(stats, "API Usage Statistics")

    def _check_authentication(self) -> bool:
        """Check if user is authenticated"""
        if not self.current_session or not self.login_api._auth_token:
            colored_output.print_error("❌ Not authenticated. Please login first.")
            return False
        return True

    def _test_session_management(self) -> Dict[str, Any]:
        """Test session management functionality"""
        session_test = {
            'success': True,
            'tests': {},
            'errors': []
        }

        try:
            # Test session info retrieval
            session_info = self.get_session_status()
            session_test['tests']['session_info_retrieval'] = {
                'success': bool(session_info),
                'has_required_fields': all(key in session_info for key in ['is_authenticated'])
            }

            # Test token validation
            if hasattr(self.login_api, 'validate_current_token'):
                token_validation = self.login_api.validate_current_token()
                session_test['tests']['token_validation'] = {
                    'success': token_validation.is_valid,
                    'errors': token_validation.errors
                }

            # Test auto-refresh capability
            if hasattr(self.login_api, 'auto_refresh_if_needed'):
                refresh_result = self.login_api.auto_refresh_if_needed()
                session_test['tests']['auto_refresh'] = {
                    'success': refresh_result
                }

        except Exception as e:
            session_test['success'] = False
            session_test['errors'].append(str(e))

        return session_test

    def _generate_test_summary(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of test results"""
        summary = {
            'total_tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'success_rate': 0.0,
            'key_findings': []
        }

        # Count tests
        if test_results.get('authentication_test'):
            summary['total_tests_run'] += 1
            if test_results['authentication_test'].get('overall_success'):
                summary['tests_passed'] += 1
            else:
                summary['tests_failed'] += 1

        if test_results.get('user_info_test'):
            summary['total_tests_run'] += 1
            if test_results['user_info_test'].get('overall_success'):
                summary['tests_passed'] += 1
            else:
                summary['tests_failed'] += 1

        if test_results.get('session_management_test'):
            summary['total_tests_run'] += 1
            if test_results['session_management_test'].get('success'):
                summary['tests_passed'] += 1
            else:
                summary['tests_failed'] += 1

        # Calculate success rate
        if summary['total_tests_run'] > 0:
            summary['success_rate'] = (summary['tests_passed'] / summary['total_tests_run']) * 100

        # Generate key findings
        if summary['success_rate'] == 100:
            summary['key_findings'].append("All tests passed successfully")
        elif summary['success_rate'] >= 80:
            summary['key_findings'].append("Most tests passed with minor issues")
        elif summary['success_rate'] >= 50:
            summary['key_findings'].append("Some tests failed - investigation needed")
        else:
            summary['key_findings'].append("Major issues detected - comprehensive review required")

        return summary

    def _display_test_suite_results(self, results: Dict[str, Any]) -> None:
        """Display comprehensive test suite results"""
        colored_output.print_header("📊 Test Suite Results Summary")

        if results.get('overall_success'):
            colored_output.print_success("🎉 All tests completed successfully!")
        else:
            colored_output.print_error("❌ Some tests failed")

        # Display summary
        if 'summary' in results:
            summary = results['summary']
            colored_output.print_info(f"Tests Run: {summary['total_tests_run']}")
            colored_output.print_success(f"Passed: {summary['tests_passed']}")
            colored_output.print_error(f"Failed: {summary['tests_failed']}")
            colored_output.print_info(f"Success Rate: {summary['success_rate']:.1f}%")

            if summary['key_findings']:
                colored_output.print_info("Key Findings:")
                for finding in summary['key_findings']:
                    colored_output.print_info(f"  • {finding}")

        # Display duration
        if results.get('total_duration'):
            colored_output.print_info(f"Total Duration: {results['total_duration']}")

        colored_output.print_separator()
        colored_output.print_json(results, "Detailed Test Results")

    # ==================== COURSE REGISTRATION METHODS ====================

    def get_regular_registration(self) -> Dict[str, Any]:
        """
        Get regular course registration for the authenticated student

        Returns:
            Dictionary containing regular course registration data and summary
        """
        if not self._check_authentication():
            return {'error': 'Not authenticated'}

        try:
            response = self.course_registration_api.get_regular_registration()

            if response.is_success:
                courses = self.course_registration_api.parse_registration_data(response.data)
                summary = self.course_registration_api.get_registration_summary(courses)

                return {
                    'success': True,
                    'courses': courses,
                    'summary': summary,
                    'raw_response': response.data
                }
            else:
                self.logger.error(f"Failed to get regular registration: {response.status_code}")
                return {
                    'success': False,
                    'error': f"API request failed with status {response.status_code}",
                    'courses': [],
                    'summary': {}
                }

        except Exception as e:
            self.logger.error(f"Error getting regular registration: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'courses': [],
                'summary': {}
            }

    def get_resit_registration(self) -> Dict[str, Any]:
        """
        Get resit course registration for the authenticated student

        Returns:
            Dictionary containing resit course registration data and summary
        """
        if not self._check_authentication():
            return {'error': 'Not authenticated'}

        try:
            response = self.course_registration_api.get_resit_registration()

            if response.is_success:
                courses = self.course_registration_api.parse_registration_data(response.data)
                summary = self.course_registration_api.get_registration_summary(courses)

                return {
                    'success': True,
                    'courses': courses,
                    'summary': summary,
                    'raw_response': response.data
                }
            else:
                self.logger.error(f"Failed to get resit registration: {response.status_code}")
                return {
                    'success': False,
                    'error': f"API request failed with status {response.status_code}",
                    'courses': [],
                    'summary': {}
                }

        except Exception as e:
            self.logger.error(f"Error getting resit registration: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'courses': [],
                'summary': {}
            }

    def get_academic_results(self) -> Dict[str, Any]:
        """
        Get academic results for the authenticated student

        Returns:
            Dictionary containing academic results data and summary
        """
        if not self._check_authentication():
            return {'error': 'Not authenticated'}

        try:
            response = self.academic_results_api.get_student_results()

            if response.is_success:
                semesters = self.academic_results_api.parse_results_data(response.data)
                summary = self.academic_results_api.get_results_summary(semesters)

                return {
                    'success': True,
                    'semesters': semesters,
                    'summary': summary,
                    'raw_response': response.data
                }
            else:
                self.logger.error(f"Failed to get academic results: {response.status_code}")
                return {
                    'success': False,
                    'error': f"API request failed with status {response.status_code}",
                    'semesters': [],
                    'summary': {}
                }

        except Exception as e:
            self.logger.error(f"Error getting academic results: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'semesters': [],
                'summary': {}
            }

    def get_bills_and_payments(self) -> Dict[str, Any]:
        """
        Get comprehensive bills and payment information for the authenticated student

        Returns:
            Dictionary containing bills, payments, and summary data
        """
        if not self._check_authentication():
            return {'error': 'Not authenticated'}

        try:
            # Get all billing and payment data
            bill_summary_response = self.bills_payment_api.get_bill_summary()
            student_bills_response = self.bills_payment_api.get_student_bills()
            transactions_response = self.bills_payment_api.get_student_transactions()

            # Parse responses
            bill_summary = {}
            student_bills = []
            transactions = {'school_fees': [], 'other_fees': []}

            if bill_summary_response.is_success:
                bill_summary = self.bills_payment_api.parse_bill_summary(bill_summary_response.data)

            if student_bills_response.is_success:
                student_bills = self.bills_payment_api.parse_student_bills(student_bills_response.data)

            if transactions_response.is_success:
                transactions = self.bills_payment_api.parse_student_transactions(transactions_response.data)

            # Generate comprehensive summary
            payment_summary = self.bills_payment_api.get_payment_summary(bill_summary, transactions)

            return {
                'success': True,
                'bill_summary': bill_summary,
                'student_bills': student_bills,
                'transactions': transactions,
                'payment_summary': payment_summary,
                'raw_responses': {
                    'bill_summary': bill_summary_response.data if bill_summary_response.is_success else None,
                    'student_bills': student_bills_response.data if student_bills_response.is_success else None,
                    'transactions': transactions_response.data if transactions_response.is_success else None
                }
            }

        except Exception as e:
            self.logger.error(f"Error getting bills and payments: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'bill_summary': {},
                'student_bills': [],
                'transactions': {'school_fees': [], 'other_fees': []},
                'payment_summary': {}
            }

    def get_course_assessments(self) -> Dict[str, Any]:
        """
        Get course assessment questions for the authenticated student

        Returns:
            Dictionary containing course assessment data and summary
        """
        if not self._check_authentication():
            return {'error': 'Not authenticated'}

        try:
            response = self.course_assessment_api.get_assessment_questions()

            if response.is_success:
                courses = self.course_assessment_api.parse_assessment_data(response.data)
                summary = self.course_assessment_api.get_assessment_summary(courses)
                categories_info = self.course_assessment_api.get_assessment_categories_info()
                categories_breakdown = self.course_assessment_api.get_question_categories_breakdown(courses)
                formatted_courses = self.course_assessment_api.format_assessment_for_display(courses)

                return {
                    'success': True,
                    'courses': courses,
                    'formatted_courses': formatted_courses,
                    'summary': summary,
                    'categories_info': categories_info,
                    'categories_breakdown': categories_breakdown,
                    'raw_response': response.data
                }
            else:
                return {
                    'success': False,
                    'error': f"API request failed with status {response.status_code}",
                    'courses': [],
                    'formatted_courses': [],
                    'summary': {},
                    'categories_info': {},
                    'categories_breakdown': {}
                }

        except Exception as e:
            self.logger.error(f"Error getting course assessments: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'courses': [],
                'formatted_courses': [],
                'summary': {},
                'categories_info': {},
                'categories_breakdown': {}
            }

    def submit_course_assessment(self, course_id: int, ratings: Dict[int, int], remarks: str = "") -> Dict[str, Any]:
        """
        Submit course assessment ratings for a specific course

        Args:
            course_id: The ID of the course being assessed
            ratings: Dictionary mapping question IDs to rating values (1-5)
            remarks: Optional remarks/comments for the course

        Returns:
            Dictionary containing submission result
        """
        if not self._check_authentication():
            return {'success': False, 'error': 'Not authenticated'}

        try:
            # Get student number from current session
            if not self.current_session:
                return {'success': False, 'error': 'No active session found'}

            current_user = self.current_session.get('current_user', {})
            student_number = current_user.get('unique_name') or current_user.get('preferred_username')
            if not student_number:
                return {'success': False, 'error': 'Student number not found in session'}

            # Get course data to validate and prepare submission
            assessment_data = self.get_course_assessments()
            if not assessment_data.get('success'):
                return {'success': False, 'error': 'Failed to get course data for validation'}

            # Find the specific course
            course_data = None
            for course in assessment_data.get('courses', []):
                if course.get('id') == course_id:
                    course_data = course
                    break

            if not course_data:
                return {'success': False, 'error': f'Course with ID {course_id} not found'}

            # Validate assessment completion
            validation = self.course_assessment_api.validate_assessment_completion(course_data, ratings)
            if not validation['is_complete']:
                return {
                    'success': False,
                    'error': 'Assessment incomplete',
                    'validation': validation
                }

            # Submit assessment
            response = self.course_assessment_api.submit_course_assessment(student_number, course_id, ratings, remarks)

            if response.is_success:
                return {
                    'success': True,
                    'message': 'Course assessment submitted successfully',
                    'course_code': course_data.get('code', 'N/A'),
                    'course_name': course_data.get('name', 'N/A'),
                    'total_questions': validation['total_questions'],
                    'submission_data': response.data
                }
            else:
                return {
                    'success': False,
                    'error': f'Submission failed with status {response.status_code}',
                    'details': response.data if hasattr(response, 'data') else None
                }

        except Exception as e:
            self.logger.error(f"Error submitting course assessment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def submit_all_course_assessments(self, assessments: List[Dict[str, Any]], general_remarks: str = "") -> Dict[str, Any]:
        """
        Submit all course assessments at once (matches web interface behavior)

        Args:
            assessments: List of assessment data for all courses
                [
                    {
                        'course_id': int,
                        'ratings': {question_id: score, ...}
                    },
                    ...
                ]
            general_remarks: General remarks to apply to all courses

        Returns:
            Dictionary with success status and details
        """
        if not self._check_authentication():
            return {'success': False, 'error': 'Not authenticated'}

        try:
            # Get student number from current session
            if not self.current_session:
                return {'success': False, 'error': 'No active session found'}

            current_user = self.current_session.get('current_user', {})
            student_number = current_user.get('unique_name') or current_user.get('preferred_username')
            if not student_number:
                return {'success': False, 'error': 'Student number not found in session'}

            # Prepare assessments with general remarks
            assessments_with_remarks = []
            for assessment in assessments:
                assessment_copy = assessment.copy()
                assessment_copy['remarks'] = general_remarks
                assessments_with_remarks.append(assessment_copy)

            # Submit all assessments at once
            response = self.course_assessment_api.submit_all_course_assessments(
                student_number, assessments_with_remarks
            )

            if response.is_success:
                self.logger.info(f"Successfully submitted all {len(assessments)} course assessments")
                return {
                    'success': True,
                    'message': f'Successfully submitted {len(assessments)} course assessments',
                    'courses_submitted': len(assessments)
                }
            else:
                error_msg = f"Failed to submit assessments: HTTP {response.status_code}"
                if response.data and isinstance(response.data, dict):
                    error_msg += f" - {response.data.get('message', 'Unknown error')}"

                self.logger.error(error_msg)
                return {'success': False, 'error': error_msg}

        except Exception as e:
            self.logger.error(f"Unexpected error during bulk course assessment submission: {str(e)}")
            return {'success': False, 'error': f'Unexpected error: {str(e)}'}

    # ==================== UPDATE METHODS ====================

    def update_user_email(self, email: str, validate_email: bool = True) -> bool:
        """
        Update user email address

        Args:
            email: New email address
            validate_email: Whether to validate email format

        Returns:
            True if update successful
        """
        colored_output.print_header("📧 Email Update Request")

        if not self._check_authentication():
            return False

        try:
            response = self.userinfo_api.update_email(email, validate_email)

            if response.is_success:
                colored_output.print_success(f"✅ Email updated successfully to: {email}")
                self.logger.info(f"Email updated successfully to: {email}")
                return True
            else:
                colored_output.print_error(f"❌ Email update failed: {response.status_code}")
                if response.data and 'error' in response.data:
                    colored_output.print_error(f"Error details: {response.data['error']}")
                self.logger.error(f"Email update failed: {response.status_code} - {response.data}")
                return False

        except Exception as e:
            colored_output.print_error(f"Email update error: {str(e)}")
            self.logger.error(f"Email update error: {str(e)}")
            return False

    def update_user_profile(self, profile_data: Dict[str, Any],
                           validate_data: bool = True) -> bool:
        """
        Update user profile information

        Args:
            profile_data: Dictionary containing profile fields to update
            validate_data: Whether to validate the update data

        Returns:
            True if update successful
        """
        colored_output.print_header("📝 Profile Update Request")

        if not self._check_authentication():
            return False

        try:
            response = self.userinfo_api.update_profile(profile_data, validate_data)

            if response.is_success:
                colored_output.print_success("✅ Profile updated successfully")
                colored_output.print_info(f"Updated fields: {list(profile_data.keys())}")
                self.logger.info(f"Profile updated successfully: {list(profile_data.keys())}")
                return True
            else:
                colored_output.print_error(f"❌ Profile update failed: {response.status_code}")
                if response.data and 'error' in response.data:
                    colored_output.print_error(f"Error details: {response.data['error']}")
                self.logger.error(f"Profile update failed: {response.status_code} - {response.data}")
                return False

        except Exception as e:
            colored_output.print_error(f"Profile update error: {str(e)}")
            self.logger.error(f"Profile update error: {str(e)}")
            return False

    def update_user_contact_info(self, contact_data: Dict[str, Any],
                                validate_data: bool = True) -> bool:
        """
        Update user contact information

        Args:
            contact_data: Dictionary containing contact fields to update
            validate_data: Whether to validate the update data

        Returns:
            True if update successful
        """
        colored_output.print_header("📞 Contact Info Update Request")

        if not self._check_authentication():
            return False

        try:
            response = self.userinfo_api.update_contact_info(contact_data, validate_data)

            if response.is_success:
                colored_output.print_success("✅ Contact information updated successfully")
                colored_output.print_info(f"Updated fields: {list(contact_data.keys())}")
                self.logger.info(f"Contact info updated successfully: {list(contact_data.keys())}")
                return True
            else:
                colored_output.print_error(f"❌ Contact info update failed: {response.status_code}")
                if response.data and 'error' in response.data:
                    colored_output.print_error(f"Error details: {response.data['error']}")
                self.logger.error(f"Contact info update failed: {response.status_code} - {response.data}")
                return False

        except Exception as e:
            colored_output.print_error(f"Contact info update error: {str(e)}")
            self.logger.error(f"Contact info update error: {str(e)}")
            return False

    def update_user_personal_info(self, personal_data: Dict[str, Any],
                                 validate_data: bool = True) -> bool:
        """
        Update user personal information

        Args:
            personal_data: Dictionary containing personal fields to update
            validate_data: Whether to validate the update data

        Returns:
            True if update successful
        """
        colored_output.print_header("🏠 Personal Info Update Request")

        if not self._check_authentication():
            return False

        try:
            response = self.userinfo_api.update_personal_info(personal_data, validate_data)

            if response.is_success:
                colored_output.print_success("✅ Personal information updated successfully")
                colored_output.print_info(f"Updated fields: {list(personal_data.keys())}")
                self.logger.info(f"Personal info updated successfully: {list(personal_data.keys())}")
                return True
            else:
                colored_output.print_error(f"❌ Personal info update failed: {response.status_code}")
                if response.data and 'error' in response.data:
                    colored_output.print_error(f"Error details: {response.data['error']}")
                self.logger.error(f"Personal info update failed: {response.status_code} - {response.data}")
                return False

        except Exception as e:
            colored_output.print_error(f"Personal info update error: {str(e)}")
            self.logger.error(f"Personal info update error: {str(e)}")
            return False