# `flowerpower_io` Library Documentation

## 1. Introduction

`flowerpower_io` is a robust and extensible Python library designed for efficient data input/output (I/O) operations. It provides a unified framework for interacting with various file formats and database systems, abstracting away the complexities of data handling. The library focuses on seamless data transfer to and from popular data structures like Pandas DataFrames, Polars Dataframes, and PyArrow Tables.

## 2. Core Class Hierarchy and Functionalities

The library's core is built around a clear hierarchy of base classes defined in [`src/flowerpower_io/base.py`](src/flowerpower_io/base.py), which are then extended by specialized classes in the `loader/` and `saver/` modules.

*   **`BaseFileIO`**: This is the foundational class for all file-based I/O operations. It handles common functionalities like path resolution, filesystem initialization, and storage option management across various storage backends (e.g., local, S3, GCS, Azure, GitHub, GitLab).
    *   `BaseFileReader` (inherits from `BaseFileIO`): Provides the fundamental methods for reading data from files. It supports various output formats (Pandas, Polars, PyArrow, DuckDB, DataFusion) and features like batch processing, file path inclusion, and concatenation of multiple files.
    *   `BaseDatasetReader` (inherits from `BaseFileReader`): Extends `BaseFileReader` for handling dataset-specific reading operations, particularly for partitioned datasets. It supports PyArrow Dataset and Pydala Dataset conversions, offering more advanced dataset-level functionalities.
    *   `BaseFileWriter` (inherits from `BaseFileIO`): Defines the core logic for writing data to files. It manages output basename, concatenation, uniqueness constraints, and various write modes (append, overwrite, delete_matching, error_if_exists).
    *   `BaseDatasetWriter` (inherits from `BaseFileWriter`): Specializes `BaseFileWriter` for writing data as datasets, supporting partitioning, compression, and fine-grained control over file and row group sizes. It also integrates with Pydala for advanced dataset writing.

*   **`BaseDatabaseIO`**: This is the foundational class for all database I/O operations. It manages database connection strings, credentials, and provides methods for connecting to various SQL and NoSQL databases.
    *   `BaseDatabaseReader` (inherits from `BaseDatabaseIO`): Provides methods for reading data from relational and non-relational databases into various DataFrame formats (Polars, Pandas, PyArrow) and integrates with DuckDB and DataFusion for SQL query execution.
    *   `BaseDatabaseWriter` (inherits from `BaseDatabaseIO`): Defines the core logic for writing data to databases, supporting different write modes (append, replace, fail) and handling data conversion for various database types.

## 3. Supported Data Formats and Storage Backends

`flowerpower_io` supports a wide array of data formats and integrates with various storage solutions, categorized by their respective loader and saver classes:

### File-based I/O

*   **CSV**: `CSVFileReader`, `CSVDatasetReader`, `CSVFileWriter`, `CSVDatasetWriter`
*   **Parquet**: `ParquetFileReader`, `ParquetDatasetReader`, `ParquetFileWriter`, `ParquetDatasetWriter`, `PydalaDatasetReader`, `PydalaDatasetWriter`
*   **JSON**: `JsonFileReader`, `JsonDatasetReader`, `JsonFileWriter`, `JsonDatasetWriter`
*   **DeltaTable**: `DeltaTableReader`, `DeltaTableWriter`
*   **MQTT (Loader Only)**: `PayloadReader` (for consuming MQTT payloads)

**Supported Storage Backends (via `fsspec_utils`):**
*   Local filesystem
*   AWS S3
*   Google Cloud Storage (GCS)
*   Azure Blob Storage
*   GitHub
*   GitLab

### Database I/O

*   **SQLite**: `SQLiteReader`, `SQLiteWriter`
*   **DuckDB**: `DuckDBReader`, `DuckDBWriter`
*   **PostgreSQL**: `PostgreSQLReader`, `PostgreSQLWriter`
*   **MySQL**: `MySQLReader`, `MySQLWriter`
*   **Microsoft SQL Server (MSSQL)**: `MSSQLReader`, `MSSQLWriter`
*   **Oracle**: `OracleDBReader`, `OracleDBWriter`

## 4. Metadata Handling

The [`src/flowerpower_io/metadata.py`](src/flowerpower_io/metadata.py) module is crucial for collecting and managing detailed metadata during I/O operations. This includes:

*   Schema information
*   Row and column counts
*   File paths
*   Timestamps of operations

