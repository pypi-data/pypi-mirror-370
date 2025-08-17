from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import ParticipationBase, mapper, metadata

if TYPE_CHECKING:
    from leaguemanager.models.baseline import Team


@define(slots=False)
class Officiating(ParticipationBase):
    """The participation of an official in a given Fixture.

    Each Official that is participating in an Fixture has an Officiating object that
    represents their involvement in that specific Fixture. It can also be used to track
    attributes specific to the Fixture (i.e., payment, uniform color, etc...)

    Attributes:
        id (UUID): Inherited from UUIDAuditBase
        fixture_id (UUID): ForeignKey to Fixture.
        label (str): Description of Officiating object (i.e., "Ref Jacobs, Week 2, Amateur Mudwrestling", etc...)
        paid (bool): Whether official has been paid for the Fixture.
        created_at (datetime): Inherited from UUIDAuditBase
        updated_at (datetime): Inherited from UUIDAuditBase
    """

    fixture_id: UUID | None = field(default=None)
    label: str | None = field(default=None, validator=validators.max_len(90))
    paid: bool | None = field(default=False)


# SQLAlchemy Imperative Mappings

officiating = Table(
    "officiating",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("fixture_id", SA_UUID, ForeignKey("fixture.id"), nullable=True),
    Column("label", String(90), nullable=False),
    Column("paid", Boolean),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)


# ORM Relationships

mapper.map_imperatively(
    Officiating,
    officiating,
    properties={
        "fixture": relationship("Fixture", back_populates="officiating"),
        "officials": relationship("Official", back_populates="officiating"),
    },
)
