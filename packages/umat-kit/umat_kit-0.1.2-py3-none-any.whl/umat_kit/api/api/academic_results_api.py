"""
Academic Results API Client
Handles academic results operations for UMAT students
"""

from typing import Dict, Any, List, Optional
from .base_client import BaseAPIClient, APIResponse
from ...utils.utils.logger import get_logger


class AcademicResultsAPI(BaseAPIClient):
    """Academic Results API client for UMAT student portal"""

    def __init__(self, base_url: str, timeout: int = 30):
        super().__init__(base_url, timeout)
        self.logger = get_logger(self.__class__.__name__)

        # Academic results endpoints
        self.endpoints = {
            'get_student_results': '/api/StudentResult/GetStudentResultsGroup'
        }

    def get_student_results(self) -> APIResponse:
        """
        Get academic results for the authenticated student

        Returns:
            APIResponse containing student academic results data
        """
        if not self._auth_token:
            return APIResponse(
                status_code=401,
                headers={},
                data={'error': 'Authentication required'},
                request_method='GET',
                request_url=self._build_url(self.endpoints['get_student_results'])
            )

        self.logger.info("Fetching student academic results")
        response = self.get(self.endpoints['get_student_results'])

        if response.is_success:
            self.logger.info("Student academic results retrieved successfully")
        else:
            self.logger.error(f"Failed to retrieve student academic results: {response.status_code}")

        return response

    def parse_results_data(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse academic results response data into a clean format

        Args:
            response_data: Raw API response data

        Returns:
            List of parsed semester results
        """
        if not response_data or 'result' not in response_data:
            return []

        semesters = []
        for semester_data in response_data.get('result', []):
            # Parse semester information
            semester = {
                'semester': semester_data.get('semester', 0),
                'year': semester_data.get('year', 0),
                'academic_year': semester_data.get('academicYear', 'N/A'),
                'student_result_id': semester_data.get('studentResultId'),
                'credit_earned': semester_data.get('creditEarned', 0),
                'credit_registered': semester_data.get('creditRegistered', 0),
                'semester_weighted_mark': semester_data.get('semesterWeightedMark', 0.0),
                'semester_average': semester_data.get('semesterAverage', 0.0),
                'cumulative_credit_registered': semester_data.get('cumulativeCreditRegistered', 0),
                'cumulative_credit_earned': semester_data.get('cumulativeCreditEarned', 0),
                'cumulative_semester_mark': semester_data.get('cumulativeSemesterMark', 0.0),
                'cwa': semester_data.get('cwa', 0.0),
                'courses': [],
                'remarks': [],
                'student_info': {}
            }

            # Parse student information
            name_data = semester_data.get('name', {})
            semester['student_info'] = {
                'full_name': name_data.get('fullName', 'N/A'),
                'full_name_v2': name_data.get('fullNamev2', 'N/A'),
                'first_name': name_data.get('firstName', 'N/A'),
                'last_name': name_data.get('lastName', 'N/A'),
                'other_name': name_data.get('otherName', 'N/A'),
                'sex': name_data.get('sex', 0)
            }

            semester['index_number'] = semester_data.get('indexNumber', 'N/A')
            semester['student_number'] = semester_data.get('studentNumber', 'N/A')

            # Parse courses (sheets)
            for course_data in semester_data.get('sheets', []):
                course = {
                    'sheet_id': course_data.get('studentResultSheetId'),
                    'code': course_data.get('code', 'N/A'),
                    'course_name': course_data.get('courseName', 'N/A'),
                    'credit': course_data.get('credit', 0),
                    'class_score': course_data.get('classScore'),
                    'exam_score': course_data.get('examScore'),
                    'full_score': course_data.get('fullScore'),
                    'special_case': course_data.get('specialCase'),
                    'letter': course_data.get('letter', 'N/A'),
                    'descriptions': course_data.get('descriptions', 'N/A'),
                    'course_category': course_data.get('courseCategory', 'N/A'),
                    'course_group': course_data.get('courseGroup', 'N/A'),
                    'course_type': course_data.get('courseType', 'N/A'),
                    'course_id': course_data.get('courseId'),
                    'has_trailed': course_data.get('hasTrailed', False),
                    'has_passed': course_data.get('hasPassed', False),
                    'document_status': course_data.get('documentStatus')
                }
                semester['courses'].append(course)

            # Parse remarks (failed/trailed courses)
            for remark_data in semester_data.get('remarks', []):
                remark = {
                    'code': remark_data.get('code', 'N/A'),
                    'name': remark_data.get('name', 'N/A'),
                    'course_id': remark_data.get('courseId'),
                    'exam_score_details': {}
                }

                # Parse detailed exam score information
                exam_score = remark_data.get('examScore', {})
                if exam_score:
                    remark['exam_score_details'] = {
                        'assignment': exam_score.get('assignment'),
                        'quiz_1': exam_score.get('quiz_1'),
                        'quiz_2': exam_score.get('quiz_2'),
                        'total': exam_score.get('total'),
                        'attendance': exam_score.get('attendance'),
                        'class_assessment': exam_score.get('classAssessment'),
                        'exam': exam_score.get('exam'),
                        'full': exam_score.get('full'),
                        'special_case': exam_score.get('specialCase'),
                        'has_passed': exam_score.get('hasPassed', False),
                        'has_trailed': exam_score.get('hasTrailed', False),
                        'status': exam_score.get('status'),
                        'letter': exam_score.get('letter', 'N/A'),
                        'descriptions': exam_score.get('descriptions', 'N/A')
                    }

                semester['remarks'].append(remark)

            semesters.append(semester)

        return semesters

    def get_results_summary(self, semesters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of academic results

        Args:
            semesters: List of parsed semester data

        Returns:
            Dictionary containing academic results summary
        """
        if not semesters:
            return {
                'total_semesters': 0,
                'total_credits_registered': 0,
                'total_credits_earned': 0,
                'overall_cwa': 0.0,
                'total_courses': 0,
                'passed_courses': 0,
                'failed_courses': 0,
                'trailed_courses': 0,
                'current_level': 'N/A'
            }

        # Get latest semester for current info
        latest_semester = max(semesters, key=lambda x: (x.get('year', 0), x.get('semester', 0)))

        total_semesters = len(semesters)
        total_credits_registered = latest_semester.get('cumulative_credit_registered', 0)
        total_credits_earned = latest_semester.get('cumulative_credit_earned', 0)
        overall_cwa = latest_semester.get('cwa', 0.0)

        # Count courses across all semesters
        total_courses = sum(len(sem.get('courses', [])) for sem in semesters)
        passed_courses = 0
        failed_courses = 0
        trailed_courses = 0

        for semester in semesters:
            for course in semester.get('courses', []):
                if course.get('has_passed'):
                    passed_courses += 1
                elif course.get('has_trailed'):
                    trailed_courses += 1
                elif course.get('letter') == 'F':
                    failed_courses += 1

        # Determine current level based on year
        current_level = 'N/A'
        if latest_semester.get('year'):
            year_level = latest_semester.get('year', 0)
            if year_level == 100:
                current_level = 'Level 100'
            elif year_level == 200:
                current_level = 'Level 200'
            elif year_level == 300:
                current_level = 'Level 300'
            elif year_level == 400:
                current_level = 'Level 400'

        return {
            'total_semesters': total_semesters,
            'total_credits_registered': total_credits_registered,
            'total_credits_earned': total_credits_earned,
            'overall_cwa': overall_cwa,
            'total_courses': total_courses,
            'passed_courses': passed_courses,
            'failed_courses': failed_courses,
            'trailed_courses': trailed_courses,
            'current_level': current_level,
            'current_academic_year': latest_semester.get('academic_year', 'N/A'),
            'student_info': latest_semester.get('student_info', {}),
            'index_number': latest_semester.get('index_number', 'N/A'),
            'student_number': latest_semester.get('student_number', 'N/A')
        }

    def get_semester_performance(self, semester_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get performance metrics for a specific semester

        Args:
            semester_data: Single semester data

        Returns:
            Dictionary containing semester performance metrics
        """
        courses = semester_data.get('courses', [])

        if not courses:
            return {
                'total_courses': 0,
                'credits_registered': 0,
                'credits_earned': 0,
                'semester_average': 0.0,
                'grade_distribution': {},
                'performance_level': 'N/A'
            }

        # Grade distribution
        grade_distribution = {}
        for course in courses:
            letter = course.get('letter', 'N/A')
            grade_distribution[letter] = grade_distribution.get(letter, 0) + 1

        # Performance level based on semester average
        semester_avg = semester_data.get('semester_average', 0.0)
        if semester_avg >= 80:
            performance_level = 'Excellent'
        elif semester_avg >= 70:
            performance_level = 'Very Good'
        elif semester_avg >= 60:
            performance_level = 'Good'
        elif semester_avg >= 50:
            performance_level = 'Pass'
        else:
            performance_level = 'Poor'

        return {
            'total_courses': len(courses),
            'credits_registered': semester_data.get('credit_registered', 0),
            'credits_earned': semester_data.get('credit_earned', 0),
            'semester_average': semester_avg,
            'grade_distribution': grade_distribution,
            'performance_level': performance_level,
            'semester': semester_data.get('semester', 0),
            'year': semester_data.get('year', 0),
            'academic_year': semester_data.get('academic_year', 'N/A')
        }