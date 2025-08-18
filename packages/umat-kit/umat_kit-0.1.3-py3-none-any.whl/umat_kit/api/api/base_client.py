"""
Base API Client for UMAT Testing Framework
Provides comprehensive HTTP client with advanced features for API testing
"""

import requests
import time
import json
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urljoin, urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ...config import config
from ...utils.utils.logger import get_logger, get_api_logger, get_performance_logger
from ...utils.utils.validators import data_validator, ValidationResult
from ...utils.utils.terminal_colors import colored_output

@dataclass
class APIResponse:
    """Comprehensive API response wrapper"""
    status_code: int
    headers: Dict[str, str]
    data: Optional[Union[Dict[str, Any], List[Any]]] = None
    raw_content: Optional[str] = None
    response_time: float = 0.0
    request_url: str = ""
    request_method: str = ""
    request_headers: Dict[str, str] = field(default_factory=dict)
    request_payload: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    validation_result: Optional[ValidationResult] = None
    error_message: Optional[str] = None

    @property
    def is_success(self) -> bool:
        """Check if response indicates success"""
        return 200 <= self.status_code < 300

    @property
    def is_client_error(self) -> bool:
        """Check if response indicates client error"""
        return 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        """Check if response indicates server error"""
        return 500 <= self.status_code < 600

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            'status_code': self.status_code,
            'headers': dict(self.headers),
            'data': self.data,
            'response_time': self.response_time,
            'request_url': self.request_url,
            'request_method': self.request_method,
            'timestamp': self.timestamp.isoformat(),
            'is_success': self.is_success
        }

    def __str__(self) -> str:
        """String representation of response"""
        status_emoji = "✅" if self.is_success else "❌"
        return f"{status_emoji} {self.request_method} {self.request_url} -> {self.status_code} ({self.response_time:.3f}s)"

