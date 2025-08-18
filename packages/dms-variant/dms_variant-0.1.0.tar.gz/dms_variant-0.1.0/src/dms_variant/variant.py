"""
A dataclass representing a protein variant.

Users are ultimately responsible for validating their inputs.
"""

import re
from dataclasses import dataclass
from typing import Optional

from .mutation import Deletion, Insertion, Missense, Mutation, MutationType, Wildtype

VARIANT_PATTERN = re.compile(
    r"^(?P<wildtype>[A-Z])(?P<position>\d+)(?P<mutation>[A-Z]|del\d+|ins[A-Z]+)$"
)


@dataclass(frozen=True)
class Variant:
    """
    Variant = wildtype + position + mutation

    A mutation could be a:
    - substitution, represented with the resultant AA
    - deletion, represented as 'del' and the number of AAs to be deleted
    - insertion, represented as 'ins' and the sequence to be inserted

    Example:
    Substitution: A123T -> A at position 123 is substituted with T
    Deletion: A123del2 -> 2 AAs are deleted starting from position 123 (inclusive)
    Insertion: A123insGACTCG -> GACTCG is inserted after position 123
    """

    wildtype: str
    position: int
    mutation: Mutation

    def __str__(self) -> str:
        if self.mutation.mutation_type == MutationType.WT:
            return "="

        return f"{self.wildtype}{self.position}{self.mutation}"

    @property
    def mutation_type(self) -> MutationType:
        """Mutation type of this variant"""
        return self.mutation.mutation_type

    @property
    def mut(self) -> str:
        """Get the mutation string representation."""
        return str(self.mutation)

    @property
    def is_wildtype(self) -> bool:
        """Whether this variant is a wildtype"""
        return self.mutation_type == MutationType.WT

    @property
    def is_deletion(self) -> bool:
        """Whether this variant is a deletion"""
        return self.mutation_type == MutationType.DEL

    @property
    def is_insertion(self) -> bool:
        """Whether this variant is an insertion"""
        return self.mutation_type == MutationType.INS

    @property
    def is_substitution(self) -> bool:
        """Whether this variant is a substitution / missense mutation"""
        return self.mutation_type == MutationType.SUB

    @property
    def is_indel(self) -> bool:
        """Whether this variant is an indel (insertion or deletion)"""
        return self.is_insertion or self.is_deletion

    @classmethod
    def from_del(cls, wildtype: str, position: int, length: int) -> "Variant":
        """Construct a variant from a deletion mutation on a position"""
        return cls(wildtype, position, Deletion(length))

    @classmethod
    def from_ins(cls, wildtype: str, position: int, sequence: str) -> "Variant":
        """Construct a variant from an insertion mutation on a position"""
        return cls(wildtype, position, Insertion(sequence))

    @classmethod
    def from_wildtype(cls) -> "Variant":
        """Construct a variant from the wildtype"""
        return cls("", 0, Wildtype())

    @classmethod
    def from_sub(cls, wildtype: str, position: int, mutation: str) -> "Variant":
        """Construct a variant from a substitution mutation on a position"""
        return cls(wildtype, position, Missense(mutation))

    @classmethod
    def from_str(cls, variant: str) -> "Variant":
        """
        Example:
        Substitution: A123T -> A at position 123 is substituted with T
        Insertion: A123insGACTCG -> GACTCG is inserted after position 123
        Deletion: A123del2 -> 2 AAs are deleted starting from position 123 (inclusive)
        Wildtype: "wildtype"
        """

        if variant in ["wildtype", "="]:
            return cls.from_wildtype()

        match = VARIANT_PATTERN.fullmatch(variant)
        if not match:
            raise ValueError(f"Invalid variant: {variant}")

        wildtype, position, mutation = (
            match["wildtype"],
            match["position"],
            match["mutation"],
        )

        return cls(wildtype, int(position), Mutation.from_str(mutation))

    @classmethod
    def parse(
        cls, variant: str, start: Optional[int] = None, end: Optional[int] = None
    ) -> "Variant":
        """
        Parse variant[start:end] into a Variant object.
        """
        return cls.from_str(variant[start:end])
