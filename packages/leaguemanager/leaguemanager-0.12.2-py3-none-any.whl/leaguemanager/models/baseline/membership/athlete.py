from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import IndividualBase, mapper, metadata
from leaguemanager.models.enums import Gender


@define(slots=False)
class Athlete(IndividualBase):
    """A member of a team or individual competitor.

    It is sometimes possible for an Athlete to belong to different Teams,
    or in some cases, fill other IndividualBase roles (officiating/managing). As
    a result, an Athlete is not directly linked to a Team, but rather to a
    AthleteMembership object. The AthleteMembership object will then define
    the Team an Athlete belongs to, and can also track start/end dates for said
    membership.

    Note that many attributes are inherited from the IndividualBase class.

    Attributes:
        id (UUID): Inherited from UUIDAuditBase
        user_id (UUID): ForeignKey to User.
        athlete_stats (UUID): ForeignKey to AthleteStats.
        label (str): If present, used to identify the Athlete.
        birth_date (datetime): Inherited from IndividualBase.
        birth_year (int): Inherited from IndividualBase.
        sex (str): Inherited from IndividualBase.
        gender (str): Inherited from IndividualBase.
        verified (bool): Whether the Athlete has been verified to compete.

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

    label: str | None = field(default=None, validator=validators.optional(validators.max_len(40)))
    verified: bool = field(default=False)
    birth_date: datetime | None = field(default=None)
    birth_year: int | None = field(default=None)
    sex: str | None = field(default=None, validator=validators.optional(validators.in_(("male", "female"))))
    gender: str | None = field(default=None, validator=validators.optional(validators.in_((e.value for e in Gender))))


# SQLAlchemy Imperative Mapping

athlete = Table(
    "athlete",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("user_id", SA_UUID, ForeignKey("user_account.id"), nullable=True),
    Column("athlete_stats_id", SA_UUID, ForeignKey("athlete_stats.id"), nullable=True),
    Column("label", String(40), unique=True, nullable=True),
    Column("verified", Boolean),
    Column("first_name", String(20), nullable=True),
    Column("middle_name", String(20), nullable=True),
    Column("last_name", String(20), nullable=True),
    Column("full_name", String(64), nullable=True),
    Column("alias", String(40), nullable=True),
    Column("email", String(40), nullable=True),
    Column("mobile_phone", String(16), nullable=True),
    Column("birth_date", DateTime, nullable=True),
    Column("birth_year", Integer, nullable=True),
    Column("sex", String(6), nullable=True),
    Column("gender", String(12), nullable=True),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)


# ORM Relationships

mapper.map_imperatively(
    Athlete,
    athlete,
    properties={
        "individual_membership": relationship("IndividualMembership", back_populates="athlete", uselist=False),
        "athlete_stats": relationship("AthleteStats", back_populates="athlete"),
    },
)
