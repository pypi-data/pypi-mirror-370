from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, AsyncGenerator, Callable, Generator, Iterator, Optional, Union, cast, overload

from advanced_alchemy.config import SQLAlchemyAsyncConfig, SQLAlchemySyncConfig
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService
from attrs import define, field
from sqlalchemy import select
from sqlalchemy.orm import Session

from leaguemanager.services._typing import AsyncServiceT, ImporterT, ModelT, ScheduleServiceT, SyncServiceT

if TYPE_CHECKING:
    from sqlalchemy import Select
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Session
__all__ = ["ServiceManagement", "ImporterManagement", "SchedulerManagement"]


@define
class ServiceManagement:
    """Manages a SQLAlchemySyncRepositoryService[ModelT] class.

    TODO: Async support

    Given the `service_type` and `db_session`, as well as a db_session, it will hold then provide
    the applicable service (for the corresponding service type.). The `get_service` property will
    return the appropriate service for the given `service_type` and `db_session`.

    Attributes:
        service_type (type[SyncServiceT] | type[AsyncServiceT]): Service type to manage.
        model_type (type[ModelT]): Model type for the given `service_type`.
        db_session (Session | None): Database session to use for the service.

    Example:
      >>> _service = ServiceManagement(
      ...     service_type=SeasonSyncService, model_type=Season, db_session=session
      ... )
      >>> _service.get_service
    """

    service_type: type[SyncServiceT[ModelT] | AsyncServiceT[ModelT]] = field()
    db_session: Session = field(default=None)
    config: type[SQLAlchemySyncConfig | SQLAlchemyAsyncConfig] = field(default=None)
    model_type: type[ModelT] = field(init=False)

    def __attrs_post_init__(self):
        self.model_type = self.service_type.repository_type.model_type

    @property
    def get_service(self) -> Iterator[ServiceManagement.service_type]:  # type: ignore[return]
        with self.service_type.new(
            session=self.db_session, config=self.config, statement=select(self.model_type)
        ) as service:
            yield service

    @asynccontextmanager
    @property
    async def get_async_service(self) -> AsyncGenerator[ServiceManagement.service_type, None]:  # type: ignore[return]
        """Asynchronous version of get_service."""
        async with self.service_type.new(session=self.db_session, statement=select(self.model_type)) as service:
            yield service

    @property
    def test_get_async_service(self) -> Iterator:
        """Test method to get an async service."""
        with self.service_type.new(statement=select(self.model_type)) as service:
            yield service


@overload
def service_provider(
    service_class: type[SyncServiceT[ModelT]],
    /,
    statement: "Optional[Select[tuple[ModelT]]]" = None,
    session: "Optional[Session]" = None,
    config: "Optional[SQLAlchemySyncConfig]" = None,
) -> Callable[..., Generator[SyncServiceT[ModelT], None, None]]: ...


@overload
def service_provider(
    service_class: type[AsyncServiceT[ModelT]],
    /,
    statement: "Optional[Select[tuple[ModelT]]]" = None,
    session: "Optional[AsyncSession]" = None,
    config: "Optional[SQLAlchemyAsyncConfig]" = None,
) -> Callable[..., AsyncGenerator[AsyncServiceT[ModelT], None]]: ...


def service_provider(
    service_class: type[Union[SyncServiceT[ModelT], AsyncServiceT[ModelT]]],
    /,
    statement: "Optional[Select[tuple[ModelT]]]" = None,
    session: "Optional[Union[Session, AsyncSession]]" = None,
    config: "Optional[Union[SQLAlchemySyncConfig, SQLAlchemyAsyncConfig]]" = None,
) -> Callable[..., Union["AsyncGenerator[AsyncServiceT[ModelT], None]", "Generator[SyncServiceT[ModelT], None, None]"]]:
    model = service_class.repository_type.model_type
    if not statement:
        statement = select(model)

    return_type = AsyncGenerator[service_class, None]
    if issubclass(service_class, SQLAlchemyAsyncRepositoryService) or service_class is SQLAlchemyAsyncRepositoryService:

        async def provide_service_async(*args: Any, **kwargs: Any) -> AsyncGenerator[AsyncServiceT[ModelT], None]:
            async with service_class.new(
                session=session, statement=statement, config=cast("Optional[SQLAlchemyAsyncConfig]", config)
            ) as service:
                print(service)
                yield service

        return provide_service_async

    return_type = Generator[service_class, None, None]

    def provide_service_sync(*args: Any, **kwargs: Any) -> Generator[SyncServiceT[ModelT], None, None]:
        with service_class.new(
            session=session, statement=statement, config=cast("Optional[SQLAlchemySyncConfig]", config)
        ) as service:
            yield service

    provide_service_sync.__annotations__ = {"return": return_type}
    return provide_service_sync


@define
class ImporterManagement:
    """Manages Importer services.

    Provides a basic utility to manage importers for league data. It takes an `importer_type` and provides
    an instance of that importer type through the `get_importer` property. It can be used to register
    a specific importer type for league data management.

    Attributes:
        importer_type (type[ImporterT]): Importer type to manage.

    Example:
      >>> _importer = ImporterManagement(importer_type=LeagueImporter)
      >>> _importer.get_importer
    """

    importer_type: type[ImporterT] = field()

    @property
    def get_importer(self) -> ImporterT:
        return self.importer_type()


@define
class SchedulerManagement:
    """Manages scheduling services.

    Provides a basic utility to manage scheduling services for league data. It takes a `scheduler_type` and provides
    an instance of that scheduler type through the `get_scheduler` property. It can be used to register
    a specific scheduler type for league scheduling management.

    Attributes:
        service_type (type[SyncServiceT]): Service type to manage.

    Example:
      >>> _scheduler = SchedulerManagement(service_type=BracketSchedule)
      >>> _scheduler.get_service
    """

    scheduler_type: type[ScheduleServiceT] = field()

    @property
    def get_scheduler(self) -> ScheduleServiceT:
        return self.scheduler_type()
