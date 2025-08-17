import os

from leaguemanager.lib.settings import get_settings

get_settings.cache_clear()
settings = get_settings()

SYNC_DATABASE_URI = os.getenv("SYNC_DATABASE_URI", None)
ASYNC_DATABASE_URI = os.getenv("ASYNC_DATABASE_URI", None)

ECHO: bool = os.getenv("ECHO", False)


def _is_sqlite(uri: str | None) -> bool:
    if uri is None:
        return False
    settings.alembic.sqlite_data_directory.mkdir(parents=True, exist_ok=True)
    return "sqlite" in uri.lower()


def _create_str_uri(is_async: bool = False) -> str:
    uri = SYNC_DATABASE_URI if not is_async else ASYNC_DATABASE_URI
    if not _is_sqlite(uri):
        try:
            settings.alembic.sqlite_data_directory.mkdir(parents=True, exist_ok=True)
            if is_async:
                return "sqlite+aiosqlite:///data_league_db/lmgr_data.db"
            return "sqlite:///data_league_db/lmgr_data.db"
        except ValueError as e:
            raise NotImplementedError(f"Database implementation needed. {e}") from ValueError
    if not uri:
        raise ValueError("DATABASE_URI is not set")
    return uri


def uri(is_async: bool = False) -> str:
    if is_async:
        return _create_str_uri(is_async=True)
    return _create_str_uri()


db_args = {"echo": ECHO, "connect_args": {"check_same_thread": False}}
