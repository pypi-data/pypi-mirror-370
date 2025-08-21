"""Main API client for Mindzie Studio."""

import os
import time
import logging
from typing import Optional, Dict, Any, Union, BinaryIO
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from mindzie_api.__version__ import __version__
from mindzie_api.auth import AuthProvider, create_auth_provider
from mindzie_api.constants import (
    AuthType, DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY, HTTP_OK, HTTP_CREATED, HTTP_ACCEPTED,
    HTTP_NO_CONTENT, HTTP_BAD_REQUEST, HTTP_UNAUTHORIZED,
    HTTP_FORBIDDEN, HTTP_NOT_FOUND, HTTP_RATE_LIMIT,
    HTTP_SERVER_ERROR
)
from mindzie_api.exceptions import (
    MindzieAPIException, AuthenticationError, ValidationError,
    NotFoundError, ServerError, RateLimitError, TimeoutError,
    ConnectionError
)
from mindzie_api.utils import calculate_retry_delay, parse_error_response

# Import controllers
from mindzie_api.controllers.project import ProjectController
from mindzie_api.controllers.dataset import DatasetController
from mindzie_api.controllers.investigation import InvestigationController
from mindzie_api.controllers.notebook import NotebookController
from mindzie_api.controllers.block import BlockController
from mindzie_api.controllers.execution import ExecutionController
from mindzie_api.controllers.enrichment import EnrichmentController
from mindzie_api.controllers.dashboard import DashboardController
from mindzie_api.controllers.action import ActionController
from mindzie_api.controllers.actionexecution import ActionExecutionController
from mindzie_api.controllers.ping import PingController
from mindzie_api.controllers.copilot import CopilotController

logger = logging.getLogger(__name__)


