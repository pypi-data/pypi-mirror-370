from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
import json
import re
import textwrap
from relationalai.clients.util import IdentityParser
from relationalai.early_access.metamodel.util import OrderedSet, ordered_set
from relationalai.early_access.rel.rel_utils import sanitize_identifier
from . import builder as b, annotations as anns
from relationalai import debugging
from snowflake.snowpark.context import get_active_session

#--------------------------------------------------
# Globals
#--------------------------------------------------

_session = None
def get_session():
    global _session
    if not _session:
        try:
            _session = get_active_session()
        except Exception:
            from relationalai import Resources
            from relationalai.clients.snowflake import Resources as SnowflakeResources
            # TODO: we need a better way to handle global config

            # using the resource constructor to differentiate between direct access and
            # regular resource as this impacts the construction of the session.
            resources = Resources()
            assert isinstance(resources, SnowflakeResources), "Can only retrieve session from Snowflake resources"
            _session = resources.get_sf_session()
    return _session

#--------------------------------------------------
# Snowflake sources
#--------------------------------------------------

SFTypes = {
    "TEXT": "String",
    "FIXED": "Number",
    "DATE": "Date",
    "TIMESTAMP": "DateTime",
    "TIMESTAMP_LTZ": "DateTime",
    "TIMESTAMP_TZ": "DateTime",
    "TIMESTAMP_NTZ": "DateTime",
    "FLOAT": "Float",
    "REAL": "Float",
    "BOOLEAN": "Bool",
}

SF_ID_REGEX = re.compile(r'^[A-Za-z_][A-Za-z0-9_$]*$')
def quoted(ident:str):
    if SF_ID_REGEX.match(ident) or ident[0] == '"':
        return ident
    return f'"{ident}"'

@dataclass
class TableInfo:
    source:Table|None
    fields:list[b.Field]
    raw_columns:list[dict]

class SchemaInfo:
    def __init__(self, database:str, schema:str) -> None:
        self.database = database
        self.schema = schema
        self.tables = defaultdict(lambda: TableInfo(None, [], []))
        self.fetched = set()

    def fetch(self):
        session = get_session()
        table_names = [name for name in self.tables.keys() if name.upper() not in self.fetched]
        self.fetched.update([x.upper() for x in table_names])
        name_lookup = {x.upper(): x for x in table_names}
        tables = ", ".join([f"'{x.upper()}', '{x}'" for x in self.tables.keys()])
        query = textwrap.dedent(f"""
            begin
                SHOW COLUMNS IN SCHEMA {quoted(self.database)}.{quoted(self.schema)};
                let r resultset := (select "table_name", "column_name", "data_type" from table(result_scan(-1)) as t
                                    where "table_name" in ({tables}));
                return table(r);
            end;
        """)
        with debugging.span("fetch_schema", sql=query):
            columns = session.sql(query).collect()
        for row in columns:
            table_name, column_name, data_type = row
            table_name = name_lookup.get(table_name, table_name)
            info = self.tables[table_name]
            sf_type_info = json.loads(data_type)
            if sf_type_info.get("type") == "FIXED":
                type_str = "Int"
                # Must follow the same mapping as the one used by CDC.
                numeric_scale = sf_type_info.get("scale", 0)
                if numeric_scale > 0:
                    if numeric_scale > 6 or sf_type_info.get("precision") > 18:
                        type_str = "Decimal128"
                    else:
                        type_str = "Decimal64"
            else:
                type_str = SFTypes[sf_type_info.get("type")]
            info.fields.append(b.Field(name=column_name, type_str=type_str))
            info.raw_columns.append(row.as_dict())

class Table():
    _schemas:dict[tuple[str, str], SchemaInfo] = {}
    _used_sources:OrderedSet[Table] = ordered_set()

    def __init__(self, fqn:str, cols:list[str]|None=None) -> None:
        self._fqn = fqn
        parser = IdentityParser(fqn, require_all_parts=True)
        self._database, self._schema, self._table, self._fqn = parser.to_list()
        self._inited = False
        self._ref = b.Integer.ref("row_id")
        self._cols = {}
        self._col_names = cols
        info = self._schemas.get((self._database, self._schema))
        if not info:
            info = self._schemas[(self._database, self._schema)] = SchemaInfo(self._database, self._schema)
        info.tables[self._table].source = self

    def _lazy_init(self):
        if self._inited:
            return
        self._inited = True
        schema_info = self._schemas[(self._database, self._schema)]
        if self._table not in schema_info.fetched:
            schema_info.fetch()
        table_info = schema_info.tables[self._table]
        self._rel = b.Relationship(self._fqn, fields=[b.Field(name="RowId", type_str="RowId")] + table_info.fields)
        self._rel.annotate(anns.external).annotate(anns.from_cdc)

    def __getattr__(self, name: str):
        if name.startswith("_"):
            return super().__getattribute__(name)
        if self._col_names is not None and name not in self._col_names:
            raise ValueError(f"Column {name} not found in {self._fqn}")
        if name.lower() not in self._cols:
            self._cols[name.lower()] = Column(self, name)
        return self._cols[name.lower()]

    def into(self, concept:b.Concept, keys:list[Column]=[]):
        self._lazy_init()
        key_dict = {sanitize_identifier(k._column_name.lower()): k for k in keys}

        # if no keys are defined but the concept has a reference scheme, try to match
        # reference schemes with column fields by name
        if not keys and concept._reference_schemes:
            sanitized_fields = [sanitize_identifier(n.lower()) for n in self._rel._field_names]
            for scheme in concept._reference_schemes:
                if scheme[0]._name in sanitized_fields:
                    key = Column(self, scheme[0]._name)
                    keys.append(key)
                    key_dict[scheme[0]._name] = key

        # TODO: this is correct, but the rel backend does the wrong thing with it
        # me = concept.new(**key_dict)
        # items = [me]
        # for field in self._rel._fields[1:]:
        #     field_rel = getattr(concept, field.name.lower())
        #     if sanitize_identifier(field.name.lower()) not in key_dict:
        #         items.append(field_rel(me, getattr(self, field.name)))
        # b.where(me).define(*items)

        # this is much less efficient than above

        if keys:
            me = concept.new(**key_dict)
            b.define(me)
        else:
            me = self._rel._field_refs[0]
            b.where(self).define(concept(me))
        for field in self._rel._fields[1:]:
            field_name = sanitize_identifier(field.name.lower())
            if field_name not in key_dict:
                r = b.Relationship(
                    f"{{{concept}}} has {{{field_name}:{field.type_str}}}",
                    parent=concept,
                    short_name=field_name,
                    model=self._rel._model
                )
                setattr(concept, field_name, r)
                relationship = getattr(concept, field_name)
                table_name = getattr(self, field.name)
                update = relationship(me, table_name)
                b.define(update)

    def _compile_lookup(self, compiler:b.Compiler, ctx:b.CompilerContext):
        self._lazy_init()
        Table._used_sources.add(self)
        compiler.lookup(self._rel, ctx)
        return

class Column(b.Producer):
    def __init__(self, source:Table, column_name:str) -> None:
        super().__init__(None)
        self._column_name = column_name
        self._source = source

    def _compile_lookup(self, compiler:b.Compiler, ctx:b.CompilerContext):
        compiler.lookup(self._source, ctx)
        for ix, field in enumerate(self._source._rel._field_refs):
            assert field._name is not None
            if field._name.lower() == self._column_name.lower():
                return compiler.lookup(b.RelationshipFieldRef(None, self._source._rel, ix), ctx)
        raise ValueError(f"Column {self._column_name} not found in {self._source._fqn}")
