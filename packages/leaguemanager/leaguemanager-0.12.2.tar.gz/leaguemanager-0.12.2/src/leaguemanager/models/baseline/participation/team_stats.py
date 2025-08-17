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
    from leaguemanager.models.baseline import Team


@define(slots=False)
class TeamStats(ParticipationBase):
    """The participation of an individual or team that can win or lose an Fixture.

    Each team entity that is participating in an Fixture has a TeamStats that represents
    where scores and stats are expressed about the team's performance in that
    given Fixture.

    Attributes:
        id (UUID): Inherited from UUIDAuditBase
        season_id (UUID): ForeignKey to Season.
        fixture_id (UUID): ForeignKey to Fixture.
        label (str): Description of TeamStats (i.e., "Team A, Week 2, Sunday Softball Div 2", etc...)
        outcome (str): Whether result of Team was a "win", "loss", "tie", or "undecided".
        score_for (int): The total points scored by the Team.
        score_against (int): The total poinst scored against the Team.
        alignment (str): Whether the Team is "home" or "away" (one of those values).
        fixture_standing_points (int): The number of points from the results of this fixture.
        standing_points (int): The number of total points during the competition.
        created_at (datetime): Inherited from UUIDAuditBase
        updated_at (datetime): Inherited from UUIDAuditBase
    """

    season_id: UUID | None = field(default=None)
    fixture_id: UUID | None = field(default=None)
    label: str | None = field(default=None, validator=validators.max_len(90))
    outcome: str | None = field(
        default=None, validator=validators.optional(validators.in_(("win", "loss", "tie", "undecided")))
    )
    score_for: int | None = field(default=0)
    score_against: int | None = field(default=0)
    alignment: str | None = field(default=None, validator=validators.optional(validators.in_(("home", "away"))))
    fixture_standing_points: int | None = field(default=None)
    standing_points: int | None = field(default=None)


# SQLAlchemy Imperative Mappings

team_stats = Table(
    "team_stats",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("season_id", SA_UUID, ForeignKey("season.id"), nullable=False),
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
    TeamStats,
    team_stats,
    properties={
        "season": relationship("Season", back_populates="team_stats"),
        "fixture": relationship("Fixture", back_populates="team_stats"),
        "team": relationship("Team", back_populates="team_stats", uselist=False),
    },
)
