# Base Classes

This section details the foundational abstract classes in `flowerpower-io` that serve as the building blocks for all I/O operations. These classes define common interfaces and functionalities, which are then specialized by concrete loader and saver implementations.

All base classes are located in [`src/flowerpower_io/base.py`](src/flowerpower_io/base.py).

## `BaseFileIO`

`BaseFileIO` is the foundational class for all file-based input/output operations. It provides core functionalities related to file path management, filesystem interactions, and handling storage options for various backends.

### Attributes

- **`path`**: The file path or a list of file paths. Can be a local path or a URI for remote storage.
- **`format`**: The format of the file (e.g., "csv", "parquet", "json").
- **`storage_options`**: A dictionary of options for the filesystem backend (e.g., AWS S3 credentials).

### Methods

- **`__post_init__(self)`**: Initializes the filesystem based on the provided path and storage options.
- **`protocol(self)`**: Property that returns the protocol of the file path (e.g., "s3", "file").
- **`_base_path(self)`**: Property that returns the base path of the file(s).
- **`_path(self)`**: Property that returns the resolved file path(s).
- **`_glob_path(self)`**: Property that returns the glob-ready file path(s).
- **`_root_path(self)`**: Property that returns the root path for the file(s).
- **`list_files(self)`**: Lists files based on the configured path.

## `BaseFileReader`

`BaseFileReader` extends `BaseFileIO` and provides fundamental methods for reading data from files. It supports conversion to various data structures like Pandas DataFrames, Polars DataFrames, and PyArrow Tables, and offers features like batch processing and metadata retrieval.

### Methods

- **`_load(self, query: str | None = None, reload: bool = False, **kwargs)`**: Internal method to load data.
- **`to_pandas(self, metadata: bool = False, **kwargs)`**: Reads data into a Pandas DataFrame.
- **`iter_pandas(self, **kwargs)`**: Returns an iterator for Pandas DataFrames.
- **`to_polars(self, lazy: bool = False, metadata: bool = False, **kwargs)`**: Reads data into a Polars DataFrame or LazyFrame.
- **`iter_polars(self, lazy: bool = False, **kwargs)`**: Returns an iterator for Polars DataFrames or LazyFrames.
- **`to_pyarrow_table(self, metadata: bool = False, **kwargs)`**: Reads data into a PyArrow Table.
- **`iter_pyarrow_table(self, **kwargs)`**: Returns an iterator for PyArrow Tables.
- **`to_duckdb_relation(self, connection: duckdb.DuckDBPyConnection | None = None, **kwargs)`**: Reads data into a DuckDB Relation.
- **`register_in_duckdb(self, connection: duckdb.DuckDBPyConnection, table_name: str, **kwargs)`**: Registers the data as a table in a DuckDB connection.
- **`to_duckdb(self, query: str, connection: duckdb.DuckDBPyConnection | None = None, **kwargs)`**: Executes a SQL query against the data using DuckDB.
- **`register_in_datafusion(self, context: SessionContext, table_name: str, **kwargs)`**: Registers the data as a table in a DataFusion context.
- **`filter(self, filter_expr)`**: Applies a filter expression to the data before loading.
- **`metadata(self)`**: Property that returns metadata about the loaded data.

## `BaseDatasetReader`

`BaseDatasetReader` extends `BaseFileReader` to handle dataset-specific reading operations, particularly for partitioned datasets. It provides specialized methods for working with PyArrow Datasets and Pydala Datasets.

### Methods

- **`to_pyarrow_dataset(self, **kwargs)`**: Reads data into a PyArrow Dataset.
- **`to_pandas(self, metadata: bool = False, **kwargs)`**: Overrides `BaseFileReader.to_pandas` for dataset-specific loading.
- **`to_polars(self, lazy: bool = False, metadata: bool = False, **kwargs)`**: Overrides `BaseFileReader.to_polars` for dataset-specific loading.
- **`to_pyarrow_table(self, metadata: bool = False, **kwargs)`**: Overrides `BaseFileReader.to_pyarrow_table` for dataset-specific loading.
- **`to_pydala_dataset(self, **kwargs)`**: Reads data into a Pydala Dataset.
- **`to_duckdb_relation(self, connection: duckdb.DuckDBPyConnection | None = None, **kwargs)`**: Overrides `BaseFileReader.to_duckdb_relation` for dataset-specific loading.
- **`register_in_duckdb(self, connection: duckdb.DuckDBPyConnection, table_name: str, **kwargs)`**: Overrides `BaseFileReader.register_in_duckdb` for dataset-specific registration.
- **`to_duckdb(self, query: str, connection: duckdb.DuckDBPyConnection | None = None, **kwargs)`**: Overrides `BaseFileReader.to_duckdb` for dataset-specific querying.
- **`register_in_datafusion(self, context: SessionContext, table_name: str, **kwargs)`**: Overrides `BaseFileReader.register_in_datafusion` for dataset-specific registration.
- **`filter(self, filter_expr)`**: Overrides `BaseFileReader.filter` for dataset-specific filtering.
- **`metadata(self)`**: Property that returns metadata about the dataset.

