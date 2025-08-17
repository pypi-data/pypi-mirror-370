from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Column, DateTime, ForeignKey, String, Table
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import CompetitionPhaseBase, mapper, metadata

if TYPE_CHECKING:
    from .league import League


@define(slots=False)
class Phase(CompetitionPhaseBase):
    """Defines a 'phase' of a competition.

    A phase represents a distinct phase within a Season. For example, while a given
    Competition could be completed in one or several Fixtures, a Phase corresponds to
    a series of Fixtures, such as a 'Matchday' or 'Match Week'. Alternatively, a
    Phase could correspond to a phase within a competition, such as quarterfinals,
    semifinals, or final match.

    Attributes:
        id (UUID): Inherited from UUIDAuditBase
        season_id (UUID): ForeignKey to Season.
        label (str): Unique label describing the Phase (i.e., Matchday 3, Gameweek 12, Semi-Final 2)
        competition_type (str): Inherited from CompetitionBase.
        phase_type (str): Designation of the competition phase. Inherited from CompetitionPhaseBase.
        created_at (datetime): Inherited from UUIDAuditBase
        updated_at (datetime): Inherited from UUIDAuditBase
    """

    season_id: UUID | None = field(default=None)
    label: str | None = field(default=None, validator=validators.max_len(20))
    competition_type: str | None = field(default="competition", validator=validators.max_len(30))


# SQLAlchemy Imperative Mappings

phase = Table(
    "phase",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("season_id", SA_UUID, ForeignKey("season.id"), nullable=True),
    Column(
        "label",
        String(20),
        nullable=False,
        unique=True,
    ),
    Column("competition_type", String(30), nullable=True),
    Column("phase_type", String(30), nullable=True),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)


# ORM Relationships

mapper.map_imperatively(
    Phase,
    phase,
    properties={
        "season": relationship("Season", back_populates="phases"),
        "fixtures": relationship("Fixture", back_populates="phase"),
    },
)
