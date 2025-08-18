"""
Course Registration API Client
Handles course registration operations for UMAT students
"""

from typing import Dict, Any, List, Optional
from .base_client import BaseAPIClient, APIResponse
from ...utils.utils.logger import get_logger


class CourseRegistrationAPI(BaseAPIClient):
    """Course Registration API client for UMAT student portal"""

    def __init__(self, base_url: str, timeout: int = 30):
        super().__init__(base_url, timeout)
        self.logger = get_logger(self.__class__.__name__)

        # Course registration endpoints
        self.endpoints = {
            'get_regular_registration': '/api/CourseRegistration/GetRegistration/0',
            'get_resit_registration': '/api/CourseRegistration/GetRegistration/1'
        }

    def get_regular_registration(self) -> APIResponse:
        """
        Get regular course registration for the authenticated student

        Returns:
            APIResponse containing regular course registration data
        """
        if not self._auth_token:
            return APIResponse(
                status_code=401,
                headers={},
                data={'error': 'Authentication required'},
                request_method='GET',
                request_url=self._build_url(self.endpoints['get_regular_registration'])
            )

        self.logger.info("Fetching regular course registration")
        response = self.get(self.endpoints['get_regular_registration'])

        if response.is_success:
            self.logger.info("Regular course registration retrieved successfully")
        else:
            self.logger.error(f"Failed to retrieve regular course registration: {response.status_code}")

        return response

    def get_resit_registration(self) -> APIResponse:
        """
        Get resit course registration for the authenticated student

        Returns:
            APIResponse containing resit course registration data
        """
        if not self._auth_token:
            return APIResponse(
                status_code=401,
                headers={},
                data={'error': 'Authentication required'},
                request_method='GET',
                request_url=self._build_url(self.endpoints['get_resit_registration'])
            )

        self.logger.info("Fetching resit course registration")
        response = self.get(self.endpoints['get_resit_registration'])

        if response.is_success:
            self.logger.info("Resit course registration retrieved successfully")
        else:
            self.logger.error(f"Failed to retrieve resit course registration: {response.status_code}")

        return response

    def parse_registration_data(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse registration response data into a clean format

        Args:
            response_data: Raw API response data

        Returns:
            List of parsed course registration records
        """
        if not response_data or 'result' not in response_data:
            return []

        courses = []
        for course_data in response_data.get('result', []):
            course = {
                'code': course_data.get('code', 'N/A'),
                'name': course_data.get('name', 'N/A'),
                'credit': course_data.get('credit', 0),
                'year': course_data.get('year', 'N/A'),
                'registration_status': course_data.get('registrationStatus', 0),
                'registration_status_desc': course_data.get('registrationStatusDesc', 'Unknown'),
                'registration_date': course_data.get('registrationDate'),
                'registration_id': course_data.get('registrationId'),
                'course_id': course_data.get('courseId'),
                'year_group': course_data.get('yearGroup'),
                'semester': course_data.get('academicPeriodSemester', 0),
                'programme_name': course_data.get('programmeName', 'N/A'),
                'programme_code': course_data.get('programmeCode', 'N/A'),
                'department': course_data.get('departmentName', 'N/A'),
                'campus': course_data.get('campusName', 'N/A'),
                'first_examiner': course_data.get('firstExaminerStaff', 'N/A'),
                'academic_period': f"{course_data.get('academicPeriodLowerYear', '')}-{course_data.get('academicPeriodUpperYear', '')}"
            }
            courses.append(course)

        return courses

    def get_registration_summary(self, courses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of registration data

        Args:
            courses: List of parsed course data

        Returns:
            Dictionary containing registration summary
        """
        if not courses:
            return {
                'total_courses': 0,
                'total_credits': 0,
                'registered_courses': 0,
                'pending_courses': 0,
                'failed_courses': 0
            }

        total_courses = len(courses)
        total_credits = sum(course.get('credit', 0) for course in courses)

        # Count by registration status
        registered_courses = len([c for c in courses if c.get('registration_status') == 1])
        pending_courses = len([c for c in courses if c.get('registration_status') == 2])
        failed_courses = len([c for c in courses if c.get('registration_status') == 3])

        return {
            'total_courses': total_courses,
            'total_credits': total_credits,
            'registered_courses': registered_courses,
            'pending_courses': pending_courses,
            'failed_courses': failed_courses,
            'programme': courses[0].get('programme_name', 'N/A') if courses else 'N/A',
            'department': courses[0].get('department', 'N/A') if courses else 'N/A',
            'academic_period': courses[0].get('academic_period', 'N/A') if courses else 'N/A'
        }