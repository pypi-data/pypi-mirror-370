from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import MembershipBase, mapper, metadata


@define(slots=False)
class IndividualMembership(MembershipBase):
    """An individual's membership in a Team.

    Instead of linking an Athlete object directly to a team, the Athlete is linked
    to an IndividualMembership object, which defines their specific affiliation to a
    given team. That way, an Athlete can be linked to different IndividualMembership
    objects, each connected to different Teams (in the event that an Athlete has multiple
    team affiliations). The IndividualMembership object can define properties specific
    to a Team, such as uniform number, start and end dates, etc...

    Attributes:
        id (UUID): Inherited from UUIDAuditBase
        team_id (UUID): ForeignKey to Team.
        athlete_id (UUID): ForeignKey to Athlete.
        label (str): Label describing the Athlete association (i.e., Henry Cooper, Team A, etc...)
        uniform_number (int): Number used for uniform.
        start_date (datetime): Date that individual joined Team.
        end_date (datetime): Date that individual left Team.
        created_at (datetime): Inherited from UUIDAuditBase
        updated_at (datetime): Inherited from UUIDAuditBase
    """

    team_id: UUID | None = field(default=None)
    athlete_id: UUID | None = field(default=None)
    label: str | None = field(default=None, validator=validators.optional(validators.max_len(24)))
    uniform_number: int | None = field(default=None)
    start_date: datetime | None = field(default=None)
    end_date: datetime | None = field(default=None)


# SQLAlchemy Imperative Mapping

individual_membership = Table(
    "individual_membership",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("team_id", SA_UUID, ForeignKey("team.id"), nullable=True),
    Column("athlete_id", SA_UUID, ForeignKey("athlete.id"), nullable=True),
    Column("label", String(24), nullable=True),
    Column("uniform_number", Integer, nullable=True),
    Column("start_date", DateTime(), nullable=True, default=None),
    Column("end_date", DateTime(), nullable=True, default=None),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)


# ORM Relationships

mapper.map_imperatively(
    IndividualMembership,
    individual_membership,
    properties={
        "athlete": relationship("Athlete", back_populates="individual_membership", uselist=False),
        "team": relationship("Team", back_populates="individual_memberships"),
    },
)
