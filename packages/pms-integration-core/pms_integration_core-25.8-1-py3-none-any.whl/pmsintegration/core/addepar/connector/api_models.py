import enum
import logging
from collections.abc import Mapping
from datetime import datetime
from typing import Optional, Any, Type, Union, List, Dict

from pydantic import BaseModel, ConfigDict, model_validator, Field

from pmsintegration.core.core_models import (
    LET,
    LenientEntity,
    TypedLenientEntity,
)


class DataWrapper(BaseModel):
    data: Union[LET, Dict[str, LET], List[LET]]  # Handles single item, dict, or list

    @classmethod
    def create(cls, v_: Union[LET, Dict[str, LET], List[LET], None] = None) -> 'DataWrapper':
        """

        :rtype: 'DataWrapper'
        """
        # Default to empty dict if nothing is provided
        if v_ is None:
            v_ = {}
        return cls(data=v_)

    def infer_attributes_type(self) -> Optional[Type[LET]]:
        """Safely infer the type of attributes in the data wrapper."""
        try:
            item = self._extract_item_from_data()
            if item is None:
                return None

            attributes = self._extract_attributes_object(item)
            return self._get_safe_type(attributes)

        except Exception as e:
            logging.error(f"Type inference failed. Data: {self.data}, Error: {str(e)}")
            raise ValueError(f"Failed to infer attributes type: {str(e)}") from e

    def _extract_item_from_data(self):
        """Handle container types and return the first item or None."""
        d = self.data

        if isinstance(d, (int, float, str, bool)):
            logging.warning(f"Primitive type detected: {type(d)}")
            return None

        if isinstance(d, Mapping):
            if not d:
                raise ValueError("Cannot infer type from empty dictionary")
            return next(iter(d.values()))

        if isinstance(d, (list, tuple)):
            if not d:
                logging.warning("Got empty sequence, skipping")
                return None
            return d[0]

        return d

    def _extract_attributes_object(self, item):
        """Extract attributes object through multiple access patterns."""
        if hasattr(item, 'attributes'):
            return item.attributes
        if isinstance(item, (dict, Mapping)) and 'attributes' in item:
            return item['attributes']
        if hasattr(item, '__dict__') and 'attributes' in item.__dict__:
            return item.__dict__['attributes']
        raise ValueError(f"No 'attributes' in {type(item).__name__}")

    def _get_safe_type(self, attributes):
        """Safely get type object from attributes."""
        return attributes if isinstance(attributes, type) else type(attributes)


class APIData(LenientEntity):
    model_config = ConfigDict(extra="forbid")
    id: str | int | None = None
    type: str | None = None
    attributes: LET | None = None
    relationships: Optional[dict[str, DataWrapper]] = None
    links: Optional[dict[str, str | None]] = None

    def unwrap(self):
        return self.attributes

    @model_validator(mode="after")
    def init_attributes(self):
        if self.attributes:
            self.attributes.init(self.relationships)
        return self


class APIResponse(BaseModel):
    data: APIData | list[APIData]
    included: Optional[list[str]] = None
    links: Optional[dict[str, str | None]] = None
    raw: Optional[Any] = None


class APIVersion(TypedLenientEntity):
    ...


class Attribute(TypedLenientEntity):
    id: str | int | None = Field(default=None)
    output_type: str | None = None
    spec_id: int
    usage: list[str] | None = None
    created_at: datetime | None = None
    display_name: str
    category: str
    modified_at: datetime | None = None


class EntityAttributeWritability(enum.Enum):
    IMMUTABLE = "IMMUTABLE"
    MUTABLE = "MUTABLE"
    FINAL = "FINAL"
    RESTRICTED_FOR_ONLINE_INTERNAL = "RESTRICTED_FOR_ONLINE_INTERNAL"


class OwnershipType(enum.Enum):
    PERCENT_BASED = "PERCENT_BASED"
    SHARE_BASED = "SHARE_BASED"
    VALUE_BASED = "VALUE_BASED"


class EntityAttribute(BaseModel):
    key: str
    required: bool
    writability: EntityAttributeWritability


class EntityType(LenientEntity):
    display_name: str
    ownership_type: str | None = None
    category: str | None = None
    entity_attributes: list[EntityAttribute]


class GroupType(LenientEntity):
    is_permissioned_resource: bool
    group_type_key: str | None = None
    display_name: str | None = None
