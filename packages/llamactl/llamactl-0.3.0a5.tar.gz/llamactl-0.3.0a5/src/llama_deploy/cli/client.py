from typing import List, Optional

import httpx
from llama_deploy.core.schema.deployments import (
    DeploymentCreate,
    DeploymentResponse,
    DeploymentsListResponse,
    DeploymentUpdate,
)
from llama_deploy.core.schema.git_validation import (
    RepositoryValidationRequest,
    RepositoryValidationResponse,
)
from llama_deploy.core.schema.projects import ProjectsListResponse, ProjectSummary
from rich.console import Console

from .config import config_manager


class BaseClient:
    def __init__(self, base_url: str, console: Console) -> None:
        self.base_url = base_url.rstrip("/")
        self.console = console
        self.client = httpx.Client(
            base_url=self.base_url, event_hooks={"response": [self._handle_response]}
        )

    def _handle_response(self, response: httpx.Response) -> None:
        if "X-Warning" in response.headers:
            self.console.print(
                f"[yellow]Warning: {response.headers['X-Warning']}[/yellow]"
            )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            try:
                response.read()
                error_data = e.response.json()
                if isinstance(error_data, dict) and "detail" in error_data:
                    error_message = error_data["detail"]
                else:
                    error_message = str(error_data)
            except (ValueError, KeyError):
                error_message = e.response.text
            raise Exception(f"HTTP {e.response.status_code}: {error_message}") from e
        except httpx.RequestError as e:
            raise Exception(f"Request failed: {e}") from e


class ControlPlaneClient(BaseClient):
    """Unscoped client for non-project endpoints."""

    def health_check(self) -> dict:
        response = self.client.get("/health")
        return response.json()

    def server_version(self) -> dict:
        response = self.client.get("/version")
        return response.json()

    def list_projects(self) -> List[ProjectSummary]:
        response = self.client.get("/projects/")
        projects_response = ProjectsListResponse.model_validate(response.json())
        return [project for project in projects_response.projects]


class ProjectClient(BaseClient):
    """Project-scoped client for deployment operations."""

    def __init__(
        self,
        base_url: str | None = None,
        project_id: str | None = None,
        console: Console | None = None,
    ) -> None:
        # Allow default construction using active profile (for tests and convenience)
        if base_url is None or project_id is None:
            profile = config_manager.get_current_profile()
            if not profile:
                # Match previous behavior for missing profiles
                (console or Console()).print(
                    "\n[bold red]No profile configured![/bold red]"
                )
                (console or Console()).print("\nTo get started, create a profile with:")
                (console or Console()).print("[cyan]llamactl profile create[/cyan]")
                raise SystemExit(1)
            base_url = base_url or profile.api_url or ""
            project_id = project_id or profile.active_project_id
        if not base_url:
            raise ValueError("API URL is required")
        if not project_id:
            raise ValueError("Project ID is required")
        resolved_console = console or Console()
        super().__init__(base_url, resolved_console)
        self.project_id = project_id

    def list_deployments(self) -> List[DeploymentResponse]:
        response = self.client.get(f"/{self.project_id}/deployments/")
        deployments_response = DeploymentsListResponse.model_validate(response.json())
        return [deployment for deployment in deployments_response.deployments]

    def get_deployment(self, deployment_id: str) -> DeploymentResponse:
        response = self.client.get(f"/{self.project_id}/deployments/{deployment_id}")
        return DeploymentResponse.model_validate(response.json())

    def create_deployment(
        self, deployment_data: DeploymentCreate
    ) -> DeploymentResponse:
        response = self.client.post(
            f"/{self.project_id}/deployments/",
            json=deployment_data.model_dump(exclude_none=True),
        )
        return DeploymentResponse.model_validate(response.json())

    def delete_deployment(self, deployment_id: str) -> None:
        self.client.delete(f"/{self.project_id}/deployments/{deployment_id}")

    def update_deployment(
        self,
        deployment_id: str,
        update_data: DeploymentUpdate,
    ) -> DeploymentResponse:
        response = self.client.patch(
            f"/{self.project_id}/deployments/{deployment_id}",
            json=update_data.model_dump(),
        )
        return DeploymentResponse.model_validate(response.json())

    def validate_repository(
        self,
        repo_url: str,
        deployment_id: str | None = None,
        pat: str | None = None,
    ) -> RepositoryValidationResponse:
        response = self.client.post(
            f"/{self.project_id}/deployments/validate-repository",
            json=RepositoryValidationRequest(
                repository_url=repo_url,
                deployment_id=deployment_id,
                pat=pat,
            ).model_dump(),
        )
        return RepositoryValidationResponse.model_validate(response.json())


def get_control_plane_client(base_url: str | None = None) -> ControlPlaneClient:
    console = Console()
    profile = config_manager.get_current_profile()
    if not profile and not base_url:
        console.print("\n[bold red]No profile configured![/bold red]")
        console.print("\nTo get started, create a profile with:")
        console.print("[cyan]llamactl profile create[/cyan]")
        raise SystemExit(1)
    resolved_base_url = (base_url or (profile.api_url if profile else "")).rstrip("/")
    if not resolved_base_url:
        raise ValueError("API URL is required")
    return ControlPlaneClient(resolved_base_url, console)


def get_project_client(
    base_url: str | None = None, project_id: str | None = None
) -> ProjectClient:
    console = Console()
    profile = config_manager.get_current_profile()
    if not profile:
        console.print("\n[bold red]No profile configured![/bold red]")
        console.print("\nTo get started, create a profile with:")
        console.print("[cyan]llamactl profile create[/cyan]")
        raise SystemExit(1)
    resolved_base_url = (base_url or profile.api_url or "").rstrip("/")
    if not resolved_base_url:
        raise ValueError("API URL is required")
    resolved_project_id = project_id or profile.active_project_id
    if not resolved_project_id:
        raise ValueError("Project ID is required")
    return ProjectClient(resolved_base_url, resolved_project_id, console)
