"""Project-related models."""

from typing import Optional, List
from datetime import datetime
from pydantic import Field

from mindzie_api.models.base import BaseModel, TimestampedModel, NamedResource, PaginatedResponse


class Project(TimestampedModel, NamedResource):
    """Project model."""
    
    project_id: str = Field(description="Project unique identifier", alias="ProjectId")
    tenant_id: str = Field(description="Tenant unique identifier", alias="TenantId")
    project_name: str = Field(description="Project name", alias="ProjectName")
    project_description: Optional[str] = Field(default=None, description="Project description", alias="ProjectDescription")
    is_active: bool = Field(default=True, description="Whether project is active", alias="IsActive")
    dataset_count: int = Field(default=0, description="Number of datasets", alias="DatasetCount")
    investigation_count: int = Field(default=0, description="Number of investigations", alias="InvestigationCount")
    dashboard_count: int = Field(default=0, description="Number of dashboards", alias="DashboardCount")
    user_count: int = Field(default=0, description="Number of users", alias="UserCount")
    
    # Override from NamedResource to use project_name
    @property
    def name(self) -> str:
        return self.project_name
    
    @property
    def description(self) -> Optional[str]:
        return self.project_description


class ProjectListResponse(PaginatedResponse[Project]):
    """Response for project list endpoint."""
    
    projects: List[Project] = Field(default_factory=list, description="List of projects", alias="Projects")
    
    @property
    def items(self) -> List[Project]:
        return self.projects


class ProjectSummary(BaseModel):
    """Project summary model."""
    
    project_id: str = Field(description="Project unique identifier", alias="ProjectId")
    tenant_id: str = Field(description="Tenant unique identifier", alias="TenantId")
    project_name: str = Field(description="Project name", alias="ProjectName")
    total_datasets: int = Field(default=0, description="Total datasets", alias="TotalDatasets")
    total_investigations: int = Field(default=0, description="Total investigations", alias="TotalInvestigations")
    total_dashboards: int = Field(default=0, description="Total dashboards", alias="TotalDashboards")
    total_actions: int = Field(default=0, description="Total actions", alias="TotalActions")
    total_users: int = Field(default=0, description="Total users", alias="TotalUsers")
    last_activity: Optional[datetime] = Field(default=None, description="Last activity timestamp", alias="LastActivity")
    storage_used_mb: float = Field(default=0.0, description="Storage used in MB", alias="StorageUsedMB")