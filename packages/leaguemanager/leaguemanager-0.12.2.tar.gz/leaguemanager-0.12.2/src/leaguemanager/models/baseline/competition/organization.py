from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Column, DateTime, ForeignKey, String, Table
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import GoverningBodyBase, add_slug_column, mapper, metadata

if TYPE_CHECKING:
    from .league import League


@define(slots=False)
class Organization(GoverningBodyBase):
    """Defines the parent organization that administers competition(s).

    This is the top-level object that defines the organization responsible for the rules and
    management of leagues and/or competitions. Generally will have CompetitionBase children
    to describe what kind of competition is being administered.

    Attributes:
        id (UUID): Inherited from UUIDAuditBase
        org_type (str): Type of organization (i.e., amateur, youth, etc...). Inherited from GoverningBodyBase.
        name (str): Descriptive name. (i.e., Coed Hockey League, Flag Football at the Park, etc...)
        description (str): Optional description of the league.
        slug (str): Unique slug for the organization, used in URLs and identifiers.
        created_at (datetime): Inherited from UUIDAuditBase
        updated_at (datetime): Inherited from UUIDAuditBase
    """

    name: str | None = field(default=None, validator=validators.max_len(100))
    description: str | None = field(default=None, validator=validators.optional(validators.max_len(255)))
    slug: str | None = field(default=None, validator=validators.optional(validators.max_len(100)))


organization = Table(
    "organization",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("org_type", String(20), nullable=True),
    Column("name", String(100), nullable=False, unique=True),
    Column("description", String(255), nullable=True),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)

# Add slug column and constraints
add_slug_column(organization)

# ORM Relationships
mapper.map_imperatively(
    Organization,
    organization,
    properties={
        "leagues": relationship("League", back_populates="organization"),
        "site": relationship("Site", back_populates="organization"),
    },
)