class MindzieAPIClient:
    """Main client for interacting with the Mindzie Studio API."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        auth_type: AuthType = AuthType.API_KEY,
        auth_provider: Optional[AuthProvider] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        verify_ssl: bool = True,
        proxies: Optional[Dict[str, str]] = None,
        **auth_kwargs
    ):
        """Initialize the Mindzie API client.
        
        Args:
            base_url: Base URL of the API (e.g., https://dev.mindziestudio.com)
            tenant_id: Tenant ID for multi-tenant operations
            auth_type: Type of authentication to use
            auth_provider: Custom auth provider (overrides auth_type)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            verify_ssl: Whether to verify SSL certificates
            proxies: Proxy configuration
            **auth_kwargs: Additional arguments for auth provider
        """
        # Get configuration from environment if not provided
        self.base_url = (base_url or os.getenv("MINDZIE_API_URL", "https://dev.mindziestudio.com")).rstrip("/")
        self.tenant_id = tenant_id or os.getenv("MINDZIE_TENANT_ID")
        
        if not self.tenant_id:
            raise ValueError("Tenant ID is required. Provide it directly or set MINDZIE_TENANT_ID environment variable.")
        
        # Set up authentication
        self.auth_provider = auth_provider or create_auth_provider(auth_type, **auth_kwargs)
        
        # Configure session
        self.timeout = timeout
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl
        self.proxies = proxies
        
        # Create session with retry strategy
        self.session = self._create_session()
        
        # Initialize controllers
        self._init_controllers()
        
        logger.info(f"Mindzie API client initialized for {self.base_url}")
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry configuration."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=DEFAULT_RETRY_DELAY,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            "User-Agent": f"mindzie-api-python/{__version__}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        
        # Add authentication headers
        session.headers.update(self.auth_provider.get_headers())
        
        # Set SSL verification
        session.verify = self.verify_ssl
        
        # Set proxies if provided
        if self.proxies:
            session.proxies.update(self.proxies)
        
        return session
    
    def _init_controllers(self) -> None:
        """Initialize API controllers."""
        self.projects = ProjectController(self)
        self.datasets = DatasetController(self)
        self.investigations = InvestigationController(self)
        self.notebooks = NotebookController(self)
        self.blocks = BlockController(self)
        self.execution = ExecutionController(self)
        self.enrichments = EnrichmentController(self)
        self.dashboards = DashboardController(self)
        self.actions = ActionController(self)
        self.action_executions = ActionExecutionController(self)
        self.ping = PingController(self)
        self.copilot = CopilotController(self)
    
    def request(
        self,
        method: str,
        endpoint: str,
        project_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], BinaryIO]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            project_id: Project ID for the request
            params: Query parameters
            json_data: JSON body data
            files: Files to upload
            data: Form data or binary data
            headers: Additional headers
            timeout: Request timeout override
            **kwargs: Additional request arguments
        
        Returns:
            Response data dictionary
        
        Raises:
            MindzieAPIException: On API errors
        """
        # Build URL
        if project_id:
            url = f"{self.base_url}/api/{self.tenant_id}/{project_id}/{endpoint.lstrip('/')}"
        elif endpoint.startswith("api/"):
            url = f"{self.base_url}/{endpoint}"
        else:
            url = f"{self.base_url}/api/{self.tenant_id}/{endpoint.lstrip('/')}"
        
        # Prepare request
        request_kwargs = {
            "method": method,
            "url": url,
            "params": params,
            "timeout": timeout or self.timeout
        }
        
        if json_data is not None:
            request_kwargs["json"] = json_data
        elif files is not None:
            request_kwargs["files"] = files
            # Remove Content-Type header for multipart/form-data
            if headers is None:
                headers = {}
            headers.pop("Content-Type", None)
        elif data is not None:
            request_kwargs["data"] = data
        
        if headers:
            request_kwargs["headers"] = {**self.session.headers, **headers}
        
        request_kwargs.update(kwargs)
        
        # Make request with retries
        attempt = 0
        last_error = None
        
        while attempt < self.max_retries:
            try:
                logger.debug(f"Making {method} request to {url}")
                response = self.session.request(**request_kwargs)
                
                # Handle response
                return self._handle_response(response)
                
            except requests.exceptions.Timeout as e:
                last_error = TimeoutError(f"Request timed out: {str(e)}")
                attempt += 1
                if attempt < self.max_retries:
                    delay = calculate_retry_delay(attempt)
                    logger.warning(f"Request timed out, retrying in {delay:.2f}s (attempt {attempt}/{self.max_retries})")
                    time.sleep(delay)
                    
            except requests.exceptions.ConnectionError as e:
                last_error = ConnectionError(f"Connection failed: {str(e)}")
                attempt += 1
                if attempt < self.max_retries:
                    delay = calculate_retry_delay(attempt)
                    logger.warning(f"Connection failed, retrying in {delay:.2f}s (attempt {attempt}/{self.max_retries})")
                    time.sleep(delay)
                    
            except requests.exceptions.RequestException as e:
                last_error = MindzieAPIException(f"Request failed: {str(e)}")
                break
        
        # Raise the last error if all retries failed
        if last_error:
            raise last_error
        
        raise MindzieAPIException("Request failed after all retries")
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response.
        
        Args:
            response: HTTP response object
        
        Returns:
            Response data dictionary
        
        Raises:
            MindzieAPIException: On API errors
        """
        # Extract request ID if available
        request_id = response.headers.get("X-Request-Id")
        
        # Handle successful responses
        if response.status_code in [HTTP_OK, HTTP_CREATED, HTTP_ACCEPTED]:
            try:
                return response.json()
            except ValueError:
                # Return text response if not JSON
                return {"data": response.text, "status_code": response.status_code}
        
        # Handle no content
        if response.status_code == HTTP_NO_CONTENT:
            return {"success": True, "status_code": response.status_code}
        
        # Handle errors
        error_data = parse_error_response(response.text)
        error_message = error_data.get("error", response.reason)
        
        if response.status_code == HTTP_BAD_REQUEST:
            raise ValidationError(error_message, response.status_code, error_data, request_id)
        elif response.status_code == HTTP_UNAUTHORIZED:
            raise AuthenticationError(error_message, response.status_code, error_data, request_id)
        elif response.status_code == HTTP_FORBIDDEN:
            raise AuthenticationError(f"Forbidden: {error_message}", response.status_code, error_data, request_id)
        elif response.status_code == HTTP_NOT_FOUND:
            raise NotFoundError(error_message, response.status_code, error_data, request_id)
        elif response.status_code == HTTP_RATE_LIMIT:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(error_message, retry_after, status_code=response.status_code, response_data=error_data, request_id=request_id)
        elif response.status_code >= HTTP_SERVER_ERROR:
            raise ServerError(error_message, response.status_code, error_data, request_id)
        else:
            raise MindzieAPIException(error_message, response.status_code, error_data, request_id)
    
    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()