from io import StringIO
from typing import Optional

import numpy as np
import pandas as pd

import relationalai.early_access.builder as qb
from relationalai.early_access.builder import define, where
from relationalai.early_access.builder.std.decimals import parse_decimal64, parse_decimal128
from relationalai.early_access.dsl.bindings.common import BindableColumn, AbstractBindableTable, BindableTable
from relationalai.early_access.dsl.snow.common import CsvColumnMetadata
from relationalai.early_access.dsl.utils import normalize
from relationalai.early_access.rel.rel_utils import DECIMAL64_SCALE, DECIMAL128_SCALE


class BindableCsvColumn(BindableColumn):
    _metadata: CsvColumnMetadata
    _column_basic_type: str

    def __init__(self, metadata: CsvColumnMetadata, table: 'CsvTable', model):
        super().__init__(metadata.name, metadata.datatype, table, model)
        self._metadata = metadata
        self._column_basic_type = "Int64" if metadata.datatype._name == qb.Integer._name else "string"

    def _construct_name(self, col_name: str, col_type: qb.Concept, source: BindableTable):
        """
        Handles the construction of the Relationship name components.

        We use a separate QB relationship per source column, as this allows proper typing.
        """
        short_name = f"{source.physical_name()}_{col_name}"
        madlib = f"{short_name} {{_row_id:RowId}} {{{col_type}}}"
        return madlib, short_name

    def __call__(self, *args):
        """
        Allows the column to be called as a function, which is handy for manual data weaving.

        Example:
            row = Integer.ref()
            where(
                {source}.ID(row, id),
                {source}.NAME(row, name),
                person := Person.new(id=id)
            ).define(
                person,
                Person.name(person, name)
            )
        """
        if len(args) != 2:
            raise ValueError(f'Expected 2 arguments passed to a call to BindableColumn, got {len(args)}')
        return qb.Relationship.__call__(self, *args)

    @property
    def metadata(self):
        return self._metadata

    def basic_type(self):
        return self._column_basic_type

    def decimal_scale(self) -> Optional[int]:
        if self.type() is qb.Decimal64:
            return DECIMAL64_SCALE
        elif self.type() is qb.Decimal128:
            return DECIMAL128_SCALE
        else:
            return None

    def decimal_size(self) -> Optional[int]:
        if self.type() is qb.Decimal64:
            return 64
        elif self.type() is qb.Decimal128:
            return 128
        else:
            return None

    def __repr__(self):
        return f"CSV:{self._source.physical_name()}.{self.physical_name()}"


class CsvTable(AbstractBindableTable[BindableCsvColumn]):
    _basic_type_schema: dict[str, str]
    _csv_data: list[pd.DataFrame]
    _num_rows: int

    def __init__(self, name: str, schema: dict[str, qb.Concept], model):
        super().__init__(name, model, set())
        self._initialize(schema, model)

    def _initialize(self, schema: dict[str, qb.Concept], model):
        self._csv_data = list()
        self._num_rows = 0
        self._cols = {column_name: BindableCsvColumn(CsvColumnMetadata(column_name, column_type), self, model)
                      for column_name, column_type in schema.items()}
        self._basic_type_schema = {col.metadata.name: col.basic_type() for col in self._cols.values()}

    def __str__(self):
        # returns the name of the table, as well as the columns and their types
        return self.physical_name() + ':\n' + '\n'.join(
            [f' {col.metadata.name} {col.metadata.datatype}' for _, col in self._cols.items()]
        ) + '\n' + '\n'.join(
            [f' {fk.source_columns} -> {fk.target_columns}' for fk in self._foreign_keys]
        )

    @property
    def csv_data(self) -> list[pd.DataFrame]:
        return self._csv_data

    def physical_name(self) -> str:
        return self._table.lower()

    def data(self, csv_data: str):
        csv_df = pd.read_csv(StringIO(normalize(csv_data)), dtype=self._basic_type_schema)
        self._csv_data.append(csv_df)
        CsvSourceModule.generate(self, csv_df, row_offset=self._num_rows)
        # update offset now that we generated the rules
        self._num_rows += len(csv_df)

class CsvSourceModule:

    @staticmethod
    def generate(table: CsvTable, data: pd.DataFrame, row_offset: int = 0):
        for local_index, row in enumerate(data.itertuples(index=False)):
            row_index = row_offset + local_index
            for column_name in data.columns:
                value = getattr(row, column_name)
                if pd.notna(value):
                    column = table.__getattr__(column_name)
                    column_type = column.type()
                    if column_type._name == qb.Date._name:
                        CsvSourceModule._row_to_date_value_rule(column, row_index, value)
                    elif column_type._name == qb.DateTime._name:
                        CsvSourceModule._row_to_date_time_value_rule(column, row_index, value)
                    elif column_type._name == qb.Decimal64._name:
                        CsvSourceModule._row_to_decimal64_value_rule(column, row_index, value)
                    elif column_type._name == qb.Decimal128._name:
                        CsvSourceModule._row_to_decimal128_value_rule(column, row_index, value)
                    else:
                        CsvSourceModule._row_to_value_rule(column, row_index, value)

    @staticmethod
    def _row_to_value_rule(column, row, value):
        # if numpy scalar, convert to a native Python type
        if isinstance(value, np.generic):
            value = value.item()
        define(column(row, value))

    @staticmethod
    def _row_to_date_value_rule(column, row, value):
        parse_date = qb.Relationship.builtins['parse_date']
        rez = qb.Date.ref()
        where(parse_date(value, 'Y-m-d', rez)).define(column(row, rez))

    @staticmethod
    def _row_to_date_time_value_rule(column, row, value):
        parse_datetime = qb.Relationship.builtins['parse_datetime']
        rez = qb.DateTime.ref()
        where(parse_datetime(value, 'Y-m-d HH:MM:SS z', rez)).define(column(row, rez))

    @staticmethod
    def _row_to_decimal64_value_rule(column, row, value):
        define(column(row, parse_decimal64(value)))

    @staticmethod
    def _row_to_decimal128_value_rule(column, row, value):
        define(column(row, parse_decimal128(value)))
