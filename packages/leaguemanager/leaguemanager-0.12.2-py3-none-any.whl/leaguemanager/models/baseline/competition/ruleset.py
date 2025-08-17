from __future__ import annotations

from datetime import UTC, datetime

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy import Enum as SA_Enum
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import PropertiesBase, mapper, metadata
from leaguemanager.models.enums import ScheduleType

if TYPE_CHECKING:
    from uuid import UUID

    from .organization import Organization


def sched_type_converter(value):
    if isinstance(value, ScheduleType):
        return value.name
    return value


@define(slots=False)
class Ruleset(PropertiesBase):
    """Defines the ruleset specific to a Competition, such as a Season.

    As opposed to a competition's Properties, the Ruleset provides the specifics and format
    of each Event/Fixture. It defines the parameters of a specific Season that is useful
    for generating a schedule (i.e., start date, number of games per season, length of games).

    Note: Only "round robin" schedule_type is implemented so far.

    TODO: Implement "bracket" and "tournament" schedule_type schedulers

    Attributes:
        id (UUID): Inherited from UUIDAuditBase
        season_id (UUID): ForeignKey to League.
        site_id (UUID): ForeignKey to Site.
        schedule_type (str): Affects how games are scheduled and standings displayed (i.e, "round robin", "tournament")
        start_date (datetime): The date (and time) of first game.
        game_length (int): Total time of a Fixture (in minutes, including breaks).
        time_between (int): Time between end of last Fixture and start of next.
        number_of_teams (int): Active teams this Season.
        number_of_phases (int): Number of total phases per team (one game per team per phase).
        tiebreaker (str): Tie breaker rules.
        venue_count (int): In the case of multiple venues/play locations (i.e., Field 4, Court B, etc..)
        mon_fixtures (bool): Whether Fixtures can be scheduled on Monday.
        tue_fixtures (bool): Whether Fixtures can be scheduled on Tuesday.
        wed_fixtures (bool): Whether Fixtures can be scheduled on Wednesday.
        thu_fixtures (bool): Whether Fixtures can be scheduled on Thursday.
        fri_fixtures (bool): Whether Fixtures can be scheduled on Friday.
        sat_fixtures (bool): Whether Fixtures can be scheduled on Saturday.
        sun_fixtures (bool): Whether Fixtures can be scheduled on Sunday.
        created_at (datetime): Inherited from UUIDAuditBase
        updated_at (datetime): Inherited from UUIDAuditBase
    """

    season_id: UUID | None = field(default=None)
    site_id: UUID | None = field(default=None)
    schedule_type: str | None = field(
        default=None,
        converter=sched_type_converter,
        validator=validators.optional(validators.in_({e.name for e in ScheduleType})),
    )
    start_date: datetime | None = field(
        default=None, converter=lambda d: datetime.fromisoformat(d) if isinstance(d, str) else d
    )
    game_length: int | None = field(default=None, validator=validators.optional(validators.ge(0)))
    time_between: int | None = field(default=0, validator=validators.ge(0))
    number_of_teams: int | None = field(default=None)
    number_of_phases: int | None = field(default=None)
    tiebreaker: str | None = field(default=None, validator=validators.optional(validators.max_len(12)))
    venue_count: int | None = field(default=1)
    mon_fixtures: bool = field(default=False)
    tue_fixtures: bool = field(default=False)
    wed_fixtures: bool = field(default=False)
    thu_fixtures: bool = field(default=False)
    fri_fixtures: bool = field(default=False)
    sat_fixtures: bool = field(default=False)
    sun_fixtures: bool = field(default=False)


ruleset = Table(
    "ruleset",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("season_id", SA_UUID, ForeignKey("season.id"), nullable=True),
    Column("site_id", SA_UUID, ForeignKey("site.id"), nullable=True),
    Column("schedule_type", SA_Enum(ScheduleType), nullable=True),
    Column("start_date", DateTime, default=None, nullable=True),
    Column("game_length", Integer, nullable=True),
    Column("time_between", Integer, nullable=True),
    Column("number_of_teams", Integer, nullable=True),
    Column("number_of_phases", Integer, nullable=True),
    Column("tiebreaker", String(12), nullable=True),
    Column("venue_count", Integer, nullable=False),
    Column("mon_fixtures", Boolean, default=False),
    Column("tue_fixtures", Boolean, default=False),
    Column("wed_fixtures", Boolean, default=False),
    Column("thu_fixtures", Boolean, default=False),
    Column("fri_fixtures", Boolean, default=False),
    Column("sat_fixtures", Boolean, default=False),
    Column("sun_fixtures", Boolean, default=False),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)

# ORM Relationships

mapper.map_imperatively(
    Ruleset,
    ruleset,
    properties={
        "season": relationship("Season", back_populates="ruleset", uselist=False),
        "site": relationship("Site", back_populates="ruleset"),
    },
)
