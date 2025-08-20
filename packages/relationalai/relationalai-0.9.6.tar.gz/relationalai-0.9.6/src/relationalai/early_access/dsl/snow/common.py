import dataclasses
from typing import Optional

from relationalai.early_access.builder import (Float, Int128, String, Bool, Date, DateTime,
                                               Concept as QBConcept, Decimal64, Decimal128)


#=
# Physical metadata for a Snowflake table.
#=

@dataclasses.dataclass(frozen=True)
class ColumnRef:
    table: str
    column: str

@dataclasses.dataclass
class ForeignKey:
    name: str
    source_columns: list[ColumnRef] = dataclasses.field(default_factory=list)
    target_columns: list[ColumnRef] = dataclasses.field(default_factory=list)

    def __hash__(self):
        return hash(self.name)

@dataclasses.dataclass
class SchemaMetadata:
    name: str
    foreign_keys: list[ForeignKey] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class ColumnMetadata:
    name: str
    datatype: str
    is_nullable: bool
    numeric_precision: Optional[int] = None
    numeric_precision_radix: Optional[int] = None
    numeric_scale: Optional[int] = None

@dataclasses.dataclass
class CsvColumnMetadata:
    name: str
    datatype: QBConcept

@dataclasses.dataclass
class TabularMetadata:
    name: str
    columns: list[ColumnMetadata] = dataclasses.field(default_factory=list)
    foreign_keys: set[ForeignKey] = dataclasses.field(default_factory=set)


_sf_type_mapping = {
    'varchar': String,
    'char': String,
    'text': String,
    'date': Date,
    'datetime': DateTime,
    'timestamp_ntz': DateTime,
    'boolean': Bool,
    'float': Float,
}

def _map_rai_type(col: ColumnMetadata) -> QBConcept:
    datatype = col.datatype.lower()
    if datatype == 'number' or datatype == 'fixed':
        if col.numeric_scale is not None and col.numeric_scale > 0:
            return _map_decimal_type(col.numeric_precision, col.numeric_scale)
        else:
            return Int128
    else:
        return _sf_type_mapping[datatype]

def _map_decimal_type(precision: Optional[int], scale: Optional[int]) -> QBConcept:
    if precision is None or scale is None:
       raise ValueError("Size and scale must be provided for decimal type mapping")
    if 1 <= precision <= 18:
        return Decimal64
    elif 18 < precision <= 38:
        return Decimal128
    else:
        raise ValueError(f"Unsupported precision {precision} for decimal type mapping")
