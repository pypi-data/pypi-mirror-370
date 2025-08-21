from __future__ import annotations

from typing import Any

from pydantic import ConfigDict, field_validator

from liminal.base.properties.base_name_template import BaseNameTemplate
from liminal.orm.name_template_parts import NameTemplateParts, SeparatorPart


class NameTemplate(BaseNameTemplate):
    """
    This class is the validated class that is public facing and inherits from the BaseNameTemplate class.
    It has the same fields as the BaseNameTemplate class, but it is validated to ensure that the fields are valid.

    Parameters
    ----------
    parts : list[NameTemplatePart] = []
        The list of name template parts that make up the name template (order matters). Defaults to no parts, an empty list.
    order_name_parts_by_sequence : bool = False
        Whether to order the name parts by sequence. This can only be set to True for sequence enity types. If one or many part link fields are included in the name template,
        list parts in the order they appear on the sequence map, sorted by start position and then end position. Defaults to False.
    """

    parts: list[NameTemplateParts] = []
    order_name_parts_by_sequence: bool = False

    @field_validator("parts")
    def validate_parts(cls, v: list[NameTemplateParts]) -> list[NameTemplateParts]:
        if len(v) > 0 and all(isinstance(part, SeparatorPart) for part in v):
            raise ValueError(
                "This name template will produce an empty name because it only includes separators. Please include at least one non-separator component."
            )
        return v

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
