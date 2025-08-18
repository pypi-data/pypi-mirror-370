from typing import Any, Optional

from .project import ProjectManager


class RegistryManager:
    """
    Registry manager for project CRUD operations.

    Provides methods to create, retrieve, update, and list projects.
    All methods return Project entities that give access to project-scoped operations.
    """

    def __init__(self, adapter: Any) -> None:
        """
        Args:
            adapter: adapter (FluidizeSDK or LocalAdapter)
        """
        self.adapter = adapter

    def create(
        self,
        project_id: str,
        label: str = "",
        description: str = "",
        location: str = "",
        status: str = "",
    ) -> ProjectManager:
        """
        Create a new project.

        Args:
            project_id: Unique identifier for the project
            label: Display label for the project
            description: Project description
            location: Project location
            status: Project status

        Returns:
            Created project wrapped in Project class
        """
        project_summary = self.adapter.projects.upsert(
            id=project_id,
            label=label,
            description=description,
            location=location,
            status=status,
        )
        return ProjectManager(self.adapter, project_summary)

    def get(self, project_id: str) -> ProjectManager:
        """
        Get a project by ID.

        Args:
            project_id: The project ID

        Returns:
            Project wrapped in Project class
        """
        project_summary = self.adapter.projects.retrieve(project_id)
        return ProjectManager(self.adapter, project_summary)

    def list(self) -> list[ProjectManager]:
        """
        List all projects.

        Returns:
            List of projects wrapped in Project class
        """
        project_summaries = self.adapter.projects.list()
        return [ProjectManager(self.adapter, summary) for summary in project_summaries]

    def update(
        self,
        project_id: str,
        label: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[str] = None,
    ) -> ProjectManager:
        """
        Update an existing project.

        Args:
            project_id: The project ID to update
            label: New label
            description: New description
            location: New location
            status: New status

        Returns:
            Updated project wrapped in Project class
        """
        # Build update data, only include non-None values
        update_data = {"id": project_id}
        if label is not None:
            update_data["label"] = label
        if description is not None:
            update_data["description"] = description
        if location is not None:
            update_data["location"] = location
        if status is not None:
            update_data["status"] = status

        project_summary = self.adapter.projects.upsert(**update_data)
        return ProjectManager(self.adapter, project_summary)
