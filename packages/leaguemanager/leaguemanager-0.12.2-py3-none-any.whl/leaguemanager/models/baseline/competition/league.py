from __future__ import annotations

from datetime import UTC, datetime

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import CompetitionBase, add_slug_column, mapper, metadata

if TYPE_CHECKING:
    from uuid import UUID

    from .organization import Organization


@define(slots=False)
class League(CompetitionBase):
    """Defines the top level of a competition.

    This is ordinarily a child of the Organization (GoverningBody) and usually refers to
    a recurring competition type (i.e., Soccer League, Little League Baseball, etc...).
    Each League can have Season and/or other CompetitionBase-type objects as children.

    Attributes:
        id (UUID): Inherited from UUIDAuditBase
        organization_id (UUID): ForeignKey to Organization.
        competition_type (str): Describes competiton type. Inherited from CompetitionBase.
        name (str): Descriptive name. (i.e., Coed Hockey League, Flag Football at the Park, etc...)
        description (str): Optional description of the league.
        active (bool): Defaults to True. Can be used to deactivate this League.
        slug (str): Unique slug for the league, used in URLs and identifiers.
        created_at (datetime): Inherited from UUIDAuditBase
        updated_at (datetime): Inherited from UUIDAuditBase
    """

    organization_id: UUID | None = field(default=None)
    competition_type: str | None = field(default="recurring-competition", validator=validators.max_len(30))
    name: str | None = field(default=None, validator=validators.max_len(80))
    description: str | None = field(default=None, validator=validators.optional(validators.max_len(120)))
    active: bool = field(default=True)
    slug: str | None = field(default=None, validator=validators.optional(validators.max_len(100)))


# SQLAlchemy Imperative Mappings

league = Table(
    "league",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("organization_id", SA_UUID, ForeignKey("organization.id"), nullable=True),
    Column("competition_type", String(30), default=("recurring-competition"), nullable=False),
    Column(
        "name",
        String(80),
        nullable=False,
        unique=True,
    ),
    Column("description", String(120), nullable=True),
    Column("active", Boolean, default=True),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)

# Add slug column and constraints
add_slug_column(league)

# ORM Relationships

mapper.map_imperatively(
    League,
    league,
    properties={
        "organization": relationship("Organization", back_populates="leagues"),
        "seasons": relationship("Season", back_populates="league"),
        "site": relationship("Site", back_populates="league"),
        "league_properties": relationship(
            "LeagueProperties", back_populates="league", uselist=False, cascade="all, delete-orphan"
        ),
    },
)
