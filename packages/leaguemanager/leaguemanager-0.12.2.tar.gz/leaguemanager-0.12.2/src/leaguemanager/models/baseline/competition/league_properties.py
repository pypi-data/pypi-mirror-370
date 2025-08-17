from __future__ import annotations

from datetime import UTC, datetime

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table
from sqlalchemy import Enum as SA_Enum
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import PropertiesBase, mapper, metadata
from leaguemanager.models.enums import Category, MatchDay

if TYPE_CHECKING:
    from uuid import UUID

    from .organization import Organization


def category_converter(value):
    if isinstance(value, Category):
        return value.name
    return value


@define(slots=False)
class LeagueProperties(PropertiesBase):
    """Defines the properties specific to a Competition, such as a League.

    It broadly describes qualifiers for a competition, which can include the sport, age class,
    day of competition, or other categories (such as "Coed" or "Division 2").

    Attributes:
        id (UUID): Inherited from UUIDAuditBase
        site_id (UUID): ForeignKey to Site.
        league_id (UUID): ForeignKey to League.
        sport (str): The sport type of the League.
        category (str): Defines if league is Women, Men, or Coed.
        division (str): Indicates the "Division" of a League (i.e., "Div 3", "B League", etc...)
        created_at (datetime): Inherited from UUIDAuditBase
        updated_at (datetime): Inherited from UUIDAuditBase
    """

    site_id: UUID | None = field(default=None)
    league_id: UUID | None = field(default=None)
    sport: str | None = field(default=None, validator=validators.max_len(16))
    category: str | None = field(
        default=None,
        converter=category_converter,
        validator=validators.optional(validators.in_({a.name for a in Category})),
    )
    division: str | None = field(default=None, validator=validators.max_len(12))


# SQLAlchemy Imperative Mappings

league_properties = Table(
    "league_properties",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("site_id", SA_UUID, ForeignKey("site.id"), nullable=True),
    Column("league_id", SA_UUID, ForeignKey("league.id"), nullable=True),
    Column("sport", String(16), nullable=True),
    Column("category", SA_Enum(Category), nullable=True),
    Column("division", String(12), nullable=True),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)


# ORM Relationships

mapper.map_imperatively(
    LeagueProperties,
    league_properties,
    properties={"league": relationship("League", back_populates="league_properties")},
)
