from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy import MetaData
from sqlalchemy.schema import CreateTable


class IR:
    def __init__(self, *, file_name, table_name="data", engine="sqlite", sample_size=None):
        assert len(file_name) != 0, "file_name is empty"
        assert engine in ["duckdb", "sqlite"], f"Unsupported engine: {engine}. Use 'duckdb' or 'sqlite'"

        self.table_name = table_name
        self.file_name = file_name
        self.engine_type = engine
        self.sample_size = sample_size

        # Initialize SQLAlchemy engine
        if engine == "duckdb":
            self.engine = create_engine("duckdb:///:memory:")
        else:  # sqlite
            self.engine = create_engine("sqlite:///:memory:")

        self._load_data()

    def _load_data(self):
        """Load data into database using pandas and SQLAlchemy"""
        file_ext = Path(self.file_name).suffix.lower()

        # Load data using pandas
        if file_ext == ".csv":
            df = pd.read_csv(self.file_name)
        elif file_ext in [".xlsx", ".xls"]:
            df = pd.read_excel(self.file_name)
        elif file_ext == ".parquet":
            df = pd.read_parquet(self.file_name)
        elif file_ext == ".json":
            df = pd.read_json(self.file_name)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

        if self.sample_size is not None and isinstance(self.sample_size, int):
            if self.sample_size > len(df):
                raise ValueError(f"Sample size {self.sample_size} exceeds number of rows in the data: {len(df)}")
            df = df.sample(n=self.sample_size, random_state=42).reset_index(drop=True)

        # Load dataframe into database using SQLAlchemy
        df.to_sql(self.table_name, self.engine, if_exists="replace", index=False)

    def query(self, sql):
        """Execute a SQL query and return a pandas DataFrame"""
        return pd.read_sql_query(sql, self.engine)

    def execute(self, sql):
        """Execute a SQL command and return raw results"""
        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            return result.fetchall()

    def close(self):
        """Close the database connection"""
        self.engine.dispose()

    def get_schema(self):
        """Get table schema as CREATE TABLE statement"""
        metadata = MetaData()
        metadata.reflect(bind=self.engine, only=[self.table_name])
        table = metadata.tables[self.table_name]
        create_statement = CreateTable(table).compile(self.engine)

        return str(create_statement)
