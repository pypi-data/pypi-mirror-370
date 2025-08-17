from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import ParticipationBase, mapper, metadata

if TYPE_CHECKING:
    from leaguemanager.models.baseline import Athlete


@define(slots=False)
class AthleteStats(ParticipationBase):
    """The participation of an individual or team that can win or lose an Fixture.

    Each individual that is participating in an Fixture has a AthleteStats that represents
    an athlete's performance in that given Fixture. This class is very basic/generic as it
    is used to represent a broad set of competitions. (Premium class can provide more sport
    specific stats.)

    Attributes:
        id (UUID): Inherited from UUIDAuditBase
        season_id (UUID): ForeignKey to Season.
        phase_id (UUID): ForeignKey to Phase.
        fixture_id (UUID): ForeignKey to Fixture.
        label (str): Description of AthleteStats (i.e., "Mark Smith, Week 4, Explosive FC", etc...)
        points_scored (int): Points scored by the Athlete.
        saves (int): Any "saves" made by a player.
        cautions (str): Any cautions received by player.
        note (str): Miscellaneous info concerning player with this fixture.
        expelled (bool): If player was expelled from the fixture.
        disqualified (bool): If player was disqualified from competing in fixture.
        created_at (datetime): Inherited from UUIDAuditBase
        updated_at (datetime): Inherited from UUIDAuditBase
    """

    season_id: UUID | None = field(default=None)
    phase_id: UUID | None = field(default=None)
    fixture_id: UUID | None = field(default=None)
    label: str | None = field(default=None, validator=validators.max_len(90))
    outcome: str | None = field(
        default=None, validator=validators.optional(validators.in_(("win", "loss", "tie", "undecided")))
    )
    score_for: int | None = field(default=0)
    score_against: int | None = field(default=0)
    alignment: str | None = field(default=None, validator=validators.optional(validators.in_(("home", "away"))))
    standing_points: int | None = field(default=None)


# SQLAlchemy Imperative Mappings

athlete_stats = Table(
    "athlete_stats",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("season_id", SA_UUID, ForeignKey("season.id"), nullable=False),
    Column("phase_id", SA_UUID, ForeignKey("phase.id"), nullable=True),
    Column("fixture_id", SA_UUID, ForeignKey("fixture.id"), nullable=True),
    Column("label", String(90), nullable=False),
    Column("outcome", String(12), nullable=True),
    Column("score_for", Integer, nullable=True),
    Column("score_against", Integer, nullable=True),
    Column("alignment", String(6), nullable=True),
    Column("fixture_standing_points", Integer, nullable=True),
    Column("standing_points", Integer, nullable=True),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)


# ORM Relationships

mapper.map_imperatively(
    AthleteStats,
    athlete_stats,
    properties={
        "season": relationship("Season", back_populates="athlete_stats"),
        "fixture": relationship("Fixture", back_populates="athlete_stats"),
        "athlete": relationship("Athlete", back_populates="athlete_stats", uselist=False),
    },
)
