from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Annotated, Any, ClassVar, Generic, Protocol, TypeVar, runtime_checkable

from attr import fields

from litestar.dto.base_dto import AbstractDTO
from litestar.dto.data_structures import DTOFieldDefinition
from litestar.dto.field import DTOField, extract_dto_field
from litestar.params import DependencyKwarg, KwargDefinition
from litestar.types.empty import Empty

if TYPE_CHECKING:
    from typing import Collection, Generator

    from litestar.types.protocols import AttrsProtocol
    from litestar.typing import FieldDefinition


__all__ = ("AttrsDTO", "T")


@runtime_checkable
class AttrsProtocol(Protocol):
    """Protocol for instance checking attrs classes"""

    __attrs_attrs__: ClassVar[dict[str, Any]]


T = TypeVar("T", bound="AttrsProtocol | Collection[AttrsProtocol]")
AnyAttrs = TypeVar("AnyAttrs", bound="AttrsProtocol")


class AttrsDTO(AbstractDTO[T], Generic[T]):
    """Support for domain modelling with attrs."""

    @classmethod
    def generate_field_definitions(cls, model_type: type[AttrsProtocol]) -> Generator[DTOFieldDefinition, None, None]:
        attr_fields = {f.name: f for f in fields(model_type)}
        properties = cls.get_property_fields(model_type)
        for key, field_definition in cls.get_model_type_hints(model_type).items():
            if not (attr_field := attr_fields.get(key)):
                continue
            default = attr_field.default if attr_field.default else Empty
            default_factory = getattr(attr_field, "factory", None) or None
            field_definition = dataclasses.replace(
                DTOFieldDefinition.from_field_definition(
                    field_definition=field_definition,
                    default_factory=default_factory,
                    dto_field=extract_dto_field(field_definition, attr_field.metadata),
                    model_name=model_type.__name__,
                ),
                name=key,
                default=default,
            )
            yield (
                dataclasses.replace(field_definition, default=Empty, kwarg_definition=default)
                if isinstance(default, (KwargDefinition, DependencyKwarg))
                else field_definition
            )
        for key, property_field in properties.items():
            if key.startswith("_"):
                continue
            yield DTOFieldDefinition.from_field_definition(
                property_field,
                model_name=model_type.__name__,
                default_factory=None,
                dto_field=DTOField(mark="read-only"),
            )

    @classmethod
    def detect_nested_field(cls, field_definition: FieldDefinition) -> bool:
        return hasattr(field_definition.annotation, "__attrs_attrs__")
