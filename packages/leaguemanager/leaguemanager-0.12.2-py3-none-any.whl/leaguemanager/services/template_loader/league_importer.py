from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, List, Protocol, runtime_checkable

import pandas as pd
from advanced_alchemy.exceptions import DuplicateKeyError, IntegrityError, InvalidRequestError

# import contextlib
from attrs import define, field, validators
from rich import print
from sqlalchemy.exc import PendingRollbackError

from leaguemanager import models as m
from leaguemanager import services as s
from leaguemanager.lib import get_settings

# TODO: Move the logger object setup to a separate module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from leaguemanager import LeagueManager


__all__ = [
    "ExcelLoader",
    "CSVLoader",
    "JSONLoader",
    "GoogleSheetsLoader",
    "MemoryLoader",
]


@runtime_checkable
class Importer(Protocol):
    """Protocol for importers that can load data into the database."""

    def load(self) -> None:
        """Load data into the database."""

    def validate(self) -> None:
        """Validate the data before loading it into the database."""

    def write_to_db(self) -> None:
        """Write data to the database."""


def convert_str_to_path(value: str | Path) -> Path:
    """Convert a string to a Path object."""
    if isinstance(value, str):
        return Path(value)
    return value


@define
class InputModels:
    """
    A class that enables all importer classes to pre-instantiate models
    as usable attributes based on the user's template data
    """

    org_model: List[m.Organization]
    league_models: List[m.League]
    season_models: List[m.Season]
    team_membership_models: List[m.TeamMembership]
    team_models: List[m.Team]


@define
class ExcelLoader:
    """A class to load data from Excel files into the database."""

    file_path: str | Path | None = field(default=None, converter=convert_str_to_path)
    league_manager_registry: LeagueManager | None = field(default=None)

    def load(self, template_type: str = "tabulated") -> InputModels:
        """Load data from an Excel file into Python."""
        if not template_type == "tabulated":
            raise NotImplementedError

        data = self._transform_tabulated_data
        org_model = [m.Organization(name=data["organization"]["name"])]

        leagues = []
        for league in data["leagues"]:
            leagues.append(m.League(name=league["name"], organization_id=org_model[0].id))

        seasons = []
        for season in data["seasons"]:
            for league in leagues:
                if league.name == season["league"]:
                    seasons.append(m.Season(name=season["name"], league_id=league.id))
                    break

        teams = []
        team_memberships = []
        for team in data["teams"]:
            for season in seasons:
                if season.name == team["season"]:
                    label = f"{team['name']} - {season.name}"
                    team_membership = m.TeamMembership(label=label, season_id=season.id)
                    team_memberships.append(team_membership)
                    teams.append(m.Team(name=team["name"], team_membership_id=team_membership.id))
                    break

        return InputModels(
            org_model=org_model,
            league_models=leagues,
            season_models=seasons,
            team_membership_models=team_memberships,
            team_models=teams,
        )

    def validate(self) -> None:
        """Validate the data before loading it into the database."""
        # Implementation for validating Excel data
        raise NotImplementedError("Excel loading not implemented yet.")

    @property
    def write_to_db(self) -> None:
        """Write data to the database."""
        input_models = self.load(template_type="tabulated")
        input_model_payloads = [
            ("organizations", input_models.org_model, self.org_service),
            ("leagues", input_models.league_models, self.league_service),
            ("seasons", input_models.season_models, self.season_service),
            ("team_memberships", input_models.team_membership_models, self.team_membership_service),
            ("teams", input_models.team_models, self.team_service),
        ]

        for name, model, service in input_model_payloads:
            try:
                service.create_many(model, auto_commit=True)
                logger.info(f"✅ Successfully created {name}!")

            except (DuplicateKeyError, IntegrityError, InvalidRequestError, PendingRollbackError) as e:
                logger.warning(
                    f"⚠️  These {name} already exist or have conflicts | Error details: {e} | Model details:\n"
                )
                print(f"{model}\n")

            except Exception as e:
                logger.error(f"❌ Failed to create {name} | Error details: {e} | Model details:\n")
                print(f"{model}\n")
                raise  # Re-raise to stop processing

    @property
    def registry(self) -> LeagueManager:
        """Get the LeagueManager registry."""
        if self.league_manager_registry is None:
            raise ValueError("LeagueManager registry is not set.")
        return self.league_manager_registry

    @property
    def org_service(self) -> s.OrganizationService:
        """Get the org service with the session already attached"""
        return self.registry.provide_db_service(s.OrganizationService)

    @property
    def league_service(self) -> s.LeagueService:
        """Get the league service with the session already attached"""
        return self.registry.provide_db_service(s.LeagueService)

    @property
    def season_service(self) -> s.SeasonService:
        """Get the season service with the session already attached"""
        return self.registry.provide_db_service(s.SeasonService)

    @property
    def team_service(self) -> s.TeamService:
        """Get the team service with the session already attached"""
        return self.registry.provide_db_service(s.TeamService)

    @property
    def team_membership_service(self) -> s.TeamMembershipService:
        """Get the team membership service with the sessions already attached"""
        return self.registry.provide_db_service(s.TeamMembershipService)

    @property
    def _transform_tabulated_data(self) -> dict:
        """Transform dataframe to hierarchical dictionary structure"""

        try:

            def dataframe_to_dict(df: pd.DataFrame) -> dict:
                organization = {"name": df["Organization"].iloc[0]}
                leagues = [{"name": league} for league in df["League"].unique()]

                seasons = []
                season_league_pairs = df[["Season", "League"]].drop_duplicates()
                for _, row in season_league_pairs.iterrows():
                    seasons.append({"name": row["Season"], "league": row["League"]})

                teams = []
                team_season_pairs = df[["Team", "Season"]].drop_duplicates()
                for _, row in team_season_pairs.iterrows():
                    teams.append({"name": row["Team"], "season": row["Season"]})

                return {"organization": organization, "leagues": leagues, "seasons": seasons, "teams": teams}

            df = pd.read_excel(self.file_path, sheet_name="Schema")
            return dataframe_to_dict(df)

        except FileNotFoundError:
            logger.error(f"Excel file not found: {self.file_path}")
            sys.exit(1)


