from __future__ import annotations

import inspect
from logging import Logger
from typing import TYPE_CHECKING

from advanced_alchemy.extensions.litestar.providers import create_service_provider
from attrs import define, field
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override

from leaguemanager.dependency.dependency_registry import LeagueManager
from leaguemanager.services._typing import (
    AsyncServiceT,
    ModelT,
    SQLAlchemyAsyncConfigT,
    SQLAlchemySyncConfigT,
    SyncServiceT,
)
from leaguemanager.services.competition.season import SeasonService
from litestar.di import Provide
from litestar.exceptions import ImproperlyConfiguredException
from litestar.plugins import InitPlugin
from litestar.plugins.sqlalchemy import SQLAlchemyPlugin

from .oauth import AccessTokenState, OAuth2AuthorizeCallback, OAuth2Token

if TYPE_CHECKING:
    from litestar.app import Litestar
    from litestar.config.app import AppConfig
    from litestar.datastructures.state import State


logger = Logger(__name__)


@define
class LMPluginConfig:
    """Configuration for the LeagueManager plugin."""

    league_manager: LeagueManager | None = None
    league_manager_state_key: str = field(default="lm")
    sync_service_provider_key: str = field(default="db_sync_service")
    async_service_provider_key: str = field(default="db_async_service")

    include_auth: bool = field(default=True)

    sqlalchemy_plugin: SQLAlchemyPlugin | None = None

    registry_key: str = field(init=False)
    container_key: str = field(init=False)

    def __attrs_post_init__(self) -> None:
        if self.league_manager is None:
            try:
                from leaguemanager import LeagueManager

                self.league_manager = LeagueManager()
            except ImportError as e:
                raise ImportError("LeagueManager is not installed. Please install it to use the LM Dashboard.") from e
        self.registry_key = self.league_manager._SVCS_KEY_REGISTRY
        self.container_key = self.league_manager._SVCS_KEY_CONTAINER


class LMPlugin(InitPlugin):
    """Plugin to integrate LeagueManager into Litestar applications."""

    _league_manager: LeagueManager

    def __init__(self, config: LMPluginConfig) -> None:
        """Initialize the plugin with the provided configuration."""
        self._config = config

    @property
    def lm_key(self) -> str:
        return self._config.league_manager_state_key

    @property
    def sync_key(self) -> str:
        return self._config.sync_service_provider_key

    @property
    def async_key(self) -> str:
        return self._config.async_service_provider_key

    def setup_sqlalchemy_plugin(self, state: State) -> SQLAlchemyPlugin:
        if self._config.sqlalchemy_plugin is None:
            league_manager = state.get(self.lm_key)

            _async_config = league_manager.provide_async_db_config
            self._config.sqlalchemy_plugin = SQLAlchemyPlugin(_async_config)
        return self._config.sqlalchemy_plugin

    def provide_lm(self, state: State) -> LeagueManager:
        league_manager = state.get(self.lm_key)
        assert league_manager is not None
        return league_manager

    def sync_db_service(self, state: State, key: str = "yes") -> type[SyncServiceT]:
        """Provide the LeagueManager instance from the app state."""
        league_manager: LeagueManager = state.get(self.lm_key)
        if league_manager is None:
            raise ImproperlyConfiguredException("LeagueManager is not available in the app state.")

        return league_manager.provide_db_service

    def async_db_service(self, state: State, key: str = "yes") -> type[AsyncServiceT]:
        """Provide the LeagueManager instance from the app state."""
        league_manager: LeagueManager = state.get(self.lm_key)
        if league_manager is None:
            raise ImproperlyConfiguredException("LeagueManager is not available in the app state.")
        return league_manager.provide_async_db_service

    def add_lm_to_app(self, app: Litestar) -> None:
        """Include LeagueManager in the app state."""
        if self._config.league_manager:
            league_manager = self._config.league_manager
            logger.info("Using provided LeagueManager instance.")
        else:
            msg = "LeagueManager class must be provided."
            raise ImproperlyConfiguredException(
                msg,
            )
        app.state.update({self.lm_key: league_manager})

    @override
    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        if self._config.sqlalchemy_plugin:
            app_config.plugins.append(self._config.sqlalchemy_plugin)
        app_config.dependencies.update(
            {
                self.lm_key: Provide(self.provide_lm, sync_to_thread=False),
                self.sync_key: Provide(self.sync_db_service, sync_to_thread=False),
                self.async_key: Provide(self.async_db_service, sync_to_thread=False),
            }
        )
        app_config.on_startup.insert(0, self.add_lm_to_app)
        app_config.signature_namespace.update(
            {
                "LeagueManager": LeagueManager,
            }
        )
        if self._config.include_auth:
            app_config.signature_namespace.update(
                {
                    "OAuth2AuthorizeCallback": OAuth2AuthorizeCallback,
                    "AccessTokenState": AccessTokenState,
                    "OAuth2Token": OAuth2Token,
                    "SeasonService": SeasonService,
                },
            )
        return app_config
