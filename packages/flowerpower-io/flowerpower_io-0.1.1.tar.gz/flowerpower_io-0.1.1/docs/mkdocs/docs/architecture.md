# Architecture

The `flowerpower-io` library is designed with a modular and extensible architecture, allowing for flexible data input/output operations across various formats and systems. At its core, the library follows a clear class hierarchy, promoting code reusability and maintainability.

## Core Design Principles

- **Modularity**: Separation of concerns, with distinct modules for base functionalities, loaders, savers, and metadata handling.
- **Extensibility**: Easy to add support for new file formats, database systems, or storage backends.
- **Abstraction**: Hides the complexities of underlying I/O operations from the user, providing a unified and intuitive API.
- **Data Structure Agnostic**: Supports seamless data transfer to and from popular data structures like Pandas DataFrames, Polars Dataframes, and PyArrow Tables.

## Class Hierarchy Overview

The library's core is built around a hierarchy of base classes defined in [`src/flowerpower_io/base.py`](src/flowerpower_io/base.py), which are then extended by specialized classes in the `loader/` and `saver/` modules.

### Base Classes

- **`BaseFileIO`**: Foundational class for all file-based I/O operations. Handles path resolution, filesystem initialization, and storage option management across various backends (local, S3, GCS, Azure, GitHub, GitLab).
    - `BaseFileReader`: Extends `BaseFileIO` for reading data from files. Supports various output formats (Pandas, Polars, PyArrow, DuckDB, DataFusion) and features like batch processing.
    - `BaseDatasetReader`: Specializes `BaseFileReader` for handling partitioned datasets, integrating with PyArrow Dataset and Pydala Dataset.
    - `BaseFileWriter`: Defines logic for writing data to files, managing output basename, concatenation, uniqueness, and write modes.
    - `BaseDatasetWriter`: Specializes `BaseFileWriter` for writing data as datasets, supporting partitioning, compression, and fine-grained control.
- **`BaseDatabaseIO`**: Foundational class for all database I/O operations. Manages connection strings, credentials, and provides methods for connecting to various SQL and NoSQL databases.
    - `BaseDatabaseReader`: Provides methods for reading data from relational and non-relational databases into various DataFrame formats (Polars, Pandas, PyArrow).
    - `BaseDatabaseWriter`: Defines logic for writing data to databases, supporting different write modes and data conversion.

## Loaders and Savers

`flowerpower-io` supports a wide array of data formats and integrates with various storage solutions through its specialized loader and saver classes.

### File-based I/O

| Format      | Loader Class(es)                                   | Saver Class(es)                                     |
|-------------|----------------------------------------------------|-----------------------------------------------------|
| **CSV**     | `CSVFileReader`, `CSVDatasetReader`                | `CSVFileWriter`, `CSVDatasetWriter`                 |
| **Parquet** | `ParquetFileReader`, `ParquetDatasetReader`, `PydalaDatasetReader` | `ParquetFileWriter`, `ParquetDatasetWriter`, `PydalaDatasetWriter` |
| **JSON**    | `JsonFileReader`, `JsonDatasetReader`              | `JsonFileWriter`, `JsonDatasetWriter`               |
| **DeltaTable** | `DeltaTableReader`                               | `DeltaTableWriter`                                  |
| **MQTT**    | `PayloadReader` (for consuming MQTT payloads)      | (N/A - Loader only)                                 |

**Supported Storage Backends (via `fsspec_utils`):**
- Local filesystem
- AWS S3
- Google Cloud Storage (GCS)
- Azure Blob Storage
- GitHub
- GitLab

### Database I/O

| Database     | Reader Class(es) | Writer Class(es) |
|--------------|------------------|------------------|
| **SQLite**   | `SQLiteReader`   | `SQLiteWriter`   |
| **DuckDB**   | `DuckDBReader`   | `DuckDBWriter`   |
| **PostgreSQL** | `PostgreSQLReader` | `PostgreSQLWriter` |
| **MySQL**    | `MySQLReader`    | `MySQLWriter`    |
| **MSSQL**    | `MSSQLReader`    | `MSSQLWriter`    |
| **Oracle**   | `OracleDBReader` | `OracleDBWriter` |