@define
class CSVLoader:
    """A class to load data from CSV files into the database."""

    file_path: str | Path | None = field(default=None, converter=convert_str_to_path)

    def load(self, data: dict) -> None:
        """Load data from a CSV file into the database."""
        # Implementation for loading data from CSV
        raise NotImplementedError("CSV loading not implemented yet.")

    def validate(self, data: dict) -> None:
        """Validate the data before loading it into the database."""
        # Implementation for validating CSV data
        raise NotImplementedError("CSV loading not implemented yet.")

    def write_to_db(self, data: dict) -> None:
        """Write data to the database."""
        # Implementation for writing data to the database
        raise NotImplementedError("CSV writing to database not implemented yet.")


@define
class JSONLoader:
    """A class to load data from JSON files into the database."""

    file_path: str | Path | None = field(default=None, converter=convert_str_to_path)

    def load(self, data: dict) -> None:
        """Load data from a JSON file into the database."""
        # Implementation for loading data from JSON
        raise NotImplementedError("JSON loading not implemented yet.")

    def validate(self, data: dict) -> None:
        """Validate the data before loading it into the database."""
        # Implementation for validating JSON data
        raise NotImplementedError("JSON loading not implemented yet.")

    def write_to_db(self, data: dict) -> None:
        """Write data to the database."""
        # Implementation for writing data to the database
        raise NotImplementedError("JSON writing to database not implemented yet.")


@define
class GoogleSheetsLoader:
    """A class to load data from Google Sheets into the database."""

    sheet_id: str | None = field(default=None)
    spreadsheet_name: str | None = field(default=None)
    """Name of the Google Sheets spreadsheet to load data from."""

    def load(self, data: dict) -> None:
        """Load data from a Google Sheet into the database."""
        # Implementation for loading data from Google Sheets
        raise NotImplementedError("Google Sheets loading not implemented yet.")

    def validate(self, data: dict) -> None:
        """Validate the data before loading it into the database."""
        # Implementation for validating Google Sheets data
        raise NotImplementedError("Google Sheets loading not implemented yet.")

    def write_to_db(self, data: dict) -> None:
        """Write data to the database."""
        # Implementation for writing data to the database
        raise NotImplementedError("Google Sheets writing to database not implemented yet.")


@define
class MemoryLoader:
    """A class to load data from memory into the database."""

    data: dict | None = field(default=None)

    def load(self, data: dict) -> None:
        """Load data from memory into the database."""
        # Implementation for loading data from memory

        return data

    def validate(self, data: dict) -> None:
        """Validate the data before loading it into the database."""
        # Implementation for validating memory data
        raise NotImplementedError("Memory loading not implemented yet.")

    def write_to_db(self, data: dict) -> None:
        """Write data to the database."""
        # Implementation for writing data to the database
        raise NotImplementedError("Memory writing to database not implemented yet.")
