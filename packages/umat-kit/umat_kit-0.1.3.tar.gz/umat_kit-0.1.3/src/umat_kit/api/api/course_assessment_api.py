"""
Course Assessment API Client
Handles course assessment and lecturer evaluation operations for UMAT students
"""

from typing import Dict, Any, List, Optional
from .base_client import BaseAPIClient, APIResponse
from ...utils.utils.logger import get_logger


class CourseAssessmentAPI(BaseAPIClient):
    """Course Assessment API client for UMAT student portal"""

    def __init__(self, base_url: str, timeout: int = 30):
        super().__init__(base_url, timeout)
        self.logger = get_logger(self.__class__.__name__)

        # Course assessment endpoints
        self.endpoints = {
            'get_assessment_questions': '/api/Survey/GetStudentLectureAssessmentQuestion',
            'submit_assessment': '/api/Survey/SaveLecturerAssessment'
        }

    def get_assessment_questions(self) -> APIResponse:
        """
        Get course assessment questions for the authenticated student

        Returns:
            APIResponse containing course assessment questions data
        """
        if not self._auth_token:
            return APIResponse(
                status_code=401,
                headers={},
                data={'error': 'Authentication required'},
                request_method='GET',
                request_url=self._build_url(self.endpoints['get_assessment_questions'])
            )

        self.logger.info("Fetching course assessment questions")
        response = self.get(self.endpoints['get_assessment_questions'])

        if response.is_success:
            self.logger.info("Course assessment questions retrieved successfully")
        else:
            self.logger.error(f"Failed to retrieve course assessment questions: {response.status_code}")

        return response

    def submit_course_assessment(self, student_number: str, course_id: int, ratings: Dict[int, int], remarks: str = "") -> APIResponse:
        """
        Submit course assessment ratings for a specific course

        Args:
            student_number: The student number
            course_id: The ID of the course being assessed
            ratings: Dictionary mapping question IDs to rating values (1-5)
            remarks: Optional remarks/comments for the course

        Returns:
            APIResponse containing submission result
        """
        if not self._auth_token:
            return APIResponse(
                status_code=401,
                headers={},
                data={'error': 'Authentication required'},
                request_method='POST',
                request_url=self._build_url(self.endpoints['submit_assessment'])
            )

        # Prepare assessment data for this course
        assessment_data = []
        for question_id, score in ratings.items():
            assessment_data.append({
                'questionId': question_id,
                'score': score
            })

        # Prepare submission payload (format matches the actual API)
        payload = {
            'assessments': [{
                'studentNumber': student_number,
                'courseId': course_id,
                'data': assessment_data,
                'remarks': remarks
            }]
        }

        self.logger.info(f"Submitting course assessment for course ID: {course_id}")

        # Debug: Print the actual payload being sent
        import json
        print(f"\n🔍 DEBUG: Payload for course {course_id}:")
        print(json.dumps(payload, indent=2))
        print("=" * 50)

        response = self.post(self.endpoints['submit_assessment'], payload=payload)

        if response.is_success:
            self.logger.info(f"Course assessment submitted successfully for course ID: {course_id}")
        else:
            self.logger.error(f"Failed to submit course assessment for course ID {course_id}: {response.status_code}")

        return response

    def submit_all_course_assessments(self, student_number: str, assessments: List[Dict[str, Any]]) -> APIResponse:
        """
        Submit all course assessments at once (matches web interface behavior)

        Args:
            student_number: Student number for the assessments
            assessments: List of assessment data for all courses
                [
                    {
                        'course_id': int,
                        'ratings': {question_id: score, ...},
                        'remarks': str
                    },
                    ...
                ]

        Returns:
            APIResponse object with submission result
        """
        if not self._auth_token:
            return APIResponse(
                status_code=401,
                headers={},
                data={'error': 'Authentication required'},
                request_method='POST',
                request_url=self._build_url(self.endpoints['submit_assessment'])
            )

        # Prepare payload with all assessments in the correct format for the API
        assessment_list = []
        for assessment in assessments:
            # Prepare assessment data for this course
            assessment_data = []
            for question_id, score in assessment['ratings'].items():
                assessment_data.append({
                    'questionId': question_id,
                    'score': score
                })

            assessment_list.append({
                'studentNumber': student_number,
                'courseId': assessment['course_id'],
                'data': assessment_data,
                'remarks': assessment.get('remarks', '')
            })

        payload = {
            'assessments': assessment_list
        }

        self.logger.info(f"Submitting all course assessments for {len(assessments)} courses")

        # Debug: Print the actual payload being sent
        import json
        print(f"\n🔍 DEBUG: Bulk Assessment Payload ({len(assessments)} courses):")
        print(json.dumps(payload, indent=2))
        print("=" * 80)

        response = self.post(self.endpoints['submit_assessment'], payload=payload)

        if response.is_success:
            self.logger.info(f"All course assessments submitted successfully for {len(assessments)} courses")
        else:
            self.logger.error(f"Failed to submit course assessments: {response.status_code}")

        return response

    def prepare_assessment_submission(self, student_number: str, course_data: Dict[str, Any], ratings: Dict[int, int], remarks: str = "") -> Dict[str, Any]:
        """
        Prepare assessment data for submission

        Args:
            student_number: The student number
            course_data: Course data with questions
            ratings: Dictionary mapping question IDs to rating values
            remarks: Optional remarks/comments for the course

        Returns:
            Dictionary containing assessment data formatted for submission
        """
        assessment_data = []

        for group in course_data.get('assessment_groups', []):
            for question in group.get('questions', []):
                question_id = question.get('id')
                if question_id in ratings:
                    assessment_data.append({
                        'questionId': question_id,
                        'score': ratings[question_id]
                    })

        return {
            'studentNumber': student_number,
            'courseId': course_data.get('id'),
            'data': assessment_data,
            'remarks': remarks
        }

    def validate_assessment_completion(self, course_data: Dict[str, Any], ratings: Dict[int, int]) -> Dict[str, Any]:
        """
        Validate that all required questions have been rated

        Args:
            course_data: Course data with questions
            ratings: Dictionary mapping question IDs to rating values

        Returns:
            Dictionary with validation results
        """
        total_questions = 0
        rated_questions = 0
        missing_questions = []

        for group in course_data.get('assessment_groups', []):
            for question in group.get('questions', []):
                question_id = question.get('id')
                total_questions += 1

                if question_id in ratings and ratings[question_id] is not None:
                    rated_questions += 1
                else:
                    missing_questions.append({
                        'id': question_id,
                        'description': question.get('description', 'N/A'),
                        'category': question.get('category_name', 'N/A'),
                        'number': question.get('number', 0)
                    })

        is_complete = rated_questions == total_questions
        completion_percentage = (rated_questions / total_questions * 100) if total_questions > 0 else 0

        return {
            'is_complete': is_complete,
            'total_questions': total_questions,
            'rated_questions': rated_questions,
            'missing_questions': missing_questions,
            'completion_percentage': completion_percentage
        }

    def parse_assessment_data(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse course assessment response data into a clean format

        Args:
            response_data: Raw API response data

        Returns:
            List of parsed course assessment data
        """
        if not response_data or 'result' not in response_data:
            return []

        courses = []
        for course_data in response_data.get('result', []):
            course = {
                'code': course_data.get('code', 'N/A'),
                'name': course_data.get('name', 'N/A'),
                'credit': course_data.get('credit', 0),
                'id': course_data.get('id'),
                'lecturer': course_data.get('lecturer', 'N/A'),
                'remarks': course_data.get('remarks', ''),
                'assessment_groups': []
            }

            # Parse assessment groups (categories)
            for group_data in course_data.get('groups', []):
                group = {
                    'category_code': group_data.get('categoryCode', 'N/A'),
                    'name': group_data.get('name', 'N/A'),
                    'questions': []
                }

                # Parse questions within each group
                for question_data in group_data.get('questions', []):
                    question = {
                        'id': question_data.get('id'),
                        'description': question_data.get('description', 'N/A'),
                        'number': question_data.get('number', 0),
                        'score': question_data.get('score'),
                        'category_code': question_data.get('categoryCode', 'N/A'),
                        'category_name': question_data.get('categoryName', 'N/A'),
                        'answers': []
                    }

                    # Parse answer options
                    for answer_data in question_data.get('answers', []):
                        answer = {
                            'id': answer_data.get('id'),
                            'label': answer_data.get('label', 'N/A'),
                            'value': answer_data.get('value', 0)
                        }
                        question['answers'].append(answer)

                    group['questions'].append(question)

                course['assessment_groups'].append(group)

            courses.append(course)

        return courses

    def get_assessment_summary(self, courses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of course assessments

        Args:
            courses: List of parsed course assessment data

        Returns:
            Dictionary containing assessment summary
        """
        if not courses:
            return {
                'total_courses': 0,
                'total_questions': 0,
                'assessment_categories': [],
                'lecturers': [],
                'total_credits': 0,
                'courses_by_lecturer': {}
            }

        total_courses = len(courses)
        total_questions = 0
        assessment_categories = set()
        lecturers = set()
        total_credits = 0
        courses_by_lecturer = {}

        for course in courses:
            total_credits += course.get('credit', 0)
            lecturer = course.get('lecturer', 'N/A')
            lecturers.add(lecturer)

            # Group courses by lecturer
            if lecturer not in courses_by_lecturer:
                courses_by_lecturer[lecturer] = []
            courses_by_lecturer[lecturer].append({
                'code': course.get('code', 'N/A'),
                'name': course.get('name', 'N/A'),
                'credit': course.get('credit', 0)
            })

            # Count questions and categories
            for group in course.get('assessment_groups', []):
                assessment_categories.add(group.get('name', 'N/A'))
                total_questions += len(group.get('questions', []))

        return {
            'total_courses': total_courses,
            'total_questions': total_questions,
            'assessment_categories': list(assessment_categories),
            'lecturers': list(lecturers),
            'total_credits': total_credits,
            'courses_by_lecturer': courses_by_lecturer
        }

    def get_assessment_categories_info(self) -> Dict[str, str]:
        """
        Get information about assessment categories

        Returns:
            Dictionary mapping category codes to descriptions
        """
        return {
            'A': 'COURSE PRESENTATION - Evaluates how well the course objectives, content, and assessment methods are presented',
            'B': 'MODE OF DELIVERY - Assesses teaching methods, clarity, pace, and lecturer knowledge',
            'C': "LECTURER'S BEARING IN CLASS - Reviews lecturer's appearance, punctuality, and classroom management",
            'D': 'PEDAGOGY - Evaluates assignments, feedback, tutorials, and overall learning experience'
        }

    def get_question_categories_breakdown(self, courses: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed breakdown of questions by category

        Args:
            courses: List of parsed course assessment data

        Returns:
            Dictionary containing category breakdown
        """
        categories = {}

        for course in courses:
            for group in course.get('assessment_groups', []):
                category_code = group.get('category_code', 'N/A')
                category_name = group.get('name', 'N/A')

                if category_code not in categories:
                    categories[category_code] = {
                        'name': category_name,
                        'total_questions': 0,
                        'courses_count': 0,
                        'sample_questions': []
                    }

                categories[category_code]['total_questions'] += len(group.get('questions', []))
                categories[category_code]['courses_count'] += 1

                # Add sample questions (first 3)
                for i, question in enumerate(group.get('questions', [])[:3]):
                    if len(categories[category_code]['sample_questions']) < 3:
                        categories[category_code]['sample_questions'].append(
                            question.get('description', 'N/A')
                        )

        return categories

    def format_assessment_for_display(self, courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format assessment data for better display

        Args:
            courses: List of parsed course assessment data

        Returns:
            List of formatted course data for display
        """
        formatted_courses = []

        for course in courses:
            formatted_course = {
                'code': course.get('code', 'N/A'),
                'name': course.get('name', 'N/A'),
                'credit': course.get('credit', 0),
                'lecturer': course.get('lecturer', 'N/A'),
                'total_questions': 0,
                'categories': []
            }

            # Process each assessment group/category
            for group in course.get('assessment_groups', []):
                category = {
                    'code': group.get('category_code', 'N/A'),
                    'name': group.get('name', 'N/A'),
                    'question_count': len(group.get('questions', [])),
                    'questions': []
                }

                formatted_course['total_questions'] += category['question_count']

                # Format questions
                for question in group.get('questions', []):
                    formatted_question = {
                        'number': question.get('number', 0),
                        'description': question.get('description', 'N/A'),
                        'current_score': question.get('score'),
                        'answer_options': []
                    }

                    # Format answer options
                    for answer in question.get('answers', []):
                        formatted_question['answer_options'].append({
                            'value': answer.get('value', 0),
                            'label': answer.get('label', 'N/A')
                        })

                    category['questions'].append(formatted_question)

                formatted_course['categories'].append(category)

            formatted_courses.append(formatted_course)

        return formatted_courses