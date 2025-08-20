
import relationalai as rai
import string
import random
import textwrap

def rel(model, rel_code):
    resources = rai.clients.snowflake.Resources()
    resources.config.set("use_graph_index", False)
    database = model
    try:
        resources.create_graph(database)
    except Exception as e:
        if "already exists" not in str(e).lower():
            raise e
    engine = resources.config.get("engine")
    return resources.exec_raw(database, engine, rel_code)

def random_string():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(32))

def run_sql(session, query, params=None):
    return session.sql(query, params).collect()

def get_models(session, database, engine):
    APP_NAME = "relationalai"
    tmp_name = f"tmp_{random_string()}"
    query = textwrap.dedent(f"""
        call {APP_NAME}.api.exec_into(
            '{database}',
            '{engine}',
            'def pairs(name, model): rel(:catalog, :model, name, model) and not starts_with(name, "rel/") and not starts_with(name, "pkg/std")
             def Export_Relation(:key, i, key): exists( (value) | sort(pairs, i, key, value) )
             def Export_Relation(:value, i, value): exists( (key) | sort(pairs, i, key, value) )',
            '{tmp_name}',
            true
        );
    """)
    try:
        run_sql(session, query)
    except Exception as e:
        raise e
        return
    result = run_sql(session, f"select key, value from relationalai.results.{tmp_name};")
    run_sql(session, f"call {APP_NAME}.api.drop_result_table('{tmp_name}');")
    for row in result:
        if row["KEY"] == "catalog":
            continue
        yield row["KEY"], row["VALUE"]