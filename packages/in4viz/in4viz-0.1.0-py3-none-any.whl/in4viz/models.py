from typing import List
from enum import Enum
from dataclasses import dataclass


class LineType(Enum):
    STRAIGHT = "straight"
    CRANK = "crank"
    SPLINE = "spline"


@dataclass
class Cardinality:
    from_side: str = "1"  # "1", "0..1", "1..*", "0..*"
    to_side: str = "1"    # "1", "0..1", "1..*", "0..*"


@dataclass
class Column:
    name: str
    logical_name: str
    type: str
    primary_key: bool = False
    nullable: bool = True
    foreign_key: bool = False
    index: bool = False


@dataclass
class Table:
    name: str
    logical_name: str
    columns: List[Column]