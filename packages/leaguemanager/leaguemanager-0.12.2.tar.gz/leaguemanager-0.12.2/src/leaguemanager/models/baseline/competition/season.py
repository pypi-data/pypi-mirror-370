from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import CompetitionBase, add_slug_column, mapper, metadata

if TYPE_CHECKING:
    from leaguemanager.models.baseline import TeamMembership

    from .league import League
    from .ruleset import Ruleset


@define(slots=False)
class Season(CompetitionBase):
    """Defines a competition type with a beginning and end, and usually has winner at the end.

    This is usually a child of a League object, with start and end dates. While the League
    is perpetual (recurring), a Season object tend to be finite (i.e., Spring Volleball 2025,
    Winter/Spring '26).

    Attributes:
        id (UUID): Inherited from UUIDAuditBase
        league_id (UUID): ForeignKey to League.
        name (str): Descriptive name. (i.e, Fall Coed Soccer 2025, Summer Little League 2026)
        description (str): Optional description of the season details.
        # competition_type (str): Desginate the type of competition. Inherited from CompetitionBase. (NOT MAPPED)
        active (bool): Defaults to True. Can be used to deactivate this Season.
        projected_start_date (datetime): When the Season is projected to start.
        projected_end_date (datetime): When the Season is project to end.
        actual_start_date (datetime): When the Season actually begins.
        actual_end_date (datetime): When the Season actually ends.
        slug (str): Unique slug for the season, used in URLs and identifiers.
        created_at (datetime): Inherited from UUIDAuditBase
        updated_at (datetime): Inherited from UUIDAuditBase
    """

    league_id: UUID | None = field(default=None)
    name: str | None = field(default=None, validator=validators.max_len(80))
    description: str | None = field(default=None, validator=validators.optional(validators.max_len(120)))
    active: bool = field(default=True)
    projected_start_date: datetime | None = field(
        default=None, converter=lambda d: datetime.fromisoformat(d) if isinstance(d, str) else d
    )
    projected_end_date: datetime | None = field(
        default=None, converter=lambda d: datetime.fromisoformat(d) if isinstance(d, str) else d
    )
    actual_start_date: datetime | None = field(
        default=None, converter=lambda d: datetime.fromisoformat(d) if isinstance(d, str) else d
    )
    actual_end_date: datetime | None = field(
        default=None, converter=lambda d: datetime.fromisoformat(d) if isinstance(d, str) else d
    )
    slug: str | None = field(default=None, validator=validators.optional(validators.max_len(100)))

    # team_memberships: list[TeamMembership] | None = None
    league_name: str | None = None


# SQLAlchemy Imperative Mappings

season = Table(
    "season",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("league_id", SA_UUID, ForeignKey("league.id"), nullable=True),
    Column(
        "name",
        String(80),
        nullable=False,
        unique=True,
    ),
    Column("description", String(120), nullable=True),
    Column("active", Boolean, default=True),
    Column("projected_start_date", DateTime(), nullable=True, default=None),
    Column("projected_end_date", DateTime(), nullable=True, default=None),
    Column("actual_start_date", DateTime(), nullable=True, default=None),
    Column("actual_end_date", DateTime(), nullable=True, default=None),
    # Column("cost", Float, nullable=True, default=None),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)

# Add slug column and constraints
add_slug_column(season)

# ORM Relationships

mapper.map_imperatively(
    Season,
    season,
    properties={
        "site": relationship("Site", back_populates="season"),
        "league": relationship("League", back_populates="seasons"),
        "phases": relationship("Phase", back_populates="season"),
        "fixtures": relationship("Fixture", back_populates="season"),
        "team_memberships": relationship("TeamMembership", back_populates="season"),
        "athlete_stats": relationship("AthleteStats", back_populates="season"),
        "team_stats": relationship("TeamStats", back_populates="season"),
        "ruleset": relationship("Ruleset", back_populates="season", uselist=False, cascade="all, delete-orphan"),
    },
)

Season.league_name = association_proxy("league", "name")
