#!/usr/bin/env python3

import json
from argparse import ArgumentParser
from enum import Enum
from typing import Dict, List, Optional

parser = ArgumentParser()

parser.add_argument(
    "-f",
    "--filepath",
    dest="filepath",
    required=True,
    help="Filename",
)

args = parser.parse_args()

print(f"Reading {args.filepath}")
f = open(args.filepath)
j = json.load(f)
f.close()

# IDEA
# We recurse through a JSON dictionary.
# For every key:value pair, we check whether we have seen the value structure
# before, if not, we will add it to our set of value structures.
# We start out with the basic value structures, and gradually observe every
# uniquely identifiable structure. At the end of it all, we are able to
# identify common substructures within the JSON structure.


class BasicType(Enum):
    Null = 0
    Boolean = 1
    Number = 2
    String = 3


class TypeDefinition:
    # Pointers used in the string representation, reset it manually if multiple
    # type definitions are extracted within a single Python interpreted program
    Ps: List[int] = []

    # Initial value structures
    S: Dict["TypeDefinition", int] = {}
    C: int = 1

    # Hash value
    H: Optional[int] = None

    # Basic / Dictionary / List
    B: Optional[BasicType] = None
    D: Optional[Dict[str, "TypeDefinition"]] = None
    L: Optional[List["TypeDefinition"]] = None

    # Pointer
    P: Optional[int] = None

    def __init__(
        self,
        B: Optional[BasicType] = None,
        D: Optional[dict] = None,
        L: Optional[list] = None,
    ):
        if B is not None:
            self.B = B
        if D is not None:
            self.D = D
        if L is not None:
            self.L = L

        # Add this type definition to the set of types
        if self not in TypeDefinition.S:
            TypeDefinition.S[self] = TypeDefinition.C
            TypeDefinition.C += 1

    def _compute_hash(self):
        if self.B is not None:
            h = self.B.name.__hash__()
            return h

        if self.D is not None:
            h = 1
            for k, v in self.D.items():
                h += k.__hash__() * 13
                h += v.__hash__() * 13
            return h

        if self.L is not None:
            h = 2
            for e in self.L:
                h += e.__hash__() * 13
            return h

        raise RuntimeError(f"Hashing an empty TypeDefinition for {self}")

    def __hash__(self):
        if self.H is None:
            self.H = self._compute_hash()

        return self.H

    def __eq__(self, o):
        if self.__hash__() == o.__hash__():
            # TODO Add an operation to check equality for certain, as hashes
            # will eventually collide.
            return True

        return False

    def __repr__(self, pointer=True, skip=False):
        """
        If pointer=True, we ought to return the pointer every chance we get.
        However, sometimes we may want to skip at least one level of depth, to
        make sure we do not reduce everything to a pointer. Especially basic
        types (Null, String, Number, Boolean) should not be reduced to a
        pointer.
        """
        if self.B is None and self.P is not None and pointer and not skip:
            s = f'"{self.P}"'
            TypeDefinition.Ps.append(self.P)
            return s

        if self.D is not None:
            # DICTIONARY
            s = (
                "{"
                + ",".join(
                    [
                        f'"{key}":{value.__repr__(pointer)}'
                        for key, value in self.D.items()
                    ]
                )
                + "}"
            )
            return s

        if self.L is not None:
            # LIST
            s = "[" + ",".join([f"{value.__repr__(pointer)}" for value in self.L]) + "]"
            return s

        if self.B is not None:
            # BASIC
            return f'"{str(self.B.name)}"'

        raise RuntimeError(f"Trying to return a string representation for {self}")

    @staticmethod
    def from_dict(C) -> "TypeDefinition":
        if isinstance(C, dict):
            r = {}
            for k in C:
                v = TypeDefinition.from_dict(C[k])
                r[k] = v
                if v in TypeDefinition.S:
                    # Replace it by a "pointer" to the type definition later
                    v.P = TypeDefinition.S[v]

            return TypeDefinition(D=r)

        if isinstance(C, list):
            # ASSUMPTION a list of elements is always a list containing 1 type
            # of element
            l = []
            for e in C:
                v = TypeDefinition.from_dict(e)
                l.append(v)
                if v in TypeDefinition.S:
                    # Replace it by a "pointer" to the type definition later
                    v.P = TypeDefinition.S[v]
                break

            return TypeDefinition(L=l)

        if C is None:
            return TypeDefinition(B=BasicType.Null)

        if isinstance(C, bool):
            return TypeDefinition(B=BasicType.Boolean)

        if isinstance(C, int) or isinstance(C, float):
            return TypeDefinition(B=BasicType.Number)

        if isinstance(C, str):
            return TypeDefinition(B=BasicType.String)

        raise RuntimeError(f"Can not detect a type for {C}")


root = TypeDefinition.from_dict(j)
print("Freshly parsed")
print(root)
result = json.loads(root.__repr__(pointer=True))

print("Types")
types = {}
for k, v in TypeDefinition.S.items():
    types[v] = json.loads(k.__repr__(pointer=True, skip=True))

print(json.dumps(types, indent=2))

print("Result")
print(json.dumps(result, indent=2))
