# API Reference

Welcome to the `flowerpower-io` API reference documentation. This section provides detailed information about all public classes, functions, and methods available in the library.

## Overview

The `flowerpower-io` library provides a unified interface for reading and writing data from various sources and formats. The API is organized into several modules:

- [Base Classes](base.md) - Core classes for file and database operations
- [Metadata Functions](metadata.md) - Functions for extracting metadata from data sources
- [Loader Classes](loader.md) - Classes for reading data from various sources
- [Saver Classes](saver.md) - Classes for writing data to various destinations

## Quick Navigation

### Base Classes

The base classes form the foundation of the library and provide common functionality for all I/O operations.

- [BaseFileIO](base.md#basefileio) - Base class for file I/O operations
- [BaseFileReader](base.md#basereader) - Base class for file reading operations
- [BaseDatasetReader](base.md#basedatasetreader) - Base class for dataset reading operations
- [BaseFileWriter](base.md#basewriter) - Base class for file writing operations
- [BaseDatasetWriter](base.md#basedatasetwriter) - Base class for dataset writing operations
- [BaseDatabaseIO](base.md#basedatabaseio) - Base class for database operations
- [BaseDatabaseReader](base.md#basedatabasereader) - Base class for database reading operations
- [BaseDatabaseWriter](base.md#basedatabasewriter) - Base class for database writing operations

### Metadata Functions

Metadata functions help you understand the structure and properties of your data before processing it.

- [get_dataframe_metadata](metadata.md#get_dataframe_metadata) - Extract metadata from DataFrames
- [get_pyarrow_table_metadata](metadata.md#get_pyarrow_table_metadata) - Extract metadata from PyArrow Tables
- [get_pyarrow_dataset_metadata](metadata.md#get_pyarrow_dataset_metadata) - Extract metadata from PyArrow Datasets
- [get_duckdb_relation_metadata](metadata.md#get_duckdb_relation_metadata) - Extract metadata from DuckDB relations
- [get_datafusion_relation_metadata](metadata.md#get_datafusion_relation_metadata) - Extract metadata from DataFusion relations
- [get_file_metadata](metadata.md#get_file_metadata) - Extract metadata from files
- [get_database_metadata](metadata.md#get_database_metadata) - Extract metadata from database tables
- [get_metadata](metadata.md#get_metadata) - Generic metadata extraction function


### Loader Classes

Loader classes provide specialized functionality for reading data from various sources.

#### File Loaders
- [CSVLoader](loader.md#csvloader) - Load data from CSV files
- [ParquetLoader](loader.md#parquetloader) - Load data from Parquet files
- [JSONLoader](loader.md#jsonloader) - Load data from JSON files
- [DeltaTableLoader](loader.md#deltatableloader) - Load data from Delta Lake tables
- [PydalaLoader](loader.md#pydalaloader) - Load data from Pydala datasets
- [MQTTLoader](loader.md#mqttloader) - Load data from MQTT messages

#### Database Loaders
- [SQLiteLoader](loader.md#sqliteloader) - Load data from SQLite databases
- [DuckDBLoader](loader.md#duckdbloader) - Load data from DuckDB databases
- [PostgreSQLLoader](loader.md#postgresloader) - Load data from PostgreSQL databases
- [MySQLLoader](loader.md#mysqlloader) - Load data from MySQL databases
- [MSSQLLoader](loader.md#mssqlloader) - Load data from Microsoft SQL Server databases
- [OracleLoader](loader.md#oracleloader) - Load data from Oracle databases

### Saver Classes

Saver classes provide specialized functionality for writing data to various destinations.

#### File Savers
- [CSVSaver](saver.md#csvsaver) - Save data to CSV files
- [ParquetSaver](saver.md#parquetsaver) - Save data to Parquet files
- [JSONSaver](saver.md#jsonsaver) - Save data to JSON files
- [DeltaTableSaver](saver.md#deltatablesaver) - Save data to Delta Lake tables
- [PydalaSaver](saver.md#pydalasaver) - Save data to Pydala datasets
- [MQTTSaver](saver.md#mqtt saver) - Save data to MQTT messages

#### Database Savers
- [SQLiteSaver](saver.md#sqlitesaver) - Save data to SQLite databases
- [DuckDBSaver](saver.md#duckdbsaver) - Save data to DuckDB databases
- [PostgreSQLSaver](saver.md#postgresqlsaver) - Save data to PostgreSQL databases
- [MySQLSaver](saver.md#mysqlsaver) - Save data to MySQL databases
- [MSSQLSaver](saver.md#mssqlsaver) - Save data to Microsoft SQL Server databases
- [OracleSaver](saver.md#oraclesaver) - Save data to Oracle databases

## Usage Examples

### Basic File Operations

```python
from flowerpower_io import CSVLoader, ParquetSaver

# Load data from CSV
loader = CSVLoader("data.csv")
df = loader.to_polars()

# Save data to Parquet
saver = ParquetSaver("output/")
saver.write(df)
```

### Database Operations

```python
from flowerpower_io import PostgreSQLLoader, SQLiteSaver

# Load from PostgreSQL
loader = PostgreSQLLoader(
    host="localhost",
    username="user",
    password="password",
    database="mydb",
    table_name="users"
)
df = loader.to_polars()

# Save to SQLite
saver = SQLiteSaver(
    path="database.db",
    table_name="users"
)
saver.write(df)
```

### Metadata Extraction

```python
from flowerpower_io.metadata import get_dataframe_metadata

# Get metadata from DataFrame
metadata = get_dataframe_metadata(df)
print(metadata)
```


## Common Patterns

### Reading Multiple Files

```python
from flowerpower_io import ParquetLoader

# Load multiple Parquet files
loader = ParquetLoader("data/*.parquet")
df = loader.to_polars()
```

### Writing with Partitioning

```python
from flowerpower_io import ParquetSaver

# Save with partitioning
saver = ParquetSaver(
    path="output/",
    partition_by="category",
    compression="zstd"
)
saver.write(df)
```

### Database Connection Management

```python
from flowerpower_io import PostgreSQLLoader

# Using context manager for connection
with PostgreSQLLoader(
    host="localhost",
    username="user",
    password="password",
    database="mydb"
) as loader:
    df = loader.to_polars()
```

## Error Handling

The library provides comprehensive error handling for various scenarios:

```python
from flowerpower_io import CSVLoader

try:
    loader = CSVLoader("nonexistent.csv")
    df = loader.to_polars()
except FileNotFoundError:
    print("File not found")
except Exception as e:
    print(f"Error: {e}")
```

## Performance Tips

1. Use `opt_dtypes=True` for better memory efficiency
2. Use `batch_size` for large datasets
3. Use `concat=False` when working with multiple files separately
4. Use appropriate compression for your data format
5. Use partitioning for large datasets

## See Also

- [Installation Guide](../installation.md)
- [Quick Start Guide](../quickstart.md)
- [Advanced Usage](../advanced.md)
- [Architecture Overview](../architecture.md)