"""
Mutations, position-agnostic

Includes:
- Wildtype
- Missense
- Insertion
- Deletion
"""

from enum import Enum


class MutationType(Enum):
    """Represents the type of mutation."""

    WT = "wildtype"
    SUB = "substitution"
    DEL = "deletion"
    INS = "insertion"


class Mutation:
    """Represents a mutation, position-agnostic"""

    def __init__(self, mutation_type: MutationType, mutation: int | str):
        self.mutation_type = mutation_type
        self.mutation = mutation

    def __hash__(self):
        return hash((self.mutation_type, self.mutation))

    @classmethod
    def from_str(cls, mutation: str) -> "Mutation":
        """
        Parse the mutation string into a Mutation object.
        """
        if mutation == "=":
            return Wildtype()
        if mutation.startswith("ins"):
            return Insertion(mutation[3:])
        if mutation.startswith("del"):
            return Deletion(int(mutation[3:]))
        return Missense(mutation)

    def __eq__(self, value: object) -> bool:
        return (self.mutation_type == getattr(value, "mutation_type")) and (
            self.mutation == getattr(value, "mutation")
        )


class Wildtype(Mutation):
    """Represents the wildtype"""

    def __init__(self):
        super().__init__(MutationType.WT, 0)

    def __repr__(self) -> str:
        return "Wildtype()"

    def __str__(self) -> str:
        return "="


class Missense(Mutation):
    """Represents a missense mutation"""

    mutation: str

    def __init__(self, mutation: str):
        super().__init__(MutationType.SUB, mutation)

    def __repr__(self) -> str:
        return f"Missense({self.mutation})"

    def __str__(self) -> str:
        return self.mutation


class Insertion(Mutation):
    """Represents an insertion mutation"""

    mutation: str

    def __init__(self, mutation: str):
        super().__init__(MutationType.INS, mutation)

    def __repr__(self) -> str:
        return f"Insertion({self.mutation})"

    def __str__(self) -> str:
        return f"ins{self.mutation}"


class Deletion(Mutation):
    """Represents a deletion mutation"""

    mutation: int

    def __init__(self, mutation: int):
        super().__init__(MutationType.DEL, mutation)

    def __repr__(self) -> str:
        return f"Deletion({self.mutation})"

    def __str__(self) -> str:
        return f"del{self.mutation}"