## 5. Module Structure and Dependencies

The library's design emphasizes separation of concerns, ensuring modularity and extensibility:

*   [`src/flowerpower_io/base.py`](src/flowerpower_io/base.py): Defines the fundamental abstract classes for I/O operations.
*   [`src/flowerpower_io/metadata.py`](src/flowerpower_io/metadata.py): Handles metadata collection and management.
*   `src/flowerpower_io/loader/`: Contains specific implementations for reading data from various sources and formats.
*   `src/flowerpower_io/saver/`: Contains specific implementations for writing data to various destinations and formats.
*   `fsspec_utils`: Orchestrates file system interactions, providing a unified interface for different storage backends.

## 6. Usage Examples

The following examples illustrate common usage patterns for `flowerpower_io`:

```python
import pandas as pd
import polars as pl
from flowerpower_io.loader import CSVFileReader, ParquetDatasetReader, SQLiteReader
from flowerpower_io.saver import CSVFileWriter, ParquetDatasetWriter, PostgreSQLWriter

# Example 1: Reading a CSV file into a Pandas DataFrame
csv_loader = CSVFileReader(path="path/to/your/data.csv")
df_pandas = csv_loader.to_pandas()
print("CSV data (Pandas):")
print(df_pandas.head())

# Example 2: Writing a Polars DataFrame to a CSV file
data_polars = pl.DataFrame({
    "col1": [1, 2, 3],
    "col2": ["A", "B", "C"]
})
csv_writer = CSVFileWriter(path="output/new_data.csv")
csv_writer.write(data=data_polars)
print("\nPolars DataFrame written to output/new_data.csv")

# Example 3: Reading a Parquet dataset into a Polars LazyFrame
# Assuming 'partition_col' is a partition column in your dataset
parquet_dataset_loader = ParquetDatasetReader(
    path="s3://your-bucket/your-parquet-dataset/",
    format="parquet",
    storage_options={"key": "YOUR_AWS_ACCESS_KEY", "secret": "YOUR_AWS_SECRET_KEY"},
    partitioning="hive" # Or specify list of column names, e.g., ["year", "month"]
)
lf_polars = parquet_dataset_loader.to_polars(lazy=True)
print("\nParquet dataset loaded as Polars LazyFrame (first 5 rows after collection):")
print(lf_polars.limit(5).collect())

# Example 4: Writing a Pandas DataFrame to a Parquet dataset with partitioning
df_to_save = pd.DataFrame({
    "id": [1, 2, 3, 4],
    "value": ["foo", "bar", "baz", "qux"],
    "year": [2023, 2023, 2024, 2024]
})
parquet_dataset_writer = ParquetDatasetWriter(
    path="output/partitioned_data/",
    format="parquet",
    partition_by="year",
    mode="overwrite"
)
parquet_dataset_writer.write(data=df_to_save)
print("\nPandas DataFrame written to partitioned Parquet dataset in output/partitioned_data/")

# Example 5: Reading from a SQLite database into a Polars DataFrame
# Ensure 'your_database.db' and 'your_table_name' exist
sqlite_reader = SQLiteReader(table_name="your_table_name", path="path/to/your/database.db")
db_data_polars = sqlite_reader.to_polars()
print("\nData from SQLite (Polars):")
print(db_data_polars.head())

# Example 6: Writing a PyArrow Table to a PostgreSQL database
import pyarrow as pa
table_to_write = pa.table({
    "event_id": [101, 102],
    "event_name": ["login", "logout"]
})
postgres_writer = PostgreSQLWriter(
    table_name="events",
    server="localhost",
    port=5432,
    username="user",
    password="password",
    database="mydatabase",
    mode="append" # "append", "replace", or "fail"
)
postgres_writer.write(data=table_to_write)
print("\nPyArrow Table written to PostgreSQL database 'events' table.")

# Example 7: Reading JSON file with metadata
json_loader = JsonFileReader(path="path/to/your/data.json")
df_json, metadata_json = json_loader.to_pandas(metadata=True)
print("\nJSON data (Pandas) with metadata:")
print(df_json.head())
print("Metadata:", metadata_json)

# Example 8: Writing data as a Delta Table
delta_writer = DeltaTableWriter(path="output/my_delta_table/", mode="overwrite")
delta_writer.write(data=pd.DataFrame({"colA": [1, 2], "colB": ["X", "Y"]}))
print("\nPandas DataFrame written to Delta Lake table.")