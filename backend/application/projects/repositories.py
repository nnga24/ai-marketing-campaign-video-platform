from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from modules.projects.models import Project


class ProjectRepository(ABC):
    @abstractmethod
    def get_by_id(
        self,
        project_id: UUID,
    ) -> Project | None:
        raise NotImplementedError

    @abstractmethod
    def add(
        self,
        project: Project,
    ) -> None:
        raise NotImplementedError