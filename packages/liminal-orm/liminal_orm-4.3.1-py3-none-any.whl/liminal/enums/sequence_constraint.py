from liminal.base.str_enum import StrEnum


class SequenceConstraint(StrEnum):
    """This enum represents hardcoded sequence constraints."""

    BASES = "bases"
    AMINO_ACIDS_IGNORE_CASE = "amino_acids_ignore_case"
    AMINO_ACIDS_EXACT_MATCH = "amino_acids_exact_match"

    @classmethod
    def is_sequence_constraint(cls, constraint: str) -> bool:
        return constraint in cls._value2member_map_
