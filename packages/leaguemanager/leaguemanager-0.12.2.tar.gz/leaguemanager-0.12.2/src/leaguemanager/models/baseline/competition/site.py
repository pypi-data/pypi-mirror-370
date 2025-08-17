from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import SiteBase, add_slug_column, mapper, metadata

if TYPE_CHECKING:
    from .league import League


@define(slots=False)
class Site(SiteBase):
    """Defines a specific location.

    A Site can be assigned to Organization, League, Season, or Fixture base
    objects. This is because different sites can exist based on the matchups.

    Attributes:
        id (UUID): Inherited from UUIDAuditBase
        organization_id (UUID): ForeignKey to Organization
        league_id (UUID): ForeignKey to League.
        season_id (UUID): ForeignKey to Season
        name (str): Descriptive name. (i.e, Barnes Center, The Pinback Complex)
        description (str): Optional description of the site.
        specifier (str): If specific field/rink/area to be designated (i.e., Field C, Gym Court 2, etc...)
        slug (str): Unique slug for the site, used in URLs and identifiers.
        created_at (datetime): Inherited from UUIDAuditBase
        updated_at (datetime): Inherited from UUIDAuditBase
    """

    organization_id: UUID | None = field(default=None)
    league_id: UUID | None = field(default=None)
    season_id: UUID | None = field(default=None)
    name: str | None = field(default=None, validator=validators.max_len(40))
    description: str | None = field(default=None, validator=validators.max_len(100))
    specifier: str | None = field(default=None, validator=validators.max_len(12))
    slug: str | None = field(default=None, validator=validators.optional(validators.max_len(100)))


# SQLAlchemy Imperative Mappings

site = Table(
    "site",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("organization_id", SA_UUID, ForeignKey("organization.id"), nullable=True),
    Column("league_id", SA_UUID, ForeignKey("league.id"), nullable=True),
    Column("season_id", SA_UUID, ForeignKey("season.id"), nullable=True),
    Column("name", String(40), nullable=True),
    Column("description", String(100), nullable=True),
    Column("specifier", String(12), nullable=True),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)

# Add slug column and constraints
add_slug_column(site)

# ORM Relationships

mapper.map_imperatively(
    Site,
    site,
    properties={
        "organization": relationship("Organization", back_populates="site"),
        "league": relationship("League", back_populates="site"),
        "season": relationship("Season", back_populates="site"),
        "ruleset": relationship("Ruleset", back_populates="site"),
        "fixture": relationship("Fixture", back_populates="site", uselist=False),
        "address": relationship("Address", back_populates="site"),
    },
)
