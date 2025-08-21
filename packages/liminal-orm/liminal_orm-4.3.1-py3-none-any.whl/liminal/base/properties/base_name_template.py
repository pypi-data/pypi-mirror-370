from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from liminal.orm.name_template_parts import NameTemplateParts


class BaseNameTemplate(BaseModel):
    """
    This class is the generic class for defining the name template.
    It is used to create a diff between the old and new name template.

    Parameters
    ----------
    parts : list[NameTemplatePart] | None
        The list of name template parts that make up the name template (order matters).
    order_name_parts_by_sequence : bool | None
        Whether to order the name parts by sequence. This can only be set to True for sequence enity types. If one or many part link fields are included in the name template,
        list parts in the order they appear on the sequence map, sorted by start position and then end position.
    """

    parts: list[NameTemplateParts] | None = None
    order_name_parts_by_sequence: bool | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def merge(self, new_props: BaseNameTemplate) -> dict[str, Any]:
        """Creates a diff between the current name template and the new name template.
        Sets value to None if the values are equal, otherwise sets the value to the new value.

        Parameters
        ----------
        new_props : BaseNameTemplate
            The new name template.

        Returns
        -------
        dict[str, Any]
            A dictionary of the differences between the old and new name template.
        """
        diff = {}
        for field_name in self.model_fields:
            new_val = getattr(new_props, field_name)
            if getattr(self, field_name) != new_val:
                diff[field_name] = new_val
        return diff

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseNameTemplate):
            return False
        return self.model_dump() == other.model_dump()

    def __str__(self) -> str:
        parts_str = (
            f"parts=[{', '.join(repr(part) for part in self.parts)}]"
            if self.parts is not None
            else None
        )
        order_name_parts_by_sequence_str = (
            f"order_name_parts_by_sequence={self.order_name_parts_by_sequence}"
            if self.order_name_parts_by_sequence is not None
            else None
        )
        return ", ".join(filter(None, [parts_str, order_name_parts_by_sequence_str]))

    def __repr__(self) -> str:
        """Generates a string representation of the class so that it can be executed."""
        model_dump = self.model_dump(exclude_defaults=True, exclude_unset=True)
        props = []
        if "parts" in model_dump:
            parts_repr = (
                f"[{', '.join(repr(part) for part in self.parts)}]"
                if self.parts
                else "[]"
            )
            props.append(f"parts={parts_repr}")
        if "order_name_parts_by_sequence" in model_dump:
            props.append(
                f"order_name_parts_by_sequence={self.order_name_parts_by_sequence}"
            )
        return f"{self.__class__.__name__}({', '.join(props)})"
