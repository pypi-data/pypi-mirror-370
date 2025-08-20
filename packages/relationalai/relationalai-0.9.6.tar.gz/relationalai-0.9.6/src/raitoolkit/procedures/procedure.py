
from dataclasses import dataclass
import textwrap
from typing import cast
from relationalai.clients.snowflake import Provider

@dataclass
class Procedure:
    provider: Provider
    database: str
    schema: str
    name: str

    def create(self, python_code: str, args: list[tuple[str, str]] = [], returns: str = "STRING"):
        arg_string = ", ".join([f"{arg[0]} {arg[1]}" for arg in args])
        sql_query = textwrap.dedent(f"""
        CREATE OR REPLACE PROCEDURE {self.database}.{self.schema}.{self.name}({arg_string})
        RETURNS {returns}
        LANGUAGE PYTHON
        RUNTIME_VERSION = '3.11'
        PACKAGES = ('snowflake-snowpark-python')
        HANDLER = 'main'
        EXECUTE AS CALLER
        AS
        $$
        {textwrap.indent(python_code, " " * 8)}
        $$;
        """)
        return self.provider.sql(sql_query)
    
    def execute(self, *args):
        arg_string = ", ".join([f"'{arg}'" if isinstance(arg, str) else str(arg) for arg in args])
        sql_query = f"CALL {self.database}.{self.schema}.{self.name}({arg_string});"
        return self.provider.sql(sql_query)
    
    def delete(self):
        for row in cast(list, self.provider.sql(f"show procedures in {self.database}.{self.schema};")):
            if row["name"].upper() == self.name.upper():
                name_with_input_args = row["arguments"].split(" RETURN ")[0]
                self.provider.sql(f"drop procedure {self.database}.{self.schema}.{name_with_input_args}")

    def get_python_code(self, database, schema, sproc_name):
        query = f"""
            SELECT PROCEDURE_DEFINITION
            FROM {database.upper()}.INFORMATION_SCHEMA.PROCEDURES
            WHERE PROCEDURE_NAME = '{sproc_name.upper()}'
            AND PROCEDURE_SCHEMA = '{schema.upper()}';
        """
        response = cast(list, self.provider.sql(query))

        if not response:
            raise ValueError(f"Stored procedure '{sproc_name}' not found in {database}.{schema}.")

        procedure_definition = response[0]['PROCEDURE_DEFINITION']
        if not procedure_definition:
            raise ValueError(f"No definition found for stored procedure '{sproc_name}'.")

        return procedure_definition
