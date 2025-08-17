from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import MembershipBase, mapper, metadata


@define(slots=False)
class TeamMembership(MembershipBase):
    """A teams membership in a given Competition (i.e., League, Season).

    Instead of linking a Team object directly to a Competition, the Team is linked
    to a TeamMembership object, which defines their specific affiliation to a
    given competition. That way, a Team can be linked to different TeamMembership
    objects, each connected to different Competitions (in the event that an Team belongs
    to differet Seasons/Leagues). The TeamMembership object can define properties specific
    to a Team, such as uniform color, start and end dates, etc...

    Attributes:
        id (UUID): Inherited from UUIDAuditBase
        season_id (UUID): ForeignKey to Season.
        label (str): Label describing the Team association (i.e., Cylon FC--Fall 2024, etc...)
        home_color (str): Primary color of home uniform.
        away_color (str): Primary color of away uniform.
        start_date (datetime): Date that individual joined Team.
        end_date (datetime): Date that individual left Team.
        created_at (datetime): Inherited from UUIDAuditBase
        updated_at (datetime): Inherited from UUIDAuditBase
    """

    season_id: UUID | None = field(default=None)
    label: str | None = field(default=None, validator=validators.optional(validators.max_len(80)))
    home_color: str | None = field(default="", validator=validators.max_len(12))
    away_color: str | None = field(default="", validator=validators.max_len(12))
    start_date: datetime | None = field(default=None)
    end_date: datetime | None = field(default=None)


# SQLAlchemy Imperative Mappings

team_membership = Table(
    "team_membership",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("season_id", SA_UUID, ForeignKey("season.id"), nullable=True),
    Column("label", String(80), nullable=False),
    Column("home_color", String(12), nullable=True),
    Column("away_color", String(12), nullable=True),
    Column("start_date", DateTime(), nullable=True, default=None),
    Column("end_date", DateTime(), nullable=True, default=None),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
    UniqueConstraint("label", name="uq_team_membership_label"),
)


# ORM Relationships

mapper.map_imperatively(
    TeamMembership,
    team_membership,
    properties={
        "team": relationship("Team", back_populates="team_membership", uselist=False),
        "season": relationship("Season", back_populates="team_memberships"),
    },
)
