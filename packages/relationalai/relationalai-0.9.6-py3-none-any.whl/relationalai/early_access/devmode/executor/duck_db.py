from __future__ import annotations

import duckdb
from pandas import DataFrame
from typing import Any, Union

from relationalai.early_access.devmode import Compiler
from relationalai.early_access.devmode.executor.result_helpers import format_duckdb_columns
from relationalai.early_access.metamodel import ir, executor as e

class DuckDBExecutor(e.Executor):

    def __init__(self, skip_denormalization: bool = False) -> None:
        super().__init__()
        self.compiler = Compiler(skip_denormalization)

    def execute(self, model: ir.Model, task: ir.Task) -> Union[DataFrame, Any]:
        """ Execute the SQL query directly. """
        connection = duckdb.connect()
        try:
            sql = self.compiler.compile(model, {"is_duck_db": True})
            arrow_table = connection.query(sql).fetch_arrow_table()
            return format_duckdb_columns(arrow_table.to_pandas(), arrow_table.schema)
        finally:
            connection.close()