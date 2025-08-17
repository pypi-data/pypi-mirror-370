"""CLI for League Manager tool."""

import json
from typing import Annotated, Optional

import typer
from advanced_alchemy.exceptions import DuplicateKeyError
from rich import print
from rich.prompt import Prompt
from sqlalchemy import delete
from sqlalchemy.orm import Session

from leaguemanager import LeagueManager, models
from leaguemanager.db import register_sqlite
from leaguemanager.db.cli.alembic_cli import db_app
from leaguemanager.dependency.cli_callbacks import (
    provide_importer_service,
    provide_manager_service,
    provide_scheduler_service,
    provide_sync_db_session,
    registry,
)
from leaguemanager.lib import get_settings
from leaguemanager.services import (
    LeagueService,
    OrganizationService,
    RoundRobinSchedule,
    SeasonService,
    TeamMembershipService,
    TeamService,
)
from leaguemanager.services.template_loader.league_importer import (
    CSVLoader,
    ExcelLoader,
    GoogleSheetsLoader,
    JSONLoader,
    MemoryLoader,
)

from . import __app_name__, __version__

settings = get_settings()
register_sqlite()

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        print(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.command(help="Populate the database with synthetic data.")
def populate(
    season_service: Annotated[
        Optional[SeasonService], typer.Argument(callback=provide_manager_service, parser=SeasonService)
    ] = None,
    league_service: Annotated[
        Optional[LeagueService], typer.Argument(callback=provide_manager_service, parser=LeagueService)
    ] = None,
    team_service: Annotated[
        Optional[TeamService], typer.Argument(callback=provide_manager_service, parser=TeamService)
    ] = None,
    team_membership_service: Annotated[
        Optional[TeamMembershipService],
        typer.Argument(callback=provide_manager_service, parser=TeamMembershipService),
    ] = None,
    organization_service: Annotated[
        Optional[OrganizationService],
        typer.Argument(callback=provide_manager_service, parser=OrganizationService),
    ] = None,
) -> None:
    if (settings.app_dir / "example_data.json").exists():
        with open(settings.app_dir / "example_data.json") as _data:
            data = json.load(_data)
    elif not (settings.synth_data_dir / "example_data.json").exists():
        data_file = Prompt.ask("Please provide the path to the data directory: ")
        try:
            with open(data_file) as _data:
                data = json.load(_data)
        except FileNotFoundError:
            print(f"File {data_file} does not exist.")
            return
    else:
        with open(settings.synth_data_dir / "example_data.json") as _data:
            data = json.load(_data)
    try:
        org = organization_service.create(data["organization"], auto_commit=True)
        for league in data["leagues"]:
            league["organization_id"] = org.id
            league_service.create(league, auto_commit=True)
        for season in data["seasons"]:
            _league = league_service.get_one(name=season["league"])
            season["league_id"] = _league.id
            season_service.create(
                season,
                auto_commit=True,
            )
        for team in data["teams"]:
            _team_membership = team_membership_service.create(
                {"label": f"{team['name']} - {team['season']}"},
                auto_commit=True,
            )
            team["team_membership_id"] = _team_membership.id
            team.pop("season", None)  # Remove season key if it exists

        for team in data["teams"]:
            team_service.create(
                team,
                auto_commit=True,
            )
    except DuplicateKeyError:
        print("[red]Data already exists in the database. Will not create any data...[/red]")
        return

    print(
        "✨ [green]Successfully created data![/green] ✨",
        f"\nCreated {season_service.count()} Seasons",
        f"\nCreated {league_service.count()} Leagues",
        f"\nCreated {team_service.count()} Teams",
        f"\nCreated {organization_service.count()} Organization",
    )
    return


@app.command(help="Run a scheduler.")
def schedule(
    session: Annotated[Optional[Session], typer.Argument(callback=provide_sync_db_session, parser=Session)] = None,
    season_service: Annotated[
        Optional[SeasonService], typer.Argument(callback=provide_manager_service, parser=SeasonService)
    ] = None,
    scheduler: Annotated[
        Optional[RoundRobinSchedule],
        typer.Argument(callback=provide_scheduler_service, parser=RoundRobinSchedule),
    ] = None,
    season_name: Annotated[Optional[str], typer.Argument(help="Name of the season to schedule.")] = None,
) -> None:
    """Run a scheduler for the given season."""
    if not season_name:
        season_name = Prompt.ask("Please provide the Season name to schedule: ")
    try:
        _season = season_service.get_one(name=season_name)
    except ValueError:
        print(f"Season [green]{season_name}[/green] does not exist.")
        return

    try:
        schedule = RoundRobinSchedule(registry, _season).generate_schedule()
        if not schedule:
            print(f"No schedule generated for season: {season_name}.")
            return
        print(f"✨ [green]Successfully generated schedule for season: {schedule.name}[/green] ✨")
        return
    except Exception as e:
        print(f"An error occurred while generating the schedule: {e}")


@app.command(help="Check the counts of data in each table.")
def check(
    session: Annotated[Optional[Session], typer.Argument(callback=provide_sync_db_session, parser=Session)] = None,
    season_service: Annotated[
        Optional[SeasonService], typer.Argument(callback=provide_manager_service, parser=SeasonService)
    ] = None,
    league_service: Annotated[
        Optional[LeagueService], typer.Argument(callback=provide_manager_service, parser=LeagueService)
    ] = None,
    team_service: Annotated[
        Optional[TeamService], typer.Argument(callback=provide_manager_service, parser=TeamService)
    ] = None,
    organization_service: Annotated[
        Optional[OrganizationService],
        typer.Argument(callback=provide_manager_service, parser=OrganizationService),
    ] = None,
    all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Check all seasons, leagues, and teams.",
    ),
) -> None:
    if all:
        print(
            "✨ [green]These are the counts of data in each table[/green] ✨",
            f"\n{season_service.count()} Seasons",
            f"\n{league_service.count()} Leagues",
            f"\n{team_service.count()} Teams",
            f"\n{organization_service.count()} Organization",
        )
    else:
        model = Prompt.ask("Please provide the model name to check (i.e. Season): ")
        try:
            _models = session.query(getattr(models, model)).all()
            print(f"Found {session.query(getattr(models, model)).count()} {model}s.")
            for m in _models:
                if m.name:
                    print(f">> {m.name}")
        except AttributeError:
            print(f"Model [green]{model}[/green] does not exist.")
    return


