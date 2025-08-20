from __future__ import annotations
import atexit
from collections import defaultdict
import json
import re
import textwrap
import uuid

from pandas import DataFrame
from typing import Any, Optional
import relationalai as rai

from relationalai import debugging
from relationalai.clients import result_helpers
from relationalai.clients.util import IdentityParser
from relationalai.clients.snowflake import APP_NAME
from relationalai.early_access.metamodel import ir, executor as e, factory as f
from relationalai.early_access.rel import Compiler
from relationalai.clients.config import Config
from relationalai.tools.constants import USE_DIRECT_ACCESS, Generation


class RelExecutor(e.Executor):
    """Executes Rel code using the RAI client."""

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

    def _export(self, raw_code: str, dest_fqn: str, actual_cols: list[str], declared_cols: list[str], update:bool):
        _exec = self.resources._exec
        output_table = "out" + str(uuid.uuid4()).replace("-", "_")
        txn_id = None
        artifacts = None
        dest_database, dest_schema, dest_table, _ = IdentityParser(dest_fqn, require_all_parts=True).to_list()
        assert self.resources._session
        with debugging.span("transaction"):
            try:
                with debugging.span("exec_format") as span:
                    res = _exec(f"call {APP_NAME}.api.exec_into_table(?, ?, ?, ?, ?, ?);", [self.database, self.engine, raw_code, output_table, False, True])
                    txn_id = json.loads(res[0]["EXEC_INTO_TABLE"])["rai_transaction_id"]
                    span["txn_id"] = txn_id

                with debugging.span("write_table", txn_id=txn_id):
                    out_sample = _exec(f"select * from {APP_NAME}.results.{output_table} limit 1;")
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
                                                FROM {APP_NAME}.results.{output_table};
                                            END;
                                        ';
                                    ELSE
                                        -- Create table based on the SELECT
                                        EXECUTE IMMEDIATE '
                                            CREATE TABLE {dest_fqn} AS
                                            SELECT {names}
                                            FROM {APP_NAME}.results.{output_table};
                                        ';
                                    END IF;
                                    CALL {APP_NAME}.api.drop_result_table('{output_table}');
                                END;
                            """)
                        else:
                            _exec(f"""
                                begin
                                    INSERT INTO {dest_fqn} SELECT {names} FROM {APP_NAME}.results.{output_table};
                                    call {APP_NAME}.api.drop_result_table('{output_table}');
                                end;
                            """)
            except Exception as e:
                msg = str(e).lower()
                if "no columns returned" in msg or "columns of results could not be determined" in msg:
                    pass
                else:
                    raise e
            if txn_id:
                artifact_info = self.resources._list_exec_async_artifacts(txn_id)
                with debugging.span("fetch"):
                    artifacts = self.resources._download_results(artifact_info, txn_id, "ABORTED")
            return artifacts

    def execute(self, model: ir.Model, task:ir.Task, result_cols:list[str]|None=None, export_to:Optional[str]=None, update:bool=False) -> DataFrame:
        self.check_graph_index()
        resources= self.resources

        rules_code = ""
        if self._last_model != model:
            with debugging.span("compile", metamodel=model) as install_span:
                base = textwrap.dedent("""
                    declare pyrel_error_attrs(err in ::std::common::UInt128, attr in ::std::common::String, v) requires true

                """)
                rules_code = base + self.compiler.compile(model, {"wide_outputs": self.wide_outputs})
                install_span["compile_type"] = "model"
                install_span["rel"] = rules_code
                rules_code = resources.create_models_code([("pyrel_qb_0", rules_code)])
                self._last_model = model


        with debugging.span("compile", metamodel=task) as compile_span:
            base = textwrap.dedent("""
                def output(:pyrel_error, err, attr, val):
                    pyrel_error_attrs(err, attr, val)

            """)
            task_model = f.compute_model(f.logical([task]))
            task_code, task_model = self.compiler.compile_inner(task_model, {"no_declares": True, "wide_outputs": self.wide_outputs})
            task_code = base + task_code
            compile_span["compile_type"] = "query"
            compile_span["rel"] = task_code

        full_code = textwrap.dedent(f"""
            {rules_code}
            {task_code}
        """)

        if self.dry_run:
            return DataFrame()

        cols, extra_cols = self._compute_cols(task, task_model)

        if not export_to:
            raw_results = resources.exec_raw(self.database, self.engine, full_code, False, nowait_durable=True)
            df, errs = result_helpers.format_results(raw_results, None, cols, generation=Generation.QB)  # Pass None for task parameter
            self.report_errors(errs)
            return self._postprocess_df(self.config, df, extra_cols)
        else:
            assert cols
            # The result cols should be a superset of the actual cols.
            if result_cols is not None:
                assert all(col in result_cols or col in extra_cols for col in cols)
            else:
                result_cols = [col for col in cols if col not in extra_cols]
            assert result_cols
            raw = self._export(full_code, export_to, cols, result_cols, update)
            errors = []
            if raw:
                dataframe, errors = result_helpers.format_results(raw, None, result_cols, generation=Generation.QB)
                self.report_errors(errors)
            return DataFrame()

    # NOTE(coey): this is added temporarily to support executing Rel for the solvers library in EA.
    # It can be removed once this is no longer needed by the solvers library.
    def execute_raw(self, raw_rel:str, readonly:bool=True) -> DataFrame:
        raw_results = self.resources.exec_raw(self.database, self.engine, raw_rel, readonly, nowait_durable=True)
        df, errs = result_helpers.format_results(raw_results, None, generation=Generation.QB)  # Pass None for task parameter
        self.report_errors(errs)
        return df
