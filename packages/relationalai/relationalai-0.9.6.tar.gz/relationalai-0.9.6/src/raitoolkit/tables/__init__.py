from dataclasses import dataclass
from relationalai.clients.snowflake import Provider
import pathlib
import os
from typing import Union, Any

@dataclass
class Table:
    provider: Provider
    database: str
    schema: str
    name: str
    
    def create_from_csv(self, csv_path: Union[str, pathlib.Path], if_exists: str = 'fail') -> None:
        """Create a table from a CSV file and load its data.
        
        Args:
            csv_path: Path to the CSV file
            if_exists: One of {'fail', 'replace', 'append'}
                - fail: Raise an error if table exists
                - replace: Drop and recreate table if exists
                - append: Keep existing table and append data
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
            
        # Handle existing table based on if_exists parameter
        if if_exists == 'replace':
            self.provider.sql(f"DROP TABLE IF EXISTS {self.database}.{self.schema}.{self.name}")
        elif if_exists == 'fail':
            result = self.provider.sql(f"""
                SELECT COUNT(*) as cnt
                FROM {self.database}.INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = '{self.schema}' 
                AND TABLE_NAME = '{self.name}'
            """)
            # Get first row's count value, regardless of result type
            row = result[0] if isinstance(result, list) else result
            raw_count: Any = row[0] if isinstance(row, (list, tuple)) else row['cnt']
            
            # Convert to string first to handle various numeric types
            count = int(str(raw_count).strip())
            
            if count > 0:
                raise ValueError(f"Table {self.database}.{self.schema}.{self.name} already exists")
        
        # Create a temporary stage for the file
        stage_name = f"@%{self.name}_temp_stage"
        self.provider.sql(f"CREATE TEMPORARY STAGE {stage_name}")
        
        try:
            # Put file into stage
            self.provider.sql(f"PUT file://{csv_path} {stage_name}")
            
            # Use COPY INTO with auto schema inference
            staged_file = f"{stage_name}/{os.path.basename(csv_path)}"
            self.provider.sql(f"""
                COPY INTO {self.database}.{self.schema}.{self.name} 
                FROM {staged_file}
                FILE_FORMAT = (
                    TYPE = CSV 
                    SKIP_HEADER = 1
                    INFERENCE_PARAMS = (AUTO_DETECT = TRUE)
                )
                MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
                PURGE = TRUE
                ON_ERROR = ABORT_STATEMENT
            """)
        finally:
            # Clean up the temporary stage
            self.provider.sql(f"DROP STAGE IF EXISTS {stage_name}")
    
    