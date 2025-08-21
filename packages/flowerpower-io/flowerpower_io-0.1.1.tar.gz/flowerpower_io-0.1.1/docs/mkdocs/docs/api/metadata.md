# Metadata

The `src/flowerpower_io/metadata.py` module is crucial for collecting and managing detailed metadata during I/O operations. This includes information about data schema, row and column counts, file paths, and timestamps of operations. This metadata can be invaluable for data governance, auditing, and understanding data lineage.

## Functions

### `get_serializable_schema(data: Any) -> dict`

Generates a JSON-serializable schema representation of the input data. This function inspects the data (e.g., Pandas DataFrame, Polars DataFrame, PyArrow Table) and extracts its schema, converting it into a dictionary format suitable for serialization.

- **Parameters**:
    - `data`: The input data (Pandas DataFrame, Polars DataFrame, PyArrow Table, etc.).
- **Returns**:
    - `dict`: A dictionary representing the serializable schema of the data.

### `get_dataframe_metadata(df: pd.DataFrame | pl.DataFrame | pa.Table) -> dict`

Extracts comprehensive metadata from a given DataFrame or PyArrow Table. This includes schema information, row count, column count, and a timestamp of when the metadata was generated.

- **Parameters**:
    - `df`: The input DataFrame (Pandas DataFrame, Polars DataFrame, or PyArrow Table).
- **Returns**:
    - `dict`: A dictionary containing the extracted metadata.

### `get_duckdb_metadata(connection: duckdb.DuckDBPyConnection, table_name: str) -> dict`

Retrieves metadata specifically from a DuckDB table. This function connects to a DuckDB database and extracts schema and other relevant information for the specified table.

- **Parameters**:
    - `connection`: An active DuckDB connection object.
    - `table_name`: The name of the table in the DuckDB database.
- **Returns**:
    - `dict`: A dictionary containing metadata about the DuckDB table.

### `get_pyarrow_dataset_metadata(dataset: pa.dataset.Dataset) -> dict`

Extracts metadata from a PyArrow Dataset. This includes information about the dataset's schema, partitioning, and the files it comprises.

- **Parameters**:
    - `dataset`: A PyArrow Dataset object.
- **Returns**:
    - `dict`: A dictionary containing metadata about the PyArrow Dataset.

### `get_delta_metadata(path: str) -> dict`

Retrieves metadata from a Delta Lake table located at the specified path. This function provides insights into the Delta table's structure, versioning, and other properties.

- **Parameters**:
    - `path`: The file path to the Delta Lake table.
- **Returns**:
    - `dict`: A dictionary containing metadata about the Delta Lake table.

### `get_mqtt_metadata(payload: bytes) -> dict`

(Conceptual) Extracts metadata from an MQTT message payload. This function is designed for real-time data streams, parsing the payload to extract relevant metadata.

- **Parameters**:
    - `payload`: The raw byte payload from an MQTT message.
- **Returns**:
    - `dict`: A dictionary containing metadata extracted from the MQTT payload.