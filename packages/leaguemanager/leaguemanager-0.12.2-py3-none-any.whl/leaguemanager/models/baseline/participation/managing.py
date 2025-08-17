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
class Managing(ParticipationBase):
    """The participation of a Manager in a given Fixture.

    Each Manager that is participating in an Fixture has a Managing object that
    represents their involvement in that specific Fixture. It can also be used to track
    attributes specific to the Fixture.

    Attributes:
        id (UUID): Inherited from UUIDAuditBase
        fixture_id (UUID): ForeignKey to Fixture.
        label (str): Description of Managing object (i.e., "Ref Jacobs, Week 2, Amateur Mudwrestling", etc...)
        notes (str): Can be used to describe game specific notes.
        created_at (datetime): Inherited from UUIDAuditBase
        updated_at (datetime): Inherited from UUIDAuditBase
    """

    fixture_id: UUID | None = field(default=None)
    label: str | None = field(default=None, validator=validators.max_len(40))
    notes: str | None = field(default=None, validator=validators.optional(validators.max_len(90)))


# SQLAlchemy Imperative Mappings

managing = Table(
    "managing",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("fixture_id", SA_UUID, ForeignKey("fixture.id"), nullable=True),
    Column("label", String(40), nullable=False),
    Column("notes", String(90), nullable=False),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)


# ORM Relationships

mapper.map_imperatively(
    Managing,
    managing,
    properties={
        "fixture": relationship("Fixture", back_populates="managing"),
        "managers": relationship("Manager", back_populates="managing"),
    },
)
