from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Column:
    name: str  # supports dot notation e.g. car.engine.hp
    data_type: str  # e.g. string, int, boolean, date, timestamp, decimal, float, double
    description: Optional[str] = None


@dataclass
class Table:
    name: str
    description: Optional[str] = None
    columns: List[Column] = field(default_factory=list)


@dataclass
class Lake:
    name: str
    description: Optional[str] = None
    tables: List[Table] = field(default_factory=list)


@dataclass
class Model:
    lakes: List[Lake] = field(default_factory=list)
