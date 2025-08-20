from relationalai.early_access.builder import annotations
from relationalai.early_access.dsl.bindings.common import BindableColumn, AbstractBindableTable, BindableTable, Symbol
from relationalai.early_access.dsl.snow.common import ColumnMetadata, _map_rai_type

import relationalai.early_access.builder as qb


#=
# Bindable classes and interfaces.
#=

class BindableSnowflakeColumn(BindableColumn):
    _metadata: ColumnMetadata

    def __init__(self, metadata: ColumnMetadata, table: 'SnowflakeTable', model):
        col_name = metadata.name
        col_type = _map_rai_type(metadata)
        super().__init__(col_name, col_type, table, model)
        self._metadata = metadata
        self.annotate(annotations.external)  # so we generate no declares, as there's one for the table

    def _construct_name(self, col_name: str, col_type: qb.Concept, source: BindableTable):
        """
        Handles the construction of the Relationship name components.

        For tabular sources coming from Snowflake, we need to specialize the relation that's been created for the table.
        We use separate QB relationships, as this allows proper typing, but in core Rel it's treated as a single
        relation; hence the name is the same.
        """
        short_name = source.physical_name()
        madlib = f"{short_name} {{_col_name:Symbol}} {{_row_id:RowId}} {{{col_type}}}"
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
        if len(args) == 2:
            args = [Symbol(self.physical_name()), *args]
        if len(args) != 3:
            raise ValueError(f'Expected 2 arguments passed to a call to BindableColumn, got {len(args)}')
        return qb.Relationship.__call__(self, *args)

    @property
    def metadata(self):
        return self._metadata

    def decimal_scale(self):
        return self._metadata.numeric_scale

    def decimal_size(self):
        precision = self._metadata.numeric_precision
        if precision is not None:
            if 1 <= precision <= 18:
                return 64
            elif 18 < precision <= 38:
                return 128
            raise ValueError(f'Precision {precision} is not supported (max: 38)')
        return precision

    def __repr__(self):
        return f"Snowflake:{super().__repr__()}"


class SnowflakeTable(AbstractBindableTable[BindableSnowflakeColumn]):

    def __init__(self, fqn: str, model):
        self._metadata = model.api().table_metadata(fqn)
        super().__init__(fqn, model, self._metadata.foreign_keys)
        self._initialize(model)

    def _initialize(self, model):
        self._model = model
        self._cols = {col.name: BindableSnowflakeColumn(col, self, model) for col in self._metadata.columns}
        self._process_foreign_keys()
        # initialize the table so that the graph index can be updated
        self._initialize_qb_table()
        self._generate_declare()

    def _initialize_qb_table(self):
        from relationalai.early_access.builder.snowflake import Table as QBTable
        self._qb_table = QBTable(self._table)
        QBTable._used_sources.add(self._qb_table)

    def _generate_declare(self):
        src = f"declare {self.physical_name()}"
        self._model.qb_model().define(qb.RawSource('rel', src))

    def __str__(self):
        # returns the name of the table, as well as the columns and their types
        return self.physical_name() + ':\n' + '\n'.join(
            [f' {col.metadata.name} {col.metadata.datatype}' for _, col in self._cols.items()]
        ) + '\n' + '\n'.join(
            [f' {fk.source_columns} -> {fk.target_columns}' for fk in self._foreign_keys]
        )

    def physical_name(self):
        # physical relation name is always in the form of `{database}_{schema}_{table}
        return f"{self._table.lower()}".replace('.', '_')
