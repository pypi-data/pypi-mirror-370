from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import IndividualBase, mapper, metadata


@define(slots=False)
class Official(IndividualBase):
    """An official or referee of competitions/fixtures.

    It is sometimes possible for an Official to fill other IndividualBase roles
    (competing/managing). As a result, an Official is primarily linked to an
    OfficialMembership object. The OfficialMembership object will can  then be used
    to track which League or Leagues they can officiate, and can also track start/end
    dates for said membership.

    Notice that many attributes are inherited from the IndividualBase class.

    Attributes:
        id (UUID): Inherited from UUIDAuditBase
        officiating_id (UUID): ForeignKey for Officiating.
        label (str): If present, used to identify the Official.
        license (str): Used to determine if Official has certification and/or license.
        verified (bool): Whether the Official has been verified to officiate.

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

    officiating_id: UUID | None = field(default=None)
    label: str | None = field(default=None, validator=validators.max_len(40))
    license: str | None = field(default=None, validator=validators.optional(validators.max_len(16)))
    verified: bool = field(default=False)


# SQLAlchemy Imperative Mapping

official = Table(
    "official",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("officiating_id", SA_UUID, ForeignKey("officiating.id"), nullable=True),
    Column("label", String(40), unique=True, nullable=False),
    Column("license", String(16), nullable=False),
    Column("verified", Boolean),
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
    Official,
    official,
    properties={
        "officiating": relationship("Officiating", back_populates="officials"),
    },
)
