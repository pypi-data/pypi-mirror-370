import relationalai as rai
from typing import cast, Literal


def get_active_event_table() -> str:
    provider = cast(rai.clients.snowflake.Provider, rai.Provider())
    return cast(
        str, provider.sql("show parameters like 'event_table' in account;")[0]["value"]
    )


def get_events(
    seconds_ago=None,
    start=None,
    end=None,
    event_table=None,
    format: Literal["list", "pandas", "polars", "lazy"] = "pandas",
):
    provider = cast(rai.clients.snowflake.Provider, rai.Provider())
    if event_table is None:
        event_table = get_active_event_table()
    where_clauses = []
    if seconds_ago is not None:
        where_clauses.append(
            f"timestamp > current_timestamp() - interval '{seconds_ago} seconds'"
        )
    else:
        if start is not None:
            where_clauses.append(f"timestamp > '{start}'")
        if end is not None:
            where_clauses.append(f"timestamp < '{end}'")
    if where_clauses:
        where_clause = " where " + " and ".join(where_clauses)
    else:
        where_clause = ""
    return provider.sql(f"select * from {event_table}{where_clause}", format=format)
