"""Base classes for database objects are loosely based on IPTC Sport Schema. see: https://sportschema.org"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Protocol
from uuid import UUID, uuid4

from attrs import converters, define, field, validators
from sqlalchemy import MetaData
from sqlalchemy.orm import Mapper, registry
from sqlalchemy.sql import FromClause

from .slug import add_slug_column

mapper = registry()
metadata = MetaData()

##############
# BASE OBJECTS
##############


@define(slots=False)
class UUIDBase:
    id: UUID = field(factory=uuid4)

    if TYPE_CHECKING:
        __table__: FromClause
        __mapper__: Mapper[Any]
        __name__: str

    def to_dict(self, exclude: set[str] | None = None) -> dict[str, Any]:
        """Convert model to dictionary.

        Returns:
            Dict[str, Any]: A dict representation of the model
        """
        exclude = {"sa_orm_sentinel", "_sentinel"}.union(self._sa_instance_state.unloaded).union(exclude or [])  # type: ignore[attr-defined]
        return {
            field: getattr(self, field)
            for field in self.__mapper__.columns.keys()  # noqa: SIM118
            if field not in exclude
        }

    def str_to_iso(date_string: str, format: str):
        """Converts string to datetime object."""
        return datetime.strptime(date_string, format)


@define(slots=False)
class UUIDAuditBase(UUIDBase):
    created_at: datetime = field(factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(factory=lambda: datetime.now(UTC))


##########################
# COMPETITION OBJECT TYPES
##########################


@define(slots=False)
class GoverningBodyBase(UUIDAuditBase):
    """Base class for organization responsible for running competitions."""

    org_type: str | None = field(default="amateur-league", validator=validators.max_len(20))


@define(slots=False)
class CompetitionBase(UUIDAuditBase):
    """Base class for competitions. Can be child of Governing Body or other Competitions.

    The competition_type attribute should describe whether the object is meant to be a recurring
    construct (i.e., recurring-competition), or something finite (i.e., competition, tournament).
    The value of this property will vary based on the object that inherits this class.

    #TODO: May need to create a constraint with pre-determined types.
    """

    # competition_type: str | None = field(default="recurring-competition", validator=validators.max_len(30))


@define(slots=False)
class CompetitionPhaseBase(CompetitionBase):
    """A sub-group of events within a competition (i.e., regular, semifinals, knockout round, etc...)"""

    phase_type: str | None = field(default="regular", validator=validators.max_len(30))


@define(slots=False)
class EventBase(UUIDAuditBase):
    """Base class for an event (match/fixture) that produces results."""

    ...


@define(slots=False)
class ActionBase(UUIDAuditBase):
    """Base class for actions related to an event."""

    ...


@define(slots=False)
class PropertiesBase(UUIDAuditBase):
    """Base class for rules or properties."""


#########################
# MEMBERSHIP OBJECT TYPES
#########################


@define(slots=False)
class AgentBase(UUIDAuditBase):
    """Base class for Individual, Team, or Club."""

    ...


@define(slots=False)
class IndividualBase(AgentBase):
    """All individuals will inherit these properties, but properties optional to allow anonymous usage."""

    first_name: str | None = field(default=None, validator=validators.optional(validators.max_len(20)))
    last_name: str | None = field(default=None, validator=validators.optional(validators.max_len(20)))
    middle_name: str | None = field(default=None, validator=validators.optional(validators.max_len(20)))
    full_name: str | None = field(default=None, validator=validators.optional(validators.max_len(64)))
    alias: str | list[str] | None = field(default=None)
    email: str | None = field(default=None, validator=validators.optional(validators.max_len(40)))
    mobile_phone: str | None = field(default=None, validator=validators.optional(validators.max_len(16)))


@define(slots=False)
class MembershipBase(UUIDAuditBase):
    """Defines membership of an entity in another entity for a given time."""

    ...


############################
# PARTICIPATION OBJECT TYPES
############################


@define(slots=None)
class SiteBase(UUIDBase):
    """Base class for a given site."""

    ...


@define(slots=None)
class ParticipationBase(UUIDAuditBase):
    """Base class for modeling participation of an actor in an event."""

    ...


@define(slots=None)
class TeamParticipationBase(ParticipationBase):
    """Base class for team stats in an Event."""

    ...


@define(slots=False)
class OfficialParticipationBase(ParticipationBase):
    """Base class for involvement of Officials in an Event."""

    ...


@define(slots=False)
class IndividualParticipationBase(ParticipationBase):
    """Base class for individual stats in an Event."""

    ...
