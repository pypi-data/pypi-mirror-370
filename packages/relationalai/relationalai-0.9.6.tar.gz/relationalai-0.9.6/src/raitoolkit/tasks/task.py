from dataclasses import dataclass
import textwrap
import time
from typing import Optional, cast
import relationalai as rai
from snowflake.snowpark import Row

from relationalai.clients.snowflake import Provider


@dataclass
class Task:
    name: str
    database: str
    schema: str
    procedure: str
    provider: Provider = cast(rai.clients.snowflake.Provider, rai.Provider())
    last_execution_time: Optional[str] = None
    logs_table: Optional[str] = None

    def create(
        self,
        args=[],
        warehouse="MAIN_WH",
        schedule_every_min=False,
        use_wrapper_sproc=False,
        wrapper_sproc_name=None,
        task_result_table_name=None,
    ):
        arg_string = ", ".join(
            f"'{arg}'" if isinstance(arg, str) else str(arg) for arg in args
        )
        if schedule_every_min:
            sql_query = textwrap.dedent(f"""
            CREATE OR REPLACE TASK {self.database}.{self.schema}.{self.name}
            WAREHOUSE = {warehouse}
            SCHEDULE = 'USING CRON * * * * * UTC'
            AS
            CALL {self.database}.{self.schema}.{self.procedure}({arg_string});
            """)
        else:
            sql_query = textwrap.dedent(f"""
            CREATE OR REPLACE TASK {self.database}.{self.schema}.{self.name}
            WAREHOUSE = {warehouse}
            AS
            CALL {self.database}.{self.schema}.{self.procedure}({arg_string});
            """)
        return self.provider.sql(sql_query)

    def exec_sync(self, log=print):
        log("Task created.")
        self.last_execution_time = self.get_current_timestamp()
        log("Executing task...")
        self.execute()
        log("Polling task...")
        return self.poll(self.last_execution_time, log=log)

    def execute(self):
        self.last_execution_time = self.get_current_timestamp()
        sql_query = f"EXECUTE TASK {self.database}.{self.schema}.{self.name};"
        return self.provider.sql(sql_query)

    def delete(self):
        sql_query = f"""
        DROP TASK {self.database}.{self.schema}.{self.name};
        """
        try:
            return self.provider.sql(sql_query)
        except Exception as e:
            if "does not exist" in str(e).lower():
                return None
            raise e

    def get_current_timestamp(self) -> str:
        sql_query = "SELECT CURRENT_TIMESTAMP() AS ts;"
        response = self.provider.sql(sql_query)
        return cast(str, response[0]["TS"])

    def check(self, scheduled_after=None):
        if scheduled_after is None:
            scheduled_after = self.last_execution_time
        sql_query = f"""
        SELECT *
        FROM TABLE({self.database}.INFORMATION_SCHEMA.TASK_HISTORY(
            SCHEDULED_TIME_RANGE_START => CAST(DATEADD('second', -1, TIMESTAMP '{scheduled_after}') AS TIMESTAMP_LTZ),
            TASK_NAME => '{self.name}'
        ));
        """
        return self.provider.sql(sql_query)

    def poll(self, scheduled_after=None, timeout=300, interval=5, log=print):
        if scheduled_after is None:
            scheduled_after = self.last_execution_time
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = cast(list, self.check(scheduled_after))
            if response:
                log("Task scheduled...")
                latest = response[-1]
                if latest["COMPLETED_TIME"]:
                    log("Task completed")
                    return latest.as_dict()
            else:
                log("Task not found in history yet...")
            time.sleep(interval)
        log("Timeout reached. Task not found in history.")
        return None

    def get_server_logs(
        self, filename: str, table_name: Optional[str] = None, all=False, log=print
    ):
        "Save logs from Snowflake to a local SQLite database."
        if table_name is None:
            table_name = self.logs_table or "logs"
        if not self.logs_table:
            raise ValueError("Logs table not provided.")

        # if your table doesn't have a `timestamp` column, specify `all` as True
        where_clause = (
            f"where timestamp > '{self.last_execution_time}'"
            if not all or self.last_execution_time is None
            else ""
        )
        sql_query = f"select * from {self.database}.{self.schema}.{self.logs_table} {where_clause};"
        logs = [row.as_dict() for row in cast(list, self.provider.sql(sql_query))]
        log(f"{len(logs)} logs retrieved")
        if not logs:
            return
        from sqlite_utils import Database
        from sqlite_utils.db import Table

        db = Database(filename)
        cast(Table, db[table_name]).insert_all(logs)
        db.close()
        log(f"Logs saved from {table_name} in Snowflake to {filename} locally.")
        
    def wait_for_task_executions(
        self,
        min_executions,
        timeout=20 * 60,
        poll_interval=30,
        log=print,
    ):
        start_time = time.time()
        while time.time() - start_time < timeout:
            sql_query = f"""
                SELECT STATE, ERROR_CODE, ERROR_MESSAGE, QUERY_ID, NAME, DATABASE_NAME, SCHEMA_NAME, QUERY_TEXT
                FROM TABLE({self.database}.INFORMATION_SCHEMA.TASK_HISTORY(TASK_NAME => '{self.name}'));
            """
            try:
                rows = self.provider.sql(sql_query, format="list")
            except Exception as e:
                raise Exception(f"Error querying task history: {e}")

            state_counts = {}
            failure_details = []
            for row in rows:
                row = cast(Row, row)
                state = row.STATE
                state_counts[state] = state_counts.get(state, 0) + 1

                if state in ("FAILED", "FAILED_AND_AUTO_SUSPENDED", "SKIPPED", "CANCELLED"):
                    error_code = row.ERROR_CODE or ""
                    error_message = row.ERROR_MESSAGE or ""
                    query_id = row.QUERY_ID or ""
                    name = row.NAME or ""
                    db_name = row.DATABASE_NAME or ""
                    schema_name = row.SCHEMA_NAME or ""
                    query_text = row.QUERY_TEXT or ""
                    failure_details.append(
                        f"STATE: {state} | ERROR_CODE: {error_code} | ERROR_MESSAGE: {error_message} | QUERY_ID: {query_id} | "
                        f"TASK_NAME: {name} | DATABASE: {db_name} | SCHEMA: {schema_name} | QUERY_TEXT: {query_text}"
                    )

            if failure_details:
                log("Task Execution Failed Details:")
                for detail in failure_details:
                    log(detail)
                raise Exception("Task encountered a failure state. See error details above")

            succeeded_count = state_counts.get("SUCCEEDED", 0)
            if succeeded_count >= min_executions:
                log(f"Task reached {succeeded_count} successful executions.")
                return

            if state_counts.get("SCHEDULED", 0) > 0 or state_counts.get("EXECUTING", 0) > 0:
                log("Task is still running or scheduled. Polling again...")
                time.sleep(poll_interval)
                continue

            raise Exception(f"Task is in an unexpected state: {state_counts}")

        raise Exception(
            f"Timeout reached: task did not reach {min_executions} successful executions within {timeout/60} minutes"
        )


def format_task_history(row):
    return (
        f"""error message: {row["ERROR_MESSAGE"]}"""
        if row["ERROR_MESSAGE"]
        else f"""successfully completed at: {row["COMPLETED_TIME"]}"""
    )

