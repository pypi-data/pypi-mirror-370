
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Sequence

@dataclass(frozen=True, slots=True)
class Real:
    name: str
    low: float
    high: float

@dataclass(frozen=True, slots=True)
class Int:
    name: str
    low: int
    high: int

@dataclass(frozen=True, slots=True)
class Cat:
    name: str
    choices: Sequence[Any]

@dataclass(frozen=True, slots=True)
class Bool:
    name: str
