import importlib.metadata

__version__ = importlib.metadata.version("flowerpower-io")

from .loader.csv import CSVDatasetReader, CSVFileReader
from .loader.deltatable import DeltaTableReader
from .loader.duckdb import DuckDBReader
from .loader.json import JsonDatasetReader, JsonFileReader
from .loader.mssql import MSSQLReader
from .loader.mysql import MySQLReader
from .loader.oracle import OracleDBReader
from .loader.parquet import ParquetDatasetReader, ParquetFileReader
from .loader.postgres import PostgreSQLReader
from .loader.pydala import PydalaDatasetReader
from .loader.sqlite import SQLiteReader

from .saver.csv import CSVDatasetWriter, CSVFileWriter
from .saver.deltatable import DeltaTableWriter
from .saver.duckdb import DuckDBWriter
from .saver.json import JsonDatasetWriter, JsonFileWriter
from .saver.mssql import MSSQLWriter
from .saver.mysql import MySQLWriter
from .saver.oracle import OracleDBWriter
from .saver.parquet import ParquetDatasetWriter, ParquetFileWriter
from .saver.postgres import PostgreSQLWriter
from .saver.pydala import PydalaDatasetWriter
from .saver.sqlite import SQLiteWriter

__all__ = [
    "CSVFileWriter",
    "CSVDatasetWriter",
    "DeltaTableWriter",
    "DuckDBWriter",
    "JsonFileWriter",
    "JsonDatasetWriter",
    "MSSQLWriter",
    "MySQLWriter",
    "OracleDBWriter",
    "ParquetFileWriter",
    "ParquetDatasetWriter",
    "PostgreSQLWriter",
    "PydalaDatasetWriter",
    "SQLiteWriter",
    "CSVFileReader",
    "CSVDatasetReader",
    "DeltaTableReader",
    "DuckDBReader",
    "JsonFileReader",
    "JsonDatasetReader",
    "MSSQLReader",
    "MySQLReader",
    "OracleDBReader",
    "ParquetFileReader",
    "ParquetDatasetReader",
    "PostgreSQLReader",
    "PydalaDatasetReader",
    "SQLiteReader",
]
