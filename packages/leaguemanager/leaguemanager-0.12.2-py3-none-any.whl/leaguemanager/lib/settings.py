import binascii
import enum
import json
import os
from functools import lru_cache
from importlib.util import find_spec
from pathlib import Path
from typing import Any

import environ

from leaguemanager.lib.toolbox import module_to_os_path

MODULE_NAME = "leaguemanager"
HOST_APP_DIR = module_to_os_path(MODULE_NAME)


def set_to_cwd_if_none(value: str) -> Path:
    """Set the user app directory."""
    if not value:
        return Path.cwd()
    try:
        return Path(value).resolve()
    except ValueError as e:
        raise ValueError(f"Invalid path for app_dir: {value}") from e


@environ.config
class HostApplication:
    app_name: str = MODULE_NAME
    app_dir: Path = environ.var(default=HOST_APP_DIR)
    root_dir: Path = environ.var(default=HOST_APP_DIR.parent.parent.resolve())
    db_services_dir: Path = environ.var(default=HOST_APP_DIR / "services")
    template_loader_dir: Path = environ.var(default=HOST_APP_DIR / "services" / "template_loader")
    schedule_loader_dir: Path = environ.var(default=HOST_APP_DIR / "services" / "scheduling")
    # db_config_dir: Path = environ.var(default=HOST_APP_DIR / "db" / "config")

    synth_data_dir: Path = environ.var(default=HOST_APP_DIR / "data" / "synthetic_data")

    excel_template_dir: Path = environ.var(default=HOST_APP_DIR / "data" / "importer_templates" / "excel")

    @environ.config(prefix="USER")
    class UserApplication:
        """User application settings."""

        app_name: str = environ.var(default=None)
        app_dir: Path = environ.var(default=None, converter=set_to_cwd_if_none)
        root_dir: Path = environ.var(default=None, converter=set_to_cwd_if_none)
        db_services_dir: Path = environ.var(default=None, converter=set_to_cwd_if_none)
        db_config_dir: Path = environ.var(default=None, converter=set_to_cwd_if_none)

    @environ.config(prefix="ALEMBIC")
    class AlembicConfig:
        """Configuration for Alembic migrations."""

        migration_path: Path = environ.var(default=None)
        migration_config_path: Path = environ.var(default=None)
        template_path: Path = environ.var(default=None)
        sqlite_data_directory: Path = environ.var(default=Path.cwd() / "data_league_db")

    @environ.config(prefix="SEC")
    class SecurityConfig:
        """Security configuration settings."""

        def _str_to_list(value: str | list[str]) -> list[str]:
            if isinstance(value, str):
                return [value]
            return value

        crypt_schemes: str | list[str] = environ.var(default=["argon2"], converter=_str_to_list)

    @environ.config(prefix="ROLE")
    class RoleConfig:
        """Role configuration settings."""

        default_user: str = environ.var(default="user")
        athlete: str = environ.var(default="athlete")
        team_manager: str = environ.var(default="team_manager")
        official: str = environ.var(default="official")
        organization_admin: str = environ.var(default="admin")
        superuser: str = environ.var(default="superuser")

    @environ.config(prefix="EMAIL")
    class EmailConfig:
        """Email configuration settings."""

        enabled: bool = environ.var(default=True)
        smtp_host: str = environ.var(default="localhost")
        smtp_port: int = environ.var(default=587)
        smtp_user: str = environ.var(default=None)
        smtp_password: str = environ.var(default=None)
        from_email: str = environ.var(default="noreply@example.com")
        from_name: str = environ.var(default="League Manager App")
        use_tls: bool = environ.var(default=True)
        use_ssl: bool = environ.var(default=False)
        timeout: int = environ.var(default=10)

    user_app: UserApplication = environ.group(UserApplication)
    alembic: AlembicConfig = environ.group(AlembicConfig)
    security: SecurityConfig = environ.group(SecurityConfig)
    role: RoleConfig = environ.group(RoleConfig)


@lru_cache(maxsize=1)
def get_settings() -> HostApplication:
    """Get the settings for the host application."""
    return environ.to_config(HostApplication)
