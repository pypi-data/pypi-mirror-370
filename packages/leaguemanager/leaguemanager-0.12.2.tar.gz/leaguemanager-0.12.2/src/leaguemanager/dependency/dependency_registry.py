from contextlib import asynccontextmanager, contextmanager
from logging import config
from pathlib import Path
from typing import Any, AsyncGenerator, Generator

from advanced_alchemy.config import SQLAlchemyAsyncConfig, SQLAlchemySyncConfig
from attrs import define, field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from svcs import Container, Registry

# from leaguemanager.core import get_settings
from leaguemanager.db import async_config, sync_config
from leaguemanager.dependency.loader import DynamicObjectLoader
from leaguemanager.dependency.managers import (
    ImporterManagement,
    SchedulerManagement,
    ServiceManagement,
    service_provider,
)
from leaguemanager.lib.settings import get_settings
from leaguemanager.lib.toolbox import module_to_os_path
from leaguemanager.services._typing import (
    AsyncServiceT,
    AsyncSessionT,
    ImporterT,
    ScheduleServiceT,
    SQLAlchemyAsyncConfigT,
    SQLAlchemySyncConfigT,
    SyncServiceT,
)

__all__ = ["LeagueManager"]

get_settings.cache_clear()
settings = get_settings()


@define
class LeagueManager:
    """Registry for managing services.

    TODO: Serve up async repos/services

    If no `Registry` is provided, one will be created. Keep in mind that there should only
    be one registry per application.

    Services are kept in an svcs `Container` and are provided as needed. This includes a
    database session, League Manager "repositories" and "services" (which themselves provide
    common database operations), Advanced Alchemy database configuration objects, and other
    league related services (such as importers and schedulers).

    Attributes:
        service_registry (Registry | None): An `svcs` Registry for managing services.
        loader (DynamicObjectLoader): A DynamicObjectLoader for loading specific objects.
        local_base_dir (Path): The local base directory. Uses `settings.APP_DIR` by default.
        local_root_dir (Path): The local root directory. Uses `settings.APP_ROOT` by default.
        aa_config_dir (Path): The Advanced Alchemy configuration directory.
        get_session (Generator[Session, Any, None]): A generator for a database session.
        get_async_session (AsyncGenerator[AsyncSession, Any]): A generator for an async database session.
        sync_services (list[type[SyncServiceT]]): List of services for sync database operations.
        async_services (list[type[AsyncServiceT]]): List of services for async database operations.

    Example:
        >>> registry = LeagueManager()
        >>> season_service = registry.provide_db_service(SeasonSyncService)
        >>> team_service = registry.provide_db_service(TeamSyncService)
        >>>
        >>> season_service.list()  #  List all seasons
        >>> team_service.count()  #  Count number of teams

    """

    service_registry: Registry | None = field(default=None)

    loader: DynamicObjectLoader = field(default=DynamicObjectLoader())

    # Might make sense to make these private or keep them in post_init
    # Better to control these through the environment variables
    local_app_dir: Path = field(default=settings.user_app.app_dir)
    local_services_dir: Path | None = None
    local_db_config_dir: Path | None = None

    # get_session: Generator[Session, Any, None] = field(default=get_session)
    # get_async_session: AsyncGenerator[AsyncSessionT, Any] = field(default=get_async_session)

    sync_services: list[type[SyncServiceT]] = field(init=False)
    async_services: list[type[AsyncServiceT]] = field(init=False)

    async_config: SQLAlchemySyncConfigT | SQLAlchemyAsyncConfigT = field(default=async_config)
    sync_config: SQLAlchemySyncConfigT | SQLAlchemyAsyncConfigT = field(default=sync_config)

    _SVCS_KEY_REGISTRY: str = field(default="league_manager_registry")
    _SVCS_KEY_CONTAINER: str = field(default="league_manager")

    def __attrs_post_init__(self):
        if not self.service_registry:
            self.service_registry = Registry()

        # Get all services
        _importers = self.loader.get_importer_services(settings.template_loader_dir)
        _schedulers = self.loader.get_schedule_services(settings.schedule_loader_dir)
        self.sync_services = self.loader.get_aa_services()
        self.async_services = self.loader.get_aa_services(is_async=True)

        # Include additional AA services from the local services directory
        if self.local_services_dir and self.local_services_dir is not settings.db_services_dir:
            svc_loader = self.loader.local_app(service_dir=self.local_services_dir)
            self.sync_services += svc_loader.get_aa_services()
            self.async_services += svc_loader.get_aa_services(is_async=True)

        # If running from within host application, migration path is set within project
        # otherwise, it sets the migration environment relative to the user's app.
        if settings.app_name not in str(settings.user_app.app_dir):
            self.async_config.alembic_config.script_location = str(settings.user_app.app_dir / "migrations")
            self.async_config.alembic_config.script_config = str(settings.user_app.app_dir / "alembic.ini")
            self.sync_config.alembic_config.script_location = str(settings.user_app.app_dir / "migrations")
            self.sync_config.alembic_config.script_config = str(settings.user_app.app_dir / "alembic.ini")

        # Register objects
        self.registry.register_value(SQLAlchemyAsyncConfigT, self.async_config)
        self.registry.register_value(SQLAlchemySyncConfigT, self.sync_config)

        for _importer in _importers:
            self.register_importer_service(importer_type=_importer)

        for _scheduler in _schedulers:
            self.register_scheduler_service(scheduler_type=_scheduler)

        for service_type in self.sync_services:
            self.register_db_service(service_type=service_type)

        for service_type in self.async_services:
            self.test_register_async(service_type=service_type)

    @property
    def registry(self) -> Registry:
        return self.service_registry

    def register_db_service(self, service_type: type[SyncServiceT]) -> None:
        """Register a League Manager service based on its type."""

        _config = self.provide_sync_config
        _service = ServiceManagement(service_type=service_type, config=_config)
        self.registry.register_value(service_type, next(_service.get_service))

    def test_register_async(self, service_type: type[AsyncServiceT]) -> None:
        """Test method to register an async League Manager service based on its type."""

        _config = Container(self.registry).get(SQLAlchemyAsyncConfigT)
        provider = service_provider(service_type, config=_config)

        self.registry.register_factory(service_type, provider)

    def register_async_db_service(self, service_type: type[AsyncServiceT]) -> None:
        """Register an async League Manager service based on its type."""
        print(f"Registering async service: {service_type.__name__}")  # Debugging line
        _service = ServiceManagement(service_type=service_type)
        print(f"Service type: {service_type}")
        self.registry.register_value(service_type, next(_service.get_service))

    def register_importer_service(self, importer_type: type[ImporterT]) -> None:
        """Register an importer service based on the type specified."""
        _importer = ImporterManagement(importer_type=importer_type)
        self.registry.register_value(importer_type, _importer.get_importer)

    def register_scheduler_service(self, scheduler_type: type[ScheduleServiceT]) -> None:
        """Register a scheduling service based on its type."""
        _scheduler = SchedulerManagement(scheduler_type=scheduler_type)
        self.registry.register_value(scheduler_type, _scheduler.get_scheduler)

    @property
    def provide_sync_config(self) -> SQLAlchemySyncConfigT:
        return Container(self.registry).get(SQLAlchemySyncConfigT)

    @property
    def provide_async_config(self) -> SQLAlchemyAsyncConfigT:
        return Container(self.registry).get(SQLAlchemyAsyncConfigT)

    @property
    def provide_sync_session(self) -> Session:
        sync_config = self.provide_sync_config
        with sync_config.get_session() as session:
            return session

    def provide_db_service(self, service_type: type[SyncServiceT]) -> type[SyncServiceT]:
        """Provide a League Manager service based on its type."""
        return Container(self.registry).get(service_type)

    def provide_async_db_service(self, service_type: type[AsyncServiceT]) -> type[AsyncServiceT]:
        """Provide an async League Manager service based on its type."""
        return Container(self.registry).aget(service_type)

    def provide_importer_service(self, importer_type: type[ImporterT]) -> ImporterT:
        """Provide an importer service based on the type specified."""
        return Container(self.registry).get(importer_type)

    def provide_scheduler_service(self, scheduler_type: type[ScheduleServiceT]) -> ScheduleServiceT:
        """Provide a scheduling service based on the type specified."""
        return Container(self.registry).get(scheduler_type)