@app.command(name="loader", help="Load data from a file into the database.")
def _loader(
    session: Annotated[Optional[Session], typer.Argument(callback=provide_sync_db_session, parser=Session)] = None,
    csv_loader: Annotated[
        Optional[CSVLoader], typer.Argument(callback=provide_importer_service, parser=CSVLoader)
    ] = None,
    excel_loader: Annotated[
        Optional[ExcelLoader], typer.Argument(callback=provide_importer_service, parser=ExcelLoader)
    ] = None,
    google_sheets_loader: Annotated[
        Optional[GoogleSheetsLoader], typer.Argument(callback=provide_importer_service, parser=GoogleSheetsLoader)
    ] = None,
    json_loader: Annotated[
        Optional[JSONLoader], typer.Argument(callback=provide_importer_service, parser=JSONLoader)
    ] = None,
    memory_loader: Annotated[
        Optional[MemoryLoader], typer.Argument(callback=provide_importer_service, parser=MemoryLoader)
    ] = None,
    file_path: Annotated[Optional[str], typer.Argument(help="Path to the file to load data from.")] = None,
    sheet_id: Annotated[Optional[str], typer.Argument(help="Google Sheets ID to load data from.")] = None,
    spreadsheet_name: Annotated[
        Optional[str], typer.Argument(help="Name of the Google Sheets spreadsheet to load data from.")
    ] = None,
    source: str = typer.Option(default=..., help="Source of the data (excel, csv, google-sheet, json, memory)."),
    validate: bool = typer.Option(
        False,
        "--validate",
        "-v",
        help="Validate the data before loading it into the database.",
    ),
) -> None:
    """Load data from a file into the database."""
    # This function is a placeholder for loading data from various file formats.
    # You can implement the logic to load data from CSV, Excel, Google Sheets, JSON, or memory here.
    # For example, you can use the provided loaders to read data from the specified file formats
    # and then insert that data into the database using the provided session.
    # Example usage:
    if source not in ["csv", "excel", "google-sheet", "json", "memory"]:
        print(f"Invalid source: {source}. Please choose from 'csv', 'excel', 'google-sheet', 'json', or 'memory'.")
        return

    if source == "memory":
        # Example of passing a dictionary from memory to the memory loader
        org = Prompt.ask("Please provide the Organization name: ")
        league = Prompt.ask("Please provide the League name: ")
        season = Prompt.ask("Please provide the Season name: ")
        data = {"organization": org, "league": league, "season": season}

        try:
            result = memory_loader.load(data=data)
        except Exception as e:
            print(f"Invalid dict data provided: {e}")
            return

        print(f"Data loaded from memory: {result}")  # This will print the data loaded from memory
        return

    elif source == "excel":
        filename = Prompt.ask("Enter the name of your Excel (.xlsx) file (e.g., Excel Template - Random User)")
        file_path = get_settings().EXCEL_TEMPLATE_DIR / f"{filename}.xlsx"

        excel_loader = ExcelLoader(file_path=file_path, league_manager_registry=LeagueManager())
        excel_loader.write_to_db  # noqa: B018

        print("✅ [green]Excel data loading completed![/green]")
        return

    elif source == "csv":
        raise NotImplementedError("CSV loading is not implemented yet.")

    elif source == "json":
        raise NotImplementedError("JSON loading is not implemented yet.")

    elif source == "google-sheet":
        raise NotImplementedError("Google Sheets loading is not implemented yet.")

    else:
        print("Couldn't understand input.")
        return


@app.command(name="delete", help="Delete data from the database.")
def _delete(
    session: Annotated[Optional[Session], typer.Argument(callback=provide_sync_db_session, parser=Session)] = None,
    all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Delete all seasons, leagues, teams, and organization.",
    ),
) -> None:
    if all:
        session.execute(delete(models.Season))
        session.execute(delete(models.League))
        session.execute(delete(models.Team))
        session.execute(delete(models.Organization))
        session.execute(delete(models.TeamMembership))
        session.commit()
        print("⛔ [yellow]Removed all Seasons, Leagues, Teams, and Organizations.[/yellow]⛔")
    else:
        model = Prompt.ask("Please provide the model name to delete (i.e. Season): ")
        try:
            session.execute(delete(getattr(models, model.title())))
            session.commit()
        except AttributeError:
            print(f"Model [green]{model.title()}[/green] does not exist.")
        print(f"⛔ [yellow]Removed all data in the {model.title()} table.[/yellow]⛔")
    return


@app.callback(no_args_is_help=True, help="League Manager CLI.")
def main(
    ctx: typer.Context,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-V",
            callback=_version_callback,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = None,
):
    """League Manager CLI."""
    return


# This creates an app for Typer, adding the above commands.
# This enables us to add the `db_app`, which is a Click group from Advanced Alchemy.
app = typer.main.get_command(app)
app.add_command(db_app)
