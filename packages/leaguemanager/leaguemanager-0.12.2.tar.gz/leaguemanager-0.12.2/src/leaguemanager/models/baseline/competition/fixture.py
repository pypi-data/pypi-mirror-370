from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Column, DateTime, ForeignKey, String, Table
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import EventBase, mapper, metadata


@define(slots=False)
class Fixture(EventBase):
    """Defines a contest/competition which results in statistical results.

    A Fixture represents a specific contest or match between opponents or contestants.
    This object is generally a child of a CompetitionPhase object. For example, during any given
    phase of a competition (such as a Matchday), there can be many Fixtures (i.e., Team A vs Team B).

    Attributes:
        id (UUID): Inherited from UUIDAuditBase
        season_id (UUID): ForeignKey to Season.
        phase_id (UUID): ForeignKey to Phase.
        site_id (UUID): ForeignKey to Site.
        label (str): Description of the fixture (i.e., Team A vs Team B, 8-Team Elimination, etc...).
        site_venue (str): Specifies specific venue for Fixture (i.e., Field A, Court 2, etc...).
        outcome_type (str): Type of outcome (i.e., regular, decision, shootout, forfeit, etc...).
        status (str): Status of fixture (i.e., pre-event, in-progress, post-event).
        created_at (datetime): Inherited from UUIDAuditBase
        updated_at (datetime): Inherited from UUIDAuditBase
    """

    season_id: UUID | None = field(default=None)
    phase_id: UUID | None = field(default=None)
    site_id: UUID | None = field(default=None)
    label: str | None = field(default=None, validator=validators.max_len(40))
    site_venue: str | None = field(default=None, validator=validators.optional(validators.max_len(40)))
    outcome_type: str | None = field(default="regular", validator=validators.max_len(12))
    status: str | None = field(default="pre-event", validator=validators.max_len(12))


# SQLAlchemy Imperative Mappings

fixture = Table(
    "fixture",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("season_id", SA_UUID, ForeignKey("season.id"), nullable=False),
    Column("phase_id", SA_UUID, ForeignKey("phase.id"), nullable=True),
    Column("site_id", SA_UUID, ForeignKey("site.id"), nullable=True),
    Column("label", String(40), nullable=False),
    Column("site_venue", String(40), nullable=True),
    Column("outcome_type", String(12), nullable=True),
    Column("status", String(12), nullable=True),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)


# ORM Relationships

mapper.map_imperatively(
    Fixture,
    fixture,
    properties={
        "season": relationship("Season", back_populates="fixtures"),
        "phase": relationship("Phase", back_populates="fixtures"),
        "team_stats": relationship("TeamStats", back_populates="fixture"),
        "athlete_stats": relationship("AthleteStats", back_populates="fixture"),
        "managing": relationship("Managing", back_populates="fixture"),
        "officiating": relationship("Officiating", back_populates="fixture"),
        "site": relationship("Site", back_populates="fixture", uselist=False),
    },
)
