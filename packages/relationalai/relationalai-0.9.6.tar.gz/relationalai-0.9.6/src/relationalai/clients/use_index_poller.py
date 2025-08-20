from typing import Iterable, Dict, Optional, List, cast, TYPE_CHECKING
import json
import uuid

from relationalai import debugging
from relationalai.clients.cache_store import GraphIndexCache
from relationalai.clients.util import get_pyrel_version, poll_with_specified_overhead
from relationalai.errors import (
    ERPNotRunningError,
    EngineAutoCreateFailed,
    SnowflakeChangeTrackingNotEnabledException,
    SnowflakeTableObjectsException,
    SnowflakeTableObject,
)
from relationalai.tools.cli_controls import SpanSpinner, Spinner
from relationalai.tools.constants import WAIT_FOR_STREAM_SYNC, Generation

if TYPE_CHECKING:
    from relationalai.clients.snowflake import Resources
    from relationalai.clients.snowflake import DirectAccessResources


class UseIndexPoller:
    """
    Encapsulates the polling logic for `use_index` streams.
    """
    def __init__(
        self,
        resource: "Resources",
        app_name: str,
        sources: Iterable[str],
        model: str,
        engine_name: str,
        engine_size: Optional[str],
        program_span_id: Optional[str],
        headers: Optional[Dict],
        generation: Optional[Generation] = None,
    ):
        self.res = resource
        self.app_name = app_name
        self.sources = list(sources)
        self.model = model
        self.engine_name = engine_name
        self.engine_size = engine_size or self.res.config.get_default_engine_size()
        self.program_span_id = program_span_id
        self.headers = headers or {}
        self.counter = 1
        self.check_ready_count = 0
        self.tables_with_not_enabled_change_tracking: List = []
        self.table_objects_with_other_errors: List = []
        self.engine_errors: List = []
        # Flag to only ensure the engine is created asynchronously the initial call
        self.init_engine_async = True
        # Initially, we assume that cdc is not checked,
        # then on subsequent calls, if we get if cdc is enabled, if it is not, we will check it
        # on every 5th iteration we reset the cdc status, so it will be checked again
        self.should_check_cdc = True

        self.wait_for_stream_sync = self.res.config.get(
            "wait_for_stream_sync", WAIT_FOR_STREAM_SYNC
        )
        current_user = self.res.get_sf_session().get_current_user()
        assert current_user is not None, "current_user must be set"
        data_freshness = self.res.config.get_data_freshness_mins()
        self.cache = GraphIndexCache(current_user, model, data_freshness, self.sources)
        self.sources = self.cache.choose_sources()
        # execution_id is allowed to group use_index call, which belongs to the same loop iteration
        self.execution_id = str(uuid.uuid4())

        self.pyrel_version = get_pyrel_version(generation)

        self.source_info = self.res._check_source_updates(self.sources)

    def poll(self) -> None:
        """
        Standard stream-based polling for use_index.
        """
        self._maybe_delete_stale()
        with Spinner(
            "Preparing your data...",
            "Data preparation complete",
            leading_newline=True,
            trailing_newline=True,
        ) as spinner:
            self._poll_loop(spinner)
        self._post_check(spinner)

    def _maybe_delete_stale(self) -> None:
        with debugging.span("check_sources"):
            # Source tables that have been altered/changed since the last stream creation
            stale_sources = [
                source
                for source, info in self.source_info.items()
                if info["state"] == "STALE"
            ]
        if stale_sources:
            with SpanSpinner("validate_sources", "Validating data sources...", "Data sources validated", leading_newline=True):
                try:
                    # Delete all stale streams, so use_index could recreate them again
                    from relationalai.clients.snowflake import PYREL_ROOT_DB
                    query = f"CALL {self.app_name}.api.delete_data_streams({stale_sources}, '{PYREL_ROOT_DB}');"
                    delete_response = self.res._exec(query)
                    delete_json_str = delete_response[0]["DELETE_DATA_STREAMS"].lower()
                    delete_data = json.loads(delete_json_str)
                    diff = len(stale_sources) - delete_data.get("deleted", 0)
                    if diff > 0:
                        errors = delete_data.get("errors", None)
                        if errors:
                            raise Exception(f"Error(s) deleting streams with modified sources: {errors}")
                except Exception as e:
                    # The delete_data_streams procedure will raise an exception if the streams do not exist
                    if "data streams do not exist" in str(e).lower():
                        pass
                    else:
                        raise e from None

    def _poll_loop(self, spinner) -> None:
        source_references = self.res._get_source_references(self.source_info)
        sources_object_references_str = ", ".join(source_references)

        def check_ready(spinner) -> bool:
            self.check_ready_count += 1

            # To limit the performance overhead, we only check if ERP is running every 5 iterations
            if self.check_ready_count % 5 == 0:
                with debugging.span("check_erp_status"):
                    if not self.res.is_erp_running(self.app_name):
                        raise ERPNotRunningError

            use_index_id = f"{self.model}_{self.execution_id}"

            params = json.dumps({
                "model": self.model,
                "engine": self.engine_name,
                "default_engine_size": self.engine_size, # engine_size
                "user_agent": self.pyrel_version,
                "use_index_id": use_index_id,
                "pyrel_program_id": self.program_span_id,
                "wait_for_stream_sync": self.wait_for_stream_sync,
                "should_check_cdc": self.should_check_cdc,
                "init_engine_async": self.init_engine_async,
            })
            sql_string = f"CALL {self.app_name}.api.use_index([{sources_object_references_str}], PARSE_JSON(?), {self.headers});"

            with debugging.span("wait", counter=self.counter, use_index_id=use_index_id) as span:
                results = self.res._exec(sql_string, [params])

                # Extract the JSON string from the `USE_INDEX` field
                use_index_json_str = results[0]["USE_INDEX"]

                # Parse the JSON string into a Python dictionary
                use_index_data = json.loads(use_index_json_str)
                span.update(use_index_data)

                all_data = use_index_data.get("data", [])
                ready = use_index_data.get("ready", False)
                engines = use_index_data.get("engines", [])
                errors = use_index_data.get("errors", [])
                cdc_enabled = use_index_data.get("cdcEnabled", False)
                if self.check_ready_count % 5 == 0 or not cdc_enabled:
                    self.should_check_cdc = True
                else:
                    self.should_check_cdc = False

                break_loop = False

                if ready:
                    self.cache.record_update(self.source_info)
                    break_loop = True
                    spinner.update_messages({ "finished_message": "Setup complete" })

                if not ready and all_data:
                    for data in all_data:
                        status = data.get("status", "").lower()
                        if data.get("errors", []):
                            for error in data.get("errors", []):
                                error_msg = f"{error.get('error')}, source: {error.get('source')}"
                                self.table_objects_with_other_errors.append(
                                    SnowflakeTableObject(error_msg, data.get("fq_object_name"))
                                )
                            break_loop = True

                        if status == "created":
                            spinner.update_messages({ "message": f"Preparing {data.get('fq_object_name')}..." })
                        if (status != "synced" or data.get("pending_batches_count") > 0):
                            batches_count = data.get("pending_batches_count")
                            if batches_count:
                                spinner.update_messages({ "message": f"Preparing {data.get('fq_object_name')}, remaining batches: {data.get('pending_batches_count')}..." })
                            else:
                                spinner.update_messages({ "message": f"Preparing {data.get('fq_object_name')}..." })
                    self.counter += 1

                if not ready and engines:
                    for engine in engines:
                        name = engine.get("name", "")
                        state = engine.get("state", "").lower()
                        status = engine.get("status", "").lower()
                        if (state == "pending" or status == "pending"):
                            writer = engine.get("writer", False)
                            message = f"Waiting for {writer and 'writer engine' or 'engine'} {name}..."
                            spinner.update_messages({ "message": message })
                    self.counter += 1

                if not ready and errors:
                    for error in errors:
                        if error.get("type") == "data":
                            message = error.get("message", "").lower()
                            if ("change_tracking" in message or "change tracking" in message):
                                err_source = error.get("source")
                                err_source_type = self.source_info.get(err_source, {}).get("type")
                                self.tables_with_not_enabled_change_tracking.append((err_source, err_source_type))
                            else:
                                self.table_objects_with_other_errors.append(
                                    SnowflakeTableObject(error.get("message"), error.get("source"))
                                )
                        elif error.get("type") == "engine":
                            self.engine_errors.append(error)
                        else:
                            # Other types of errors, e.g. "validation"
                            self.table_objects_with_other_errors.append(
                                SnowflakeTableObject(error.get("message"), error.get("source"))
                            )
                    break_loop = True
                return break_loop

        poll_with_specified_overhead(lambda: check_ready(spinner), overhead_rate=0.1, max_delay=1)

    def _post_check(self, spinner) -> None:
            num_tables_altered = 0

            enabled_tables = []
            if (
                self.tables_with_not_enabled_change_tracking
                and self.res.config.get("ensure_change_tracking", False)
            ):
                for table in self.tables_with_not_enabled_change_tracking:
                    try:
                        fqn, kind = table
                        self.res._exec(f"ALTER {kind} {fqn} SET CHANGE_TRACKING = TRUE;")
                        enabled_tables.append(table)
                        num_tables_altered += 1
                    except Exception:
                        pass
                # Remove the tables that were successfully enabled from the list of not enabled tables
                # so that we don't raise an exception for them later
                self.tables_with_not_enabled_change_tracking = [
                    t for t in self.tables_with_not_enabled_change_tracking if t not in enabled_tables
                ]

            if self.tables_with_not_enabled_change_tracking:
                spinner.update_messages({ "message": "Errors found. See below for details." })
                raise SnowflakeChangeTrackingNotEnabledException(
                    self.tables_with_not_enabled_change_tracking
                )

            if self.table_objects_with_other_errors:
                spinner.update_messages({ "message": "Errors found. See below for details." })
                raise SnowflakeTableObjectsException(self.table_objects_with_other_errors)
            if self.engine_errors:
                spinner.update_messages({ "message": "Errors found. See below for details." })
                # if there is an engine error, probably auto create engine failed
                raise EngineAutoCreateFailed(self.engine_name)

            if num_tables_altered > 0:
                s = "s" if num_tables_altered > 1 else ""
                spinner.update_messages({ "message": f"Enabled change tracking on {num_tables_altered} table{s}. Still preparing your data..." })
                self._poll_loop(spinner)

