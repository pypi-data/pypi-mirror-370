from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import AgentBase, mapper, metadata


@define(slots=False)
class Team(AgentBase):
    """A group of individuals competing as one entitiy.

    Although it may be unusual, it is sometimes possible for a Team to have
    "membership" in different Leagues. For this reason, a Team is not directly
    linked to a League, but rather, to a TeamMebership object. The TeamMembership
    object will then define the League (or Leagues) a Team belongs to, and can
    also track start/end dates for said membership.

    Attributes:
        id (UUID): Inherited from UUIDAuditBase
        team_membership_id (UUID): ForeignKey to TeamMembership.
        team_stats_id (UUID): ForeignKey to TeamStats.
        name (str): Team name.
        active (bool): Defaults to True. Can be used to deactivate this Team.
        created_at (datetime): Inherited from UUIDAuditBase
        updated_at (datetime): Inherited from UUIDAuditBase
    """

    team_membership_id: UUID | None = field(default=None)
    team_stats_id: UUID | None = field(default=None)
    name: str | None = field(default=None, validator=validators.max_len(40))
    active: bool = field(default=True)


# SQLAlchemy Imperative Mappings

team = Table(
    "team",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("team_membership_id", SA_UUID, ForeignKey("team_membership.id"), nullable=True),
    Column("team_stats_id", SA_UUID, ForeignKey("team_stats.id"), nullable=True),
    Column("name", String(40), nullable=False),
    Column("active", Boolean, default=True),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)

# ORM Relationships

mapper.map_imperatively(
    Team,
    team,
    properties={
        "team_membership": relationship("TeamMembership", back_populates="team"),
        "individual_memberships": relationship("IndividualMembership", back_populates="team"),
        "manager_memberships": relationship("ManagerMembership", back_populates="team"),
        "team_stats": relationship("TeamStats", back_populates="team"),
    },
)
