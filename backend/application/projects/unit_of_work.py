from __future__ import annotations

from abc import abstractmethod

from application.common.unit_of_work import UnitOfWork
from application.projects.repositories import ProjectRepository
from application.workspaces.repositories import WorkspaceRepository


class ProjectUnitOfWork(UnitOfWork):
    @property
    @abstractmethod
    def projects(self) -> ProjectRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def workspaces(self) -> WorkspaceRepository:
        raise NotImplementedError