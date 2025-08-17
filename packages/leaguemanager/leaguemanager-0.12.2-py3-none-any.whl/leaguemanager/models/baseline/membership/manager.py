from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Column, DateTime, ForeignKey, String, Table
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import IndividualBase, mapper, metadata


@define(slots=False)
class Manager(IndividualBase):
    """A manager/coach or part of coaching staff for a Team.

    It is sometimes possible for an Manager to mnage different Teams,
    or in some cases, fill other IndividualBase roles (officiating/competing). As
    a result, a Manager is not directly linked to a Team, but rather to a
    ManagerMembership object. The ManagerMembership object will then define
    the Team that they manage, a and it can also track start/end dates for said
    membership.

    Notice that many attributes are inherited from the IndividualBase class.

    Attributes:
        id (UUID): Inherited from UUIDAuditBase
        managing_id (UUID): ForeignKey to Managing.
        label (str): If present, used to identify the Manager.

        first_name (str): Inherited from IndividualBase.
        middle_name (str): Inherited from IndividualBase.
        last_name (str): Inherited from IndividualBase.
        full_name (str): Inherited from IndividualBase.
        alias (str): Inherited from IndividualBase.
        email (str): Inherited from IndividualBase.
        mobile_phone (str): Inherited from IndividualBase.
        created_at (datetime): Inherited from UUIDAuditBase
        updated_at (datetime): Inherited from UUIDAuditBase
    """

    managing_id: UUID | None = field(default=None)
    label: str | None = field(default=None, validator=validators.max_len(40))


# SQLAlchemy Imperative Mapping

manager = Table(
    "manager",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("managing_id", SA_UUID, ForeignKey("managing.id"), nullable=True),
    Column("label", String(40), unique=True, nullable=False),
    Column("first_name", String(20), nullable=True),
    Column("middle_name", String(20), nullable=True),
    Column("last_name", String(20), nullable=True),
    Column("full_name", String(64), nullable=True),
    Column("alias", String(40), nullable=True),
    Column("email", String(40), nullable=True),
    Column("mobile_phone", String(16), nullable=True),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)


# ORM Relationships

mapper.map_imperatively(
    Manager,
    manager,
    properties={
        "manager_membership": relationship("ManagerMembership", back_populates="manager", uselist=False),
        "managing": relationship("Managing", back_populates="managers"),
    },
)
