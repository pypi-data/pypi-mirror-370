"""
A simple metamodel for SQL.
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass
from io import StringIO
from typing import Optional, Union, Tuple, Any
from relationalai.early_access.metamodel.util import Printer as BasePrinter
import json

@dataclass(frozen=True)
class Node:
    def __str__(self):
        return to_string(self)

@dataclass(frozen=True)
class Program(Node):
    """ The root node of the SQL program. """
    statements: list[Node]

#-------------------------------------------------
# Table
#-------------------------------------------------

@dataclass(frozen=True)
class Column(Node):
    name: str
    type: str

@dataclass(frozen=True)
class Table(Node):
    name: str
    columns: list[Column]

#-------------------------------------------------
# Statements
#-------------------------------------------------

@dataclass(frozen=True)
class CreateTable(Node):
    table: Table
    if_not_exists: bool = False

@dataclass(frozen=True)
class CreateView(Node):
    name: str
    query: Union[Select, CTE]

@dataclass(frozen=True)
class Insert(Node):
    table: str
    columns: list[str]
    values: list[Tuple[Any, ...]]
    select: Optional[Select]

@dataclass(frozen=True)
class Update(Node):
    table: str
    set: list[UpdateSet]
    where: Optional[Where]

@dataclass(frozen=True)
class UpdateSet(Node):
    name: str
    expression: str

@dataclass(frozen=True)
class Select(Node):
    distinct: bool
    vars: list[Union[VarRef, RowNumberVar, int]]
    froms: Union[list[From], Select]
    where: Optional[Where] = None
    joins: Optional[list[Join]] = None
    group_by: Optional[list[VarRef]] = None
    limit: Optional[int] = None

@dataclass(frozen=True)
class VarRef(Node):
    name: str
    column: Optional[str] = None
    alias: Optional[str] = None

@dataclass(frozen=True)
class From(Node):
    table: str
    alias: Optional[str]

@dataclass(frozen=True)
class Join(Node):
    table: str
    alias: Optional[str]
    on: Optional[Expr] = None

@dataclass(frozen=True)
class LeftOuterJoin(Join):
    pass

@dataclass(frozen=True)
class FullOuterJoin(Join):
    pass

@dataclass(frozen=True)
class RowNumberVar(Node):
    order_by_vars: list[OrderByVar]
    partition_by_vars: list[str]
    alias: str

@dataclass(frozen=True)
class OrderByVar(Node):
    var: str
    is_ascending: bool

# TODO: consider removing Where and make Select.where: Expr
@dataclass(frozen=True)
class Where(Node):
    expression: Expr

@dataclass(frozen=True)
class RawSource(Node):
    """ A raw source for SQL, used to represent a raw SQL query or expression. """
    src: str

#-------------------------------------------------
# Clauses
#-------------------------------------------------
# TODO: move clauses from other sections

@dataclass(frozen=True)
class CTE(Node):
    """ Common Table Expressions. """
    recursive: bool
    name: str
    columns: list[str]
    selects: list[Select]

#-------------------------------------------------
# Expressions
#-------------------------------------------------

@dataclass(frozen=True)
class Expr(Node):
    pass

@dataclass(frozen=True)
class And(Expr):
    expr: list[Expr]

@dataclass(frozen=True)
class Or(Expr):
    expr: list[Expr]

@dataclass(frozen=True)
class Terminal(Expr):
    """ Avoid going deeper in the meta-model, this is an arbitrary terminal expression."""
    expr: str

@dataclass(frozen=True)
class NotNull(Expr):
    var: str

@dataclass(frozen=True)
class NotExists(Expr):
    expr: Select

@dataclass(frozen=True)
class Like(Expr):
    left: str
    right: str

#--------------------------------------------------
# Printer
#--------------------------------------------------

def to_string(node) -> str:
    io = StringIO()
    Printer(io).print_node(node, 0)
    return io.getvalue()

@dataclass(frozen=True)
class Printer(BasePrinter):

    _RESERVED_NAMES: frozenset[str] = frozenset({"right", "left"})

    def _is_reserved_name(self, name: str) -> bool:
        return isinstance(name, str) and name.lower() in self._RESERVED_NAMES

    def _join(self, args, sep=', ', indent=0):
        for i, s in enumerate(args):
            if i != 0:
                if indent != 0:
                    self._print(sep.rstrip())
                    self._nl()
                else:
                    self._print(sep)
            self.print_node(s, indent)

    def _print_value(self, value, quote_strings:bool = False):
        if isinstance(value, tuple):
            for i, v in enumerate(value):
                if i != 0:
                    self._print(", ")
                self._print_value(v, True)
        elif isinstance(value, str):
            if quote_strings:
                self._print(json.dumps(value))
            else:
                self._print(value)
        elif isinstance(value, bool):
            self._print(str(value).lower())
        elif isinstance(value, datetime.date):
            self._print(f"'{value}'")
        elif isinstance(value, type(None)):
            self._print("NULL")
        else:
            self._print(str(value))

    def _get_table_name(self, name: str) -> str:
        return f'"{name}"' if self._is_reserved_name(name) else name

    def print_node(self, node:Node, indent=0, inlined=False) -> None:
        # Table
        if isinstance(node, Program):
            for idx, d in enumerate(node.statements):
                self.print_node(d, indent)
                # Avoid an extra newline at the end of the file.
                if idx != len(node.statements) - 1:
                    self._nl()
        elif isinstance(node, Table):
            self._print(f"{self._get_table_name(node.name)} (")
            self._join(node.columns)
            self._print(")")
        elif isinstance(node, Column):
            self._print(f"{node.name} {node.type}")

        # Statements
        elif isinstance(node, CreateTable):
            clause = "IF NOT EXISTS " if node.if_not_exists else ""
            self._print(f"CREATE TABLE {clause}{node.table};")
        elif isinstance(node, CreateView):
            # TODO - crying a bit inside :(
            self._print_nl(f"DROP TABLE IF EXISTS {self._get_table_name(node.name)};")
            self._print(f"CREATE VIEW {self._get_table_name(node.name)} AS ")
            self.print_node(node.query, indent, True)
            self._print(";")
        elif isinstance(node, Insert):
            self._print(f"INSERT INTO {self._get_table_name(node.table)} ")
            if len(node.columns) > 0:
                self._print("(")
                self._join(node.columns)
                self._print(") ")
            if len(node.values) > 0:
                # We need to use `SELECT` with `UNION ALL` instead of `VALUES` because Snowflake parses and restricts
                #   certain expressions in VALUES(...). Built-in functions like HASH() or MD5() are often rejected unless used in SELECT.
                for i, value in enumerate(node.values):
                    if i != 0:
                        self._print(" UNION ALL ")
                    self._print("SELECT ")
                    self._join(value)
            if node.select is not None:
                self.print_node(node.select, indent, True)
            self._print(";")
        elif isinstance(node, Update):
            self._print(f"UPDATE {self._get_table_name(node.table)} SET ")
            self._join(node.set)
            if node.where is not None:
                self.print_node(node.where, indent)
            self._print(";")
        elif isinstance(node, UpdateSet):
            self._print(f"{node.name} = {node.expression}")
        elif isinstance(node, Select):
            self._indent_print(indent, "SELECT ")
            if node.distinct and node.froms:
                self._print("DISTINCT ")
            self._join(node.vars)
            if node.froms:
                self._print(" FROM ")
                if isinstance(node.froms, Select):
                    # If `froms` is a `Select`, we need to print it inline
                    self._print("( ")
                    self.print_node(node.froms, indent, True)
                    self._print(" )")
                else:
                    self._join(node.froms)
            if node.joins:
                self._print(" ")
                self._join(node.joins, sep=" ")
            if node.where:
                self.print_node(node.where, indent)
            if node.group_by:
                self._print(" GROUP BY ")
                self._join(node.group_by)
            if node.limit:
                self._print(f" LIMIT {node.limit}")
            if not inlined:
                self._print(";")
        elif isinstance(node, VarRef):
            if node.column is None:
                self._print(node.name)
            else:
                if node.column.lower() == "any":
                    self._print(f'{node.name}."{node.column}"')
                else:
                    self._print(f"{node.name}.{node.column}")
            if node.alias and node.alias != node.column:
                if '-' in node.alias:
                    # If alias contains a dash, we need to quote it
                    self._print(f' as "{node.alias}"')
                else:
                    self._print(f" as {node.alias}")
        elif isinstance(node, RowNumberVar):
            self._print("ROW_NUMBER() OVER (")
            if node.partition_by_vars:
                self._print(" PARTITION BY ")
                self._join(node.partition_by_vars)
            self._print(" ORDER BY ")
            self._join(node.order_by_vars)
            self._print(f" ) as {node.alias}")
        elif isinstance(node, OrderByVar):
            self._print(node.var)
            if node.is_ascending:
                self._print(" ASC")
            else:
                self._print(" DESC")
        elif isinstance(node, From):
            self._print(self._get_table_name(node.table))
            if node.alias is not None:
                self._print(f" AS {node.alias}")
        elif isinstance(node, Join):
            join_type = (
                "LEFT OUTER JOIN" if isinstance(node, LeftOuterJoin)
                else "FULL OUTER JOIN" if isinstance(node, FullOuterJoin)
                else "JOIN"
            )
            self._print(f"{join_type} {self._get_table_name(node.table)}")
            if node.alias is not None:
                self._print(f" AS {node.alias}")
            self._print(" ON ")
            if node.on is None:
                self._print("TRUE")
            else:
                self.print_node(node.on, indent, True)
        elif isinstance(node, Where):
            self._print(f" WHERE {node.expression}")
        elif isinstance(node, RawSource):
            self._print(node.src)

        # Clauses
        elif isinstance(node, CTE):
            self._print("WITH ")
            if node.recursive:
                self._print("RECURSIVE ")
            self._print(f"{self._get_table_name(node.name)} (")
            self._join(node.columns)
            self._print_nl(") AS (")
            for i, s in enumerate(node.selects):
                if i != 0:
                    self._nl()
                    self._indent_print_nl(indent + 2, "UNION ALL")
                self.print_node(s, indent + 1, True)
            self._nl()
            self._print(f") SELECT * FROM {self._get_table_name(node.name)}")
            if not inlined:
                self._print(";")
        # --------------------------------------------------
        # Primitives, Annotations
        # --------------------------------------------------
        elif isinstance(node, (str, int, float, bool, datetime.date, tuple, type(None))):
            self._indent_print(indent, "")
            self._print_value(node)
        # Expressions
        elif isinstance(node, And):
            self._join(node.expr, " AND ", indent)
        elif isinstance(node, Or):
            self._print("( ")
            for i, expr in enumerate(node.expr):
                if i > 0:
                    self._print(" OR ")
                needs_parens = isinstance(expr, And)
                if needs_parens:
                    self._print("( ")
                self.print_node(expr, indent, True)
                if needs_parens:
                    self._print(" )")
            self._print(" )")
        elif isinstance(node, Terminal):
            self._print(node.expr)
        elif isinstance(node, NotNull):
            self._print(f"{node.var} IS NOT NULL")
        elif isinstance(node, NotExists):
            self._print("NOT EXISTS ( ")
            self.print_node(node.expr, indent, True)
            self._print(" )")
        elif isinstance(node, Like):
            self._print(f"{node.left} LIKE {node.right}")
        else:
            raise Exception(f"Missing SQL.pprint({type(node)}): {node}")