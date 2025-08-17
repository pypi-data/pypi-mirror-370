import typer
from advanced_alchemy.cli import add_migration_commands

from leaguemanager.dependency.cli_callbacks import provide_async_db_config, provide_sync_db_config

app = typer.Typer(name="db", help="Database commands.", no_args_is_help=True)

_configs = []


if async_db_config := provide_async_db_config():
    _configs.append(async_db_config)
else:
    raise ValueError("Async database configuration is not provided.")


@app.callback(context_settings={"obj": {"configs": _configs}})
def _app(ctx: typer.Context):
    """Passes SQLAlchemy configuration to the Click database group within Advanced Alchemy.

    The SQLAlchemySyncConfig and SQLAlchemyAsyncConfig classes that are defined elsewhere are
    imported here and passed through the Click context. The configuration is accessed by the
    Advanced Alchemy migration commands.

    Args:
        ctx (typer.Context): The Click context.
    """
    pass


# Generate a Click group from Typer "db" app and add Advanced Alchemy migration commands.
click_group = typer.main.get_command(app)

# Add the db_app to the main Typer app to access the db commands.
db_app = add_migration_commands(click_group)
