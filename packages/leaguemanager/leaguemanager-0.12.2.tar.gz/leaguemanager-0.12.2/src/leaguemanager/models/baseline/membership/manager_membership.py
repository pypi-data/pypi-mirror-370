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
class ManagerMembership(MembershipBase):
    """An manager's affiliation with a Team.

    Instead of linking an Manager object directly to a team, the Manager is linked
    to an ManagerMembership object, which defines their specific affiliation to a
    given team. That way, an Manager can be linked to different ManagerMembership
    objects, each connected to different Teams (in the event that an Manager has multiple
    team affiliations). The ManagerMembership object can define properties specific
    to a Team, such as management role, start and end dates, etc...

    Attributes:
        id (UUID): Inherited from UUIDAuditBase
        team_id (UUID): ForeignKey to Team.
        manager_id (UUID): ForeignKey to Manager.
        label (str): Label describing the Manager association (i.e., Henry Cooper, Team A, etc...)
        role (str): Role within the team (i.e., Head Coach, Assistant, Trainer, etc...)
        start_date (datetime): Date that individual joined Team.
        end_date (datetime): Date that individual left Team.
        created_at (datetime): Inherited from UUIDAuditBase
        updated_at (datetime): Inherited from UUIDAuditBase
    """

    team_id: UUID | None = field(default=None)
    manager_id: UUID | None = field(default=None)
    label: str | None = field(default=None, validator=validators.optional(validators.max_len(24)))
    role: str | None = field(default=None, validator=validators.optional(validators.max_len(12)))
    start_date: datetime | None = field(default=None)
    end_date: datetime | None = field(default=None)


# SQLAlchemy Imperative Mapping

manager_membership = Table(
    "manager_membership",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("team_id", SA_UUID, ForeignKey("team.id"), nullable=True),
    Column("manager_id", SA_UUID, ForeignKey("manager.id"), nullable=True),
    Column("label", String(24), nullable=True),
    Column("role", String(12), nullable=True),
    Column("start_date", DateTime(), nullable=True, default=None),
    Column("end_date", DateTime(), nullable=True, default=None),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)


# ORM Relationships

mapper.map_imperatively(
    ManagerMembership,
    manager_membership,
    properties={
        "manager": relationship("Manager", back_populates="manager_membership", uselist=False),
        "team": relationship("Team", back_populates="manager_memberships"),
    },
)
