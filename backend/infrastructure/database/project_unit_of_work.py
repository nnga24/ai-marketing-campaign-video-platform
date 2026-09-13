from application.projects.repositories import ProjectRepository
from application.projects.unit_of_work import ProjectUnitOfWork
from infrastructure.database.repositories.projects import (
    SQLAlchemyProjectRepository,
)
from infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class SQLAlchemyProjectUnitOfWork(
    SQLAlchemyUnitOfWork,
    ProjectUnitOfWork,
):
    @property
    def projects(self) -> ProjectRepository:
        session = self._require_session()

        return SQLAlchemyProjectRepository(session)