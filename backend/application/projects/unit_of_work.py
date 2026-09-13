from __future__ import annotations

from abc import abstractmethod

from application.common.unit_of_work import UnitOfWork
from application.projects.repositories import ProjectRepository


class ProjectUnitOfWork(UnitOfWork):
    @property
    @abstractmethod
    def projects(self) -> ProjectRepository:
        raise NotImplementedError