"""Investigation controller for Mindzie API."""

from typing import Optional, Dict, Any, List
import logging

from mindzie_api.controllers import BaseController
from mindzie_api.utils import validate_guid, build_query_params

logger = logging.getLogger(__name__)


class InvestigationController(BaseController):
    """Controller for investigation-related API endpoints."""
    
    def ping_unauthorized(self, project_id: str) -> str:
        """Test connectivity without authentication.
        
        Args:
            project_id: Project ID
            
        Returns:
            Ping response message
        """
        response = self._request("GET", "investigation/unauthorized-ping", project_id=project_id)
        return response if isinstance(response, str) else response.get("data", "Ping Successful")
    
    def ping(self, project_id: str) -> str:
        """Test authenticated connectivity.
        
        Args:
            project_id: Project ID
            
        Returns:
            Ping response message
        """
        response = self._request("GET", "investigation/ping", project_id=project_id)
        return response if isinstance(response, str) else response.get("data", "Ping Successful")

    def get_all(self, project_id: str, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """Get all investigations for a project."""
        params = build_query_params(page=page, page_size=page_size)
        return self._request("GET", "investigation", project_id=project_id, params=params)
    
    def get_by_id(self, project_id: str, investigation_id: str) -> Dict[str, Any]:
        """Get investigation by ID."""
        return self._request("GET", f"investigation/{investigation_id}", project_id=project_id)
    
    def create(self, project_id: str, **kwargs) -> Dict[str, Any]:
        """Create new investigation."""
        return self._request("POST", "investigation", project_id=project_id, json_data=kwargs)
    
    def update(self, project_id: str, investigation_id: str, **kwargs) -> Dict[str, Any]:
        """Update investigation."""
        return self._request("PUT", f"investigation/{investigation_id}", project_id=project_id, json_data=kwargs)
    
    def delete(self, project_id: str, investigation_id: str) -> Dict[str, Any]:
        """Delete investigation."""
        return self._request("DELETE", f"investigation/{investigation_id}", project_id=project_id)
    
    def get_notebooks(self, project_id: str, investigation_id: str) -> Dict[str, Any]:
        """Get notebooks for investigation."""
        return self._request("GET", f"investigation/{investigation_id}/notebooks", project_id=project_id)
    
    def get_main_notebook(self, project_id: str, investigation_id: str) -> Dict[str, Any]:
        """Get main notebook for investigation."""
        return self._request("GET", f"investigation/{investigation_id}/main-notebook", project_id=project_id)
