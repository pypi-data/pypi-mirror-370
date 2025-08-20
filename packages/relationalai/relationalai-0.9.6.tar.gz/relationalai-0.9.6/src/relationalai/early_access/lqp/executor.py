from __future__ import annotations
from collections import defaultdict
import atexit
import re

from pandas import DataFrame
from typing import Any, Optional
import relationalai as rai

from relationalai import debugging
from relationalai.early_access.lqp import result_helpers
from relationalai.early_access.metamodel import ir, factory as f, executor as e
from relationalai.early_access.lqp.compiler import Compiler
from relationalai.early_access.lqp.types import lqp_type_to_sql
from lqp import print as lqp_print, ir as lqp_ir
from relationalai.early_access.lqp.ir import convert_transaction, validate_lqp
from relationalai.clients.config import Config
from relationalai.clients.snowflake import APP_NAME
from relationalai.clients.types import TransactionAsyncResponse
from relationalai.clients.util import IdentityParser
from relationalai.tools.constants import USE_DIRECT_ACCESS


class LQPExecutor(e.Executor):
    """Executes LQP using the RAI client."""

    def __init__(
        self,
        database: str,
        dry_run: bool = False,
        keep_model: bool = True,
        wide_outputs: bool = False,
        config: Config | None = None,
    ) -> None:
        super().__init__()
        self.database = database
        self.dry_run = dry_run
        self.keep_model = keep_model
        self.wide_outputs = wide_outputs
        self.compiler = Compiler()
        self.config = config or Config()
        self._resources = None
        self._last_model = None
        self._error_ids = []
        self._last_sources_version = (-1, None)

    @property
    def resources(self):
        if not self._resources:
            with debugging.span("create_session"):
                self.dry_run |= bool(self.config.get("compiler.dry_run", False))
                resource_class = rai.clients.snowflake.Resources
                if self.config.get("use_direct_access", USE_DIRECT_ACCESS):
                    resource_class = rai.clients.snowflake.DirectAccessResources
                self._resources = resource_class(dry_run=self.dry_run, config=self.config, generation=rai.Generation.QB)
                if not self.dry_run:
                    self.engine = self._resources.get_default_engine_name()
                    if not self.keep_model:
                        atexit.register(self._resources.delete_graph, self.database, True)
        return self._resources

    def check_graph_index(self):
        # Has to happen first, so self.dry_run is populated.
        resources = self.resources

        if self.dry_run:
            return

        from relationalai.early_access.builder.snowflake import Table
        table_sources = Table._used_sources
        if not table_sources.has_changed(self._last_sources_version):
            return

        model = self.database
        app_name = resources.get_app_name()
        engine_name = self.engine
        engine_size = self.resources.config.get_default_engine_size()

        program_span_id = debugging.get_program_span_id()
        sources = [t._fqn for t in Table._used_sources]
        self._last_sources_version = Table._used_sources.version()

        assert self.engine is not None

        with debugging.span("poll_use_index", sources=sources, model=model, engine=engine_name):
            resources.poll_use_index(app_name, sources, model, self.engine, engine_size, program_span_id)

    def report_errors(self, problems: list[dict[str, Any]], abort_on_error=True):
        from relationalai import errors
        all_errors = []
        undefineds = []
        pyrel_errors = defaultdict(list)
        pyrel_warnings = defaultdict(list)

        for problem in problems:
            message = problem.get("message", "")
            report = problem.get("report", "")
            # TODO: we need to build source maps
            # path = problem.get("path", "")
            # source_task = self._install_batch.line_to_task(path, problem["start_line"]) or task
            # source = debugging.get_source(source_task) or debugging.SourceInfo()
            source = debugging.SourceInfo()
            severity = problem.get("severity", "warning")
            code = problem.get("code")

            if severity in ["error", "exception"]:
                if code == "UNDEFINED_IDENTIFIER":
                    match = re.search(r'`(.+?)` is undefined', message)
                    if match:
                        undefineds.append((match.group(1), source))
                    else:
                        all_errors.append(errors.RelQueryError(problem, source))
                elif "overflowed" in report:
                    all_errors.append(errors.NumericOverflow(problem, source))
                elif code == "PYREL_ERROR":
                    pyrel_errors[problem["props"]["pyrel_id"]].append(problem)
                elif abort_on_error:
                    all_errors.append(errors.RelQueryError(problem, source))
            else:
                if code == "ARITY_MISMATCH":
                    errors.ArityMismatch(problem, source)
                elif code == "IC_VIOLATION":
                    all_errors.append(errors.IntegrityConstraintViolation(problem, source))
                elif code == "PYREL_ERROR":
                    pyrel_warnings[problem["props"]["pyrel_id"]].append(problem)
                else:
                    errors.RelQueryWarning(problem, source)

        if abort_on_error and len(undefineds):
            all_errors.append(errors.UninitializedPropertyException(undefineds))

        if abort_on_error:
            for pyrel_id, pyrel_problems in pyrel_errors.items():
                all_errors.append(errors.ModelError(pyrel_problems))

        for pyrel_id, pyrel_problems in pyrel_warnings.items():
            errors.ModelWarning(pyrel_problems)


        if len(all_errors) == 1:
            raise all_errors[0]
        elif len(all_errors) > 1:
            raise errors.RAIExceptionSet(all_errors)

    def _export(self, txn_id: str, export_info: tuple, dest_fqn: str, actual_cols: list[str], declared_cols: list[str], update:bool):
        # At this point of the export, we assume that a CSV file has already been written
        # to the Snowflake Native App stage area. Thus, the purpose of this method is to
        # copy the data from the CSV file to the destination table.
        _exec = self.resources._exec
        dest_database, dest_schema, dest_table, _ = IdentityParser(dest_fqn, require_all_parts=True).to_list()
        filename = export_info[0]
        result_table_name = filename + "_table"

        with debugging.span("export", txn_id=txn_id, export_info=export_info, dest_table=dest_table):
            with debugging.span("export_to_result_schema"):
                # First, we need to persist from the CSV file to the results schema by calling the
                # `persist_from_stage` stored procedure. This step also cleans up the CSV file in
                # the stage area.
                column_fields = []
                for (col_name, col_type) in export_info[1]:
                    column_fields.append([col_name, lqp_type_to_sql(col_type)])

                # NOTE: the `str(column_fields)` depends on python formatting which surrounds
                # strings with single quotes. If this changes, or if we ever get a single quote in
                # the actual string, then we need to do something more sophisticated.
                exec_str = f"call {APP_NAME}.api.persist_from_stage('{txn_id}', '{filename}', '{result_table_name}', {str(column_fields)})"
                _exec(exec_str)

            with debugging.span("write_table"):
                # The result of the first step above is a table in the results schema,
                # {app_name}.results.{result_table_name}.
                # Second, we need to copy the data from the results schema to the
                # destination table. This step also cleans up the result table.
                out_sample = _exec(f"select * from {APP_NAME}.results.{result_table_name} limit 1;")
                if out_sample:
                    keys = set([k.lower() for k in out_sample[0].as_dict().keys()])
                    fields = []
                    ix = 0
                    for name in declared_cols:
                        if name in actual_cols:
                            field = f"col{ix:03} as \"{name}\"" if f"col{ix:03}" in keys else f"NULL as {name}"
                            ix += 1
                        else:
                            field = f"NULL as \"{name}\""
                        fields.append(field)
                    names = ", ".join(fields)
                    if not update:
                        _exec(f"""
                            BEGIN
                                -- Check if table exists
                                IF (EXISTS (
                                    SELECT 1
                                    FROM {dest_database}.INFORMATION_SCHEMA.TABLES
                                    WHERE table_schema = '{dest_schema}'
                                    AND table_name = '{dest_table}'
                                )) THEN
                                    -- Insert into existing table
                                    EXECUTE IMMEDIATE '
                                        BEGIN
                                            TRUNCATE TABLE {dest_fqn};
                                            INSERT INTO {dest_fqn}
                                            SELECT {names}
                                            FROM {APP_NAME}.results.{result_table_name};
                                        END;
                                    ';
                                ELSE
                                    -- Create table based on the SELECT
                                    EXECUTE IMMEDIATE '
                                        CREATE TABLE {dest_fqn} AS
                                        SELECT {names}
                                        FROM {APP_NAME}.results.{result_table_name};
                                    ';
                                END IF;
                                CALL {APP_NAME}.api.drop_result_table('{result_table_name}');
                            END;
                        """)
                    else:
                        _exec(f"""
                            begin
                                INSERT INTO {dest_fqn} SELECT {names} FROM {APP_NAME}.results.{result_table_name};
                                call {APP_NAME}.api.drop_result_table('{result_table_name}');
                            end;
                        """)

            return None

    def execute(self, model: ir.Model, task:ir.Task, result_cols:Optional[list[str]]=None, export_to:Optional[str]=None, update:bool=False) -> DataFrame:
        self.check_graph_index()

        model_txn = None
        if self._last_model != model:
            with debugging.span("compile", metamodel=model) as install_span:
                _, error_ids, model_txn = self.compiler.compile(model, {"fragment_id": b"model"})
                install_span["compile_type"] = "model"
                install_span["lqp"] = lqp_print.to_string(model_txn)
                install_span["lqp_debug"] = lqp_print.to_string(model_txn, {"print_names": True, "print_debug": False})
                self._last_model = model
                self._error_ids = error_ids

        with debugging.span("compile", metamodel=task) as compile_span:
            query = f.compute_model(f.logical([task]))
            options = {
                "wide_outputs": self.wide_outputs,
                "fragment_id": b"query",
                "error_attr_ids": self._error_ids,
            }
            result, final_model = self.compiler.compile_inner(query, options)
            export_info, _, query_txn = result
            compile_span["compile_type"] = "query"
            compile_span["lqp"] = lqp_print.to_string(query_txn)
            compile_span["lqp_debug"] = lqp_print.to_string(query_txn, {"print_names": True, "print_debug": False})

        txn = query_txn
        if model_txn is not None:
            # Merge the two LQP transactions into one. Long term the query bits should all
            # go into a WhatIf action. But for now we just use two separate epochs.
            model_epoch = model_txn.epochs[0]
            query_epoch = query_txn.epochs[0]
            txn = lqp_ir.Transaction(epochs=[model_epoch, query_epoch], meta=None)

            # Revalidate now that we've joined two epochs
            validate_lqp(txn)

        txn_proto = convert_transaction(txn)

        if self.dry_run:
            return DataFrame()

        raw_results = self.resources.exec_lqp(
            self.database,
            self.engine,
            txn_proto.SerializeToString(),
            # Current strategy is to run all queries as write transactions, in order to
            # benefit from view caching. This will have to be revisited, because write
            # transactions are serialized.
            readonly=False,
            nowait_durable=True,
        )

        cols, extra_cols = self._compute_cols(task, final_model)

        df, errs = result_helpers.format_results(raw_results, cols)
        self.report_errors(errs)

        # Process exports
        if export_to and not self.dry_run:
            assert cols, "No columns found in the output"
            assert isinstance(raw_results, TransactionAsyncResponse) and raw_results.transaction, "Invalid transaction result"

            if result_cols is not None:
                assert all(col in result_cols or col in extra_cols for col in cols)
            else:
                result_cols = cols
            assert result_cols

            assert export_info, "Export info should be populated if we are exporting results"
            self._export(raw_results.transaction['id'], export_info, export_to, cols, result_cols, update)

        return self._postprocess_df(self.config, df, extra_cols)
