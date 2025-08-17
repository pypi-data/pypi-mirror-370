from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import UUIDBase, mapper, metadata
from leaguemanager.models.enums import Category, Division, MatchDay

if TYPE_CHECKING:
    from leaguemanager.models.baseline.competition import Site


@define(slots=False)
class Address(UUIDBase):
    """Defines the street address of another object"""

    site_id: UUID | None = field(default=None)
    city_id: UUID | None = field(default=None)
    street: str | None = field(default=None, validator=validators.optional(validators.max_len(120)))
    postal_code: str | None = field(default=None, validator=validators.optional(validators.max_len(20)))


@define(slots=False)
class City(UUIDBase):
    """Defines a city with a name and an optional country code."""

    state_id: UUID | None = field(default=None)
    city_name: str | None = field(default=None, validator=validators.max_len(80))


@define(slots=False)
class State(UUIDBase):
    """Defines a state with a name and an optional country code."""

    country_id: UUID | None = field(default=None)
    state_name: str | None = field(default=None, validator=validators.max_len(80))
    state_code: str | None = field(default=None, validator=validators.optional(validators.max_len(3)))


@define(slots=False)
class Country(UUIDBase):
    """Defines a country with a name and an optional country code."""

    country_name: str | None = field(default=None, validator=validators.max_len(80))
    country_code: str | None = field(default=None, validator=validators.optional(validators.max_len(3)))


# SQLAlchemy Imperative Mappings
address = Table(
    "address",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("site_id", SA_UUID, ForeignKey("site.id"), nullable=True),
    Column("city_id", SA_UUID, ForeignKey("city.id"), nullable=True),
    Column("street", String(120), nullable=True),
    Column("postal_code", String(20), nullable=True),
)

city = Table(
    "city",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("state_id", SA_UUID, ForeignKey("state.id"), nullable=True),
    Column("city_name", String(80), nullable=False),
)
state = Table(
    "state",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("country_id", SA_UUID, ForeignKey("country.id"), nullable=True),
    Column("state_name", String(80), nullable=False),
    Column("state_code", String(3), nullable=True),
)
country = Table(
    "country",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("country_name", String(80), nullable=False),
    Column("country_code", String(3), nullable=True),
)

# ORM Relationships
mapper.map_imperatively(
    Address,
    address,
    properties={
        "site": relationship("Site", back_populates="address", uselist=False),
        "city": relationship("City", back_populates="addresses"),
    },
)

mapper.map_imperatively(
    City,
    city,
    properties={
        "state": relationship("State", back_populates="cities"),
        "addresses": relationship("Address", back_populates="city", uselist=True),
    },
)

mapper.map_imperatively(
    State,
    state,
    properties={
        "country": relationship("Country", back_populates="states"),
        "cities": relationship("City", back_populates="state", uselist=True),
    },
)

mapper.map_imperatively(
    Country,
    country,
    properties={
        "states": relationship("State", back_populates="country", uselist=True),
    },
)
