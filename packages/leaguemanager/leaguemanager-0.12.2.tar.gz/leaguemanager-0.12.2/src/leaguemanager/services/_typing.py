from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from advanced_alchemy.config import SQLAlchemyAsyncConfig, SQLAlchemySyncConfig
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService
from sqlalchemy.ext.asyncio import AsyncSession

from leaguemanager.models.base import UUIDBase
from leaguemanager.services.scheduling import (
    BracketSchedule,
    RoundRobinPlayoffSchedule,
    RoundRobinSchedule,
    TournamentSchedule,
)
from leaguemanager.services.template_loader.league_importer import Importer

ModelT = TypeVar("ModelT", bound=UUIDBase)
SyncRepositoryT = TypeVar("RepositoryT", bound=SQLAlchemySyncRepository)
AsyncRepositoryT = TypeVar("RepositoryT", bound=SQLAlchemyAsyncRepository)
SyncServiceT = TypeVar("ServiceT", bound=SQLAlchemySyncRepositoryService[ModelT])
AsyncServiceT = TypeVar("ServiceT", bound=SQLAlchemyAsyncRepositoryService[ModelT])
AsyncSessionT = TypeVar("AsyncSessionT", bound=AsyncSession)
SQLAlchemySyncConfigT = TypeVar("SQLAlchemySyncConfigT", bound=SQLAlchemySyncConfig)
SQLAlchemyAsyncConfigT = TypeVar("SQLAlchemyAsyncConfigT", bound=SQLAlchemyAsyncConfig)
ImporterT = TypeVar("ImporterT", bound=Importer)
ScheduleServiceT = TypeVar(
    "ScheduleServiceT", bound=BracketSchedule | RoundRobinSchedule | RoundRobinPlayoffSchedule | TournamentSchedule
)