## `BaseFileWriter`

`BaseFileWriter` defines the core logic for writing data to files. It manages output paths, uniqueness constraints, and various write modes.

### Methods

- **`write(self, data: pd.DataFrame | pl.DataFrame | pa.Table, **kwargs)`**: Writes data to the specified file path.
    - `data`: The data to write (Pandas DataFrame, Polars DataFrame, or PyArrow Table).
    - `**kwargs`: Additional keyword arguments for the specific file format writer.
- **`metadata(self)`**: Property that returns metadata about the write operation.

## `BaseDatasetWriter`

`BaseDatasetWriter` specializes `BaseFileWriter` for writing data as datasets, supporting partitioning, compression, and fine-grained control over file and row group sizes. It also integrates with Pydala for advanced dataset writing.

### Methods

- **`write(self, data: pd.DataFrame | pl.DataFrame | pa.Table, **kwargs)`**: Writes data as a dataset.
    - `data`: The data to write.
    - `**kwargs`: Additional keyword arguments for the specific dataset writer.
- **`metadata(self)`**: Property that returns metadata about the dataset write operation.

## `BaseDatabaseIO`

`BaseDatabaseIO` is the foundational class for all database input/output operations. It manages database connection strings, credentials, and provides methods for connecting to various SQL and NoSQL databases.

### Attributes

- **`connection_string`**: The connection string for the database.
- **`server`**: The database server address.
- **`port`**: The database port.
- **`username`**: The database username.
- **`password`**: The database password.
- **`database`**: The database name.
- **`table_name`**: The name of the table to interact with.
- **`query`**: A SQL query to execute.
- **`path`**: File path for file-based databases (e.g., SQLite, DuckDB).
- **`type_`**: The type of database (e.g., "sqlite", "postgresql").

### Methods

- **`__post_init__(self)`**: Initializes the database connection.
- **`execute(self, query: str, cursor: bool = True, **query_kwargs)`**: Executes a SQL query.
- **`_to_pandas(self, data: pl.DataFrame | pa.Table)`**: Internal method to convert data to Pandas DataFrame.
- **`connect(self)`**: Establishes a connection to the database.

## `BaseDatabaseWriter`

`BaseDatabaseWriter` defines the core logic for writing data to databases, supporting different write modes and handling data conversion for various database types.

### Methods

- **`_write_sqlite(self, data: pl.DataFrame)`**: Internal method to write data to SQLite.
- **`_write_duckdb(self, data: pl.DataFrame)`**: Internal method to write data to DuckDB.
- **`_write_sqlalchemy(self, data: pl.DataFrame)`**: Internal method to write data using SQLAlchemy.
- **`write(self, data: pd.DataFrame | pl.DataFrame | pa.Table, **kwargs)`**: Writes data to the specified database table.
    - `data`: The data to write.
    - `**kwargs`: Additional keyword arguments for the specific database writer (e.g., `if_exists`).
- **`metadata(self)`**: Property that returns metadata about the database write operation.

## `BaseDatabaseReader`

`BaseDatabaseReader` provides methods for reading data from relational and non-relational databases into various DataFrame formats (Polars, Pandas, PyArrow) and integrates with DuckDB and DataFusion for SQL query execution.

### Methods

- **`__post_init__(self)`**: Initializes the database reader.
- **`_load(self, query: str | None = None, reload: bool = False, **kwargs)`**: Internal method to load data from the database.
- **`to_polars(self, **kwargs)`**: Reads data into a Polars DataFrame.
- **`to_pandas(self, **kwargs)`**: Reads data into a Pandas DataFrame.
- **`to_pyarrow_table(self, **kwargs)`**: Reads data into a PyArrow Table.
- **`to_duckdb_relation(self, connection: duckdb.DuckDBPyConnection | None = None, **kwargs)`**: Reads data into a DuckDB Relation.
- **`register_in_duckdb(self, connection: duckdb.DuckDBPyConnection, table_name: str, **kwargs)`**: Registers the data as a table in a DuckDB connection.
- **`register_in_datafusion(self, context: SessionContext, table_name: str, **kwargs)`**: Registers the data as a table in a DataFusion context.
- **`metadata(self)`**: Property that returns metadata about the database read operation.