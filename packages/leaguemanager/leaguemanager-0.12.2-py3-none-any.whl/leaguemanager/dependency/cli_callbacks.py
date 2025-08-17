from __future__ import annotations

import typer
from sqlalchemy.orm import Session

from leaguemanager.dependency import LeagueManager
from leaguemanager.services._typing import (
    ImporterT,
    SQLAlchemyAsyncConfigT,
    SQLAlchemySyncConfigT,
    SyncRepositoryT,
    SyncServiceT,
)

registry = LeagueManager()


def provide_manager_service(param: typer.CallbackParam) -> SyncServiceT | SyncRepositoryT:
    return registry.provide_db_service(service_type=param.type.func)


def provide_sync_db_session() -> Session:
    return registry.provide_sync_session


def provide_sync_db_config() -> SQLAlchemySyncConfigT:
    """Provide the synchronous SQLAlchemy configuration."""
    return registry.provide_sync_config


def provide_async_db_config() -> SQLAlchemyAsyncConfigT:
    """Provide the asynchronous SQLAlchemy configuration."""
    return registry.provide_async_config


def provide_importer_service(param: typer.CallbackParam) -> ImporterT:
    """Provide an importer service based on the type specified in the callback parameter."""
    importer_type = param.type.func
    return registry.provide_importer_service(importer_type=importer_type)


def provide_scheduler_service(param: typer.CallbackParam) -> SyncServiceT:
    """Provide a scheduling service based on the type specified in the callback parameter."""
    scheduler_type = param.type.func
    return registry.provide_scheduler_service(scheduler_type=scheduler_type)