class DirectUseIndexPoller(UseIndexPoller):
    """
    Extends UseIndexPoller to handle direct-access prepare_index when no sources.
    """
    def __init__(
        self,
        resource: "DirectAccessResources",
        app_name: str,
        sources: Iterable[str],
        model: str,
        engine_name: str,
        engine_size: Optional[str],
        program_span_id: Optional[str],
        headers: Optional[Dict],
        generation: Optional[Generation] = None,
    ):
        super().__init__(resource, app_name, sources, model, engine_name, engine_size, program_span_id, headers, generation)
        from relationalai.clients.snowflake import DirectAccessResources
        self.res: DirectAccessResources = cast(DirectAccessResources, self.res)

    def poll(self) -> None:
        if not self.sources:
            from relationalai.errors import RAIException
            collected_errors: List[Dict] = []
            attempt = 1

            def check_direct(spinner) -> bool:
                nonlocal attempt
                with debugging.span("wait", counter=self.counter) as span:
                    span.update({"attempt": attempt, "engine_name": self.engine_name, "model": self.model})
                    # we are skipping pulling relations here, as direct access only handle non-sources cases
                    # and we don't need to pull relations for that, therefore, we pass empty list for rai_relations
                    # and set skip_pull_relations to True
                    resp = self.res._prepare_index(
                        model=self.model,
                        engine_name=self.engine_name,
                        engine_size=self.engine_size,
                        rai_relations=[],
                        pyrel_program_id=self.program_span_id,
                        skip_pull_relations=True,
                        headers=self.headers,
                    )
                    span.update(resp)
                    caller_engine = resp.get("caller_engine", {})
                    ce_status = caller_engine.get("status", "").lower()
                    errors = resp.get("errors", [])

                    ready = resp.get("ready", False)

                    if ready:
                        spinner.update_messages({"finished_message": "Setup complete"})
                        return True
                    else:
                        if ce_status == "pending":
                            message = f"Waiting for engine '{caller_engine.get('name', self.engine_name)}' to be ready..."
                            spinner.update_messages({"message": message})
                        else:
                            for err in errors:
                                collected_errors.append(err)

                    attempt += 1
                    return False

            with Spinner(
                "Preparing your data...",
                "Setup complete",
                leading_newline=True,
                trailing_newline=True,
            ) as spinner:
                with debugging.span("poll_direct"):
                    poll_with_specified_overhead(lambda: check_direct(spinner), overhead_rate=0.1, max_delay=1)

            if collected_errors:
                spinner.update_messages({"message": "Errors found. See below for details."})
                msg = "; ".join(e.get("message", "") for e in collected_errors)
                raise RAIException(msg)
        else:
            super().poll()