class BaseAPIClient:
    """Advanced base API client with comprehensive features"""

    def __init__(self, base_url: Optional[str] = None, timeout: int = 30, max_retries: int = 3):
        self.base_url = base_url or config.api.base_url
        self.timeout = timeout
        self.max_retries = max_retries

        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Default headers
        self.default_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'UMAT-API-Tester/1.0'
        }

        # Authentication token storage
        self._auth_token: Optional[str] = None

        # Logging setup
        self.logger = get_logger(self.__class__.__name__)
        self.api_logger = get_api_logger(self.__class__.__name__)
        self.perf_logger = get_performance_logger(self.__class__.__name__)

        # Request/Response history
        self.request_history: List[APIResponse] = []
        self.max_history_size = 100

    def set_auth_token(self, token: str) -> None:
        """Set authentication token for requests"""
        self._auth_token = token
        self.session.headers.update({'Authorization': f'Bearer {token}'})
        self.logger.info("Authentication token updated")

    def clear_auth_token(self) -> None:
        """Clear authentication token"""
        self._auth_token = None
        self.session.headers.pop('Authorization', None)
        self.logger.info("Authentication token cleared")

    def _build_url(self, endpoint: str) -> str:
        """Build complete URL from endpoint"""
        if endpoint.startswith(('http://', 'https://')):
            return endpoint
        return urljoin(self.base_url, endpoint.lstrip('/'))

    def _prepare_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Prepare request headers"""
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)
        return request_headers

    def _log_request(self, method: str, url: str, headers: Dict[str, str],
                    payload: Optional[Dict[str, Any]] = None) -> None:
        """Log request details (file only - no terminal output for clean UI)"""
        self.api_logger.log_request(method, url, headers, payload)

    def _log_response(self, response: APIResponse) -> None:
        """Log response details (file only - no terminal output for clean UI)"""
        self.api_logger.log_response(
            response.status_code,
            response.response_time,
            response.data
        )

    def _validate_response(self, response: APIResponse,
                          expected_fields: Optional[List[str]] = None) -> ValidationResult:
        """Validate response data"""
        validations = [
            (data_validator.validate_http_status, response.status_code),
            (data_validator.validate_response_time, response.response_time)
        ]

        if response.data and expected_fields:
            validations.append(
                (data_validator.validate_api_response, response.data, expected_fields)
            )

        return data_validator.batch_validate(validations)

    def _add_to_history(self, response: APIResponse) -> None:
        """Add response to request history"""
        self.request_history.append(response)

        # Maintain history size limit
        if len(self.request_history) > self.max_history_size:
            self.request_history = self.request_history[-self.max_history_size:]

    def _make_request(self, method: str, endpoint: str,
                     headers: Optional[Dict[str, str]] = None,
                     payload: Optional[Dict[str, Any]] = None,
                     params: Optional[Dict[str, Any]] = None,
                     expected_fields: Optional[List[str]] = None) -> APIResponse:
        """Make HTTP request with comprehensive logging and validation"""

        url = self._build_url(endpoint)
        request_headers = self._prepare_headers(headers)

        # Log request
        self._log_request(method, url, request_headers, payload)

        # Start performance timing
        start_time = time.time()

        try:
            # Make request
            response = self.session.request(
                method=method,
                url=url,
                headers=request_headers,
                json=payload,
                params=params,
                timeout=self.timeout
            )

            response_time = time.time() - start_time

            # Parse response data
            response_data = None
            raw_content = response.text

            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    response_data = response.json()
                except json.JSONDecodeError:
                    self.logger.warning("Failed to parse JSON response")

            # Create API response object
            api_response = APIResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                data=response_data,
                raw_content=raw_content,
                response_time=response_time,
                request_url=url,
                request_method=method,
                request_headers=request_headers,
                request_payload=payload
            )

            # Validate response
            api_response.validation_result = self._validate_response(api_response, expected_fields)

            # Log response
            self._log_response(api_response)

            # Add to history
            self._add_to_history(api_response)

            return api_response

        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            self.logger.error(f"Request timeout after {self.timeout}s")
            return APIResponse(
                status_code=408,  # Request Timeout
                headers={},
                data=None,
                raw_content="Request timeout",
                response_time=response_time,
                request_url=url,
                request_method=method,
                error_message=f"Request timeout after {self.timeout}s"
            )
        except requests.exceptions.ConnectionError as e:
            response_time = time.time() - start_time
            self.logger.error(f"Connection error: {str(e)}")
            # Determine specific error type
            error_msg = str(e)
            if "502" in error_msg:
                status_code = 502
                user_msg = "Server is temporarily unavailable (502 Bad Gateway)"
            elif "503" in error_msg:
                status_code = 503
                user_msg = "Service temporarily unavailable (503)"
            elif "Max retries exceeded" in error_msg:
                status_code = 503
                user_msg = "Server is not responding - please try again later"
            else:
                status_code = 503
                user_msg = "Unable to connect to server"

            return APIResponse(
                status_code=status_code,
                headers={},
                data=None,
                raw_content=error_msg,
                response_time=response_time,
                request_url=url,
                request_method=method,
                error_message=user_msg
            )
        except Exception as e:
            response_time = time.time() - start_time
            self.logger.error(f"Request failed: {str(e)}")
            return APIResponse(
                status_code=500,
                headers={},
                data=None,
                raw_content=str(e),
                response_time=response_time,
                request_url=url,
                request_method=method,
                error_message=f"Unexpected error: {str(e)}"
            )

    def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, Any]] = None,
            expected_fields: Optional[List[str]] = None) -> APIResponse:
        """Make GET request"""
        return self._make_request('GET', endpoint, headers, None, params, expected_fields)

    def post(self, endpoint: str, payload: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None,
             expected_fields: Optional[List[str]] = None) -> APIResponse:
        """Make POST request"""
        return self._make_request('POST', endpoint, headers, payload, None, expected_fields)

    def put(self, endpoint: str, payload: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            expected_fields: Optional[List[str]] = None) -> APIResponse:
        """Make PUT request"""
        return self._make_request('PUT', endpoint, headers, payload, None, expected_fields)

    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None,
               expected_fields: Optional[List[str]] = None) -> APIResponse:
        """Make DELETE request"""
        return self._make_request('DELETE', endpoint, headers, None, None, expected_fields)

    def patch(self, endpoint: str, payload: Optional[Dict[str, Any]] = None,
              headers: Optional[Dict[str, str]] = None,
              expected_fields: Optional[List[str]] = None) -> APIResponse:
        """Make PATCH request"""
        return self._make_request('PATCH', endpoint, headers, payload, None, expected_fields)

    def get_last_response(self) -> Optional[APIResponse]:
        """Get the last API response"""
        return self.request_history[-1] if self.request_history else None

    def get_successful_responses(self) -> List[APIResponse]:
        """Get all successful responses from history"""
        return [r for r in self.request_history if r.is_success]

    def get_failed_responses(self) -> List[APIResponse]:
        """Get all failed responses from history"""
        return [r for r in self.request_history if not r.is_success]

    def clear_history(self) -> None:
        """Clear request history"""
        self.request_history.clear()
        self.logger.info("Request history cleared")

    def print_history_summary(self) -> None:
        """Print summary of request history"""
        if not self.request_history:
            colored_output.print_info("No requests in history")
            return

        total_requests = len(self.request_history)
        successful_requests = len(self.get_successful_responses())
        failed_requests = len(self.get_failed_responses())
        avg_response_time = sum(r.response_time for r in self.request_history) / total_requests

        colored_output.print_header("Request History Summary")
        colored_output.print_info(f"Total Requests: {total_requests}")
        colored_output.print_success(f"Successful: {successful_requests}")
        colored_output.print_error(f"Failed: {failed_requests}")
        colored_output.print_info(f"Average Response Time: {avg_response_time:.3f}s")

        # Show recent requests
        recent_requests = self.request_history[-5:]
        colored_output.print_info("\nRecent Requests:")
        for response in recent_requests:
            print(f"  {response}")