from __future__ import annotations

from typing import Any
from uuid import UUID

import attrs
from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.repository import SQLAlchemyAsyncSlugRepository, SQLAlchemySyncSlugRepository
from sqlalchemy import select

from leaguemanager import models as m
from leaguemanager.services._typing import ModelT
from leaguemanager.services.base import (
    SQLAlchemyAsyncRepositoryService,
    SQLAlchemySyncRepositoryService,
    is_dict_with_field,
    is_dict_without_field,
)

__all__ = ["SeasonService", "SeasonAsyncService"]


class SeasonService(SQLAlchemySyncRepositoryService):
    """Handles database operations for season data."""

    class SlugRepo(SQLAlchemySyncSlugRepository[m.Season]):
        """Season repository."""

        model_type = m.Season

    repository_type = SlugRepo

    def all_teams(self, season_id: UUID, active: bool = True) -> list[m.Team]:
        """Get all active teams for a given season.

        Selects all teams based off their associaton to a TeamMembership object, which
        in turn is associated with a Season object. The Team must be active."""

        season = self.get(season_id)
        memberships = season.team_memberships
        teams = []
        if not memberships:
            return []
        for _memb in memberships:
            if active:
                if not _memb.team.active:
                    continue
            teams.append(_memb.team)
        return teams

    def all_athletes(self, season_id: UUID, incl_inactive_team: bool = False) -> list[m.Athlete]:
        """Get all players for a given season.

        Selects all players based off their associaton to a IndividualMembership object.
        """

        season = self.get(season_id)
        team_memberships = season.team_memberships
        athletes = []
        for _member in team_memberships:
            team = _member.team
            if team is None:
                continue
            if not incl_inactive_team and not team.active:
                continue
            individual_members = team.individual_memberships
            if individual_members is None:
                continue
            for _indiv in individual_members:
                athletes.append(_indiv.athlete)
        return athletes

    def to_model_on_create(
        self,
        data: ModelT | dict[str, Any],
    ) -> ModelT:
        if attrs.has(data):
            data = attrs.asdict(data)
        if is_dict_without_field(data, "slug"):
            data["slug"] = self.repository.get_available_slug(data["name"])
        return data

    def to_model_on_update(self, data):
        if attrs.has(data):
            data = attrs.asdict(data)
        if is_dict_without_field(data, "slug") and is_dict_with_field(data, "name"):
            data["slug"] = self.repository.get_available_slug(data["name"])
        return data


class SeasonAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for season data."""

    class SlugRepo(SQLAlchemyAsyncSlugRepository[m.Season]):
        """Season repository."""

        model_type = m.Season

    repository_type = SlugRepo

    async def all_teams(self, season_id: UUID, active: bool = True) -> list[m.Team]:
        """Get all active teams for a given season.

        Selects all teams based off their associaton to a TeamMembership object, which
        in turn is associated with a Season object. The Team must be active."""

        season = await self.get(season_id)
        memberships = season.team_memberships
        teams = []
        if not memberships:
            return []
        for _memb in memberships:
            if active:
                if not _memb.team.active:
                    continue
            teams.append(_memb.team)
        return teams

    async def all_athletes(self, season_id: UUID, incl_inactive_team: bool = False) -> list[m.Athlete]:
        """Get all players for a given season.

        Selects all players based off their associaton to a IndividualMembership object.
        """

        season = await self.get(season_id)
        team_memberships = season.team_memberships
        athletes = []
        for _member in team_memberships:
            team = _member.team
            if team is None:
                continue
            if not incl_inactive_team and not team.active:
                continue
            individual_members = team.individual_memberships
            if individual_members is None:
                continue
            for _indiv in individual_members:
                athletes.append(_indiv.athlete)
        return athletes

    async def to_model_on_create(
        self,
        data: ModelT | dict[str, Any],
    ) -> ModelT:
        if attrs.has(data):
            data = attrs.asdict(data)
        if is_dict_without_field(data, "slug"):
            data["slug"] = await self.repository.get_available_slug(data["name"])
        return data

    async def to_model_on_update(self, data):
        if attrs.has(data):
            data = attrs.asdict(data)
        if is_dict_without_field(data, "slug") and is_dict_with_field(data, "name"):
            data["slug"] = await self.repository.get_available_slug(data["name"])
        return data
