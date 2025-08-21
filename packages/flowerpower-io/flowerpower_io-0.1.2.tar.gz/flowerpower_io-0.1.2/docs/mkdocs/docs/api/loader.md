# Loaders

The `flowerpower-io` library provides a comprehensive set of loader classes, each specialized for reading data from specific file formats or database systems. These loaders extend `BaseFileReader` or `BaseDatabaseReader` and offer tailored functionalities for efficient data ingestion.

## File-based Loaders

### `CSVFileReader`

Reads data from CSV files.
- **Path**: `src/flowerpower_io/loader/csv.py`
- **Example**:
  ```python
  from flowerpower_io.loader import CSVFileReader
  import pandas as pd

  csv_reader = CSVFileReader(path="data.csv")
  df = csv_reader.to_pandas()
  ```

### `ParquetFileReader`

Reads data from Parquet files.
- **Path**: `src/flowerpower_io/loader/parquet.py`
- **Example**:
  ```python
  from flowerpower_io.loader import ParquetFileReader
  import polars as pl

  parquet_reader = ParquetFileReader(path="data.parquet")
  df = parquet_reader.to_polars()
  ```

### `JsonFileReader`

Reads data from JSON files.
- **Path**: `src/flowerpower_io/loader/json.py`
- **Example**:
  ```python
  from flowerpower_io.loader import JsonFileReader
  import pyarrow as pa

  json_reader = JsonFileReader(path="data.json")
  table = json_reader.to_pyarrow_table()
  ```

### `DeltaTableReader`

Reads data from Delta Lake tables.
- **Path**: `src/flowerpower_io/loader/deltatable.py`
- **Example**:
  ```python
  from flowerpower_io.loader import DeltaTableReader
  import pandas as pd

  delta_reader = DeltaTableReader(path="path/to/delta_table")
  df = delta_reader.to_pandas()
  ```

### `PayloadReader` (MQTT)

Reads payloads from MQTT messages. This is a specialized loader for streaming data.
- **Path**: `src/flowerpower_io/loader/mqtt.py`
- **Example**:
  ```python
  # This example is conceptual, as MQTT integration requires a running broker and client setup.
  # from flowerpower_io.loader import PayloadReader
  # from paho.mqtt.client import Client as MQTTClient

  # mqtt_client = MQTTClient()
  # # ... configure and connect mqtt_client ...
  # payload_reader = PayloadReader(mqtt_client=mqtt_client)
  # payload = payload_reader.read_payload()
  # print(payload)
  ```

## Database Loaders

### `SQLiteReader`

Reads data from SQLite databases.
- **Path**: `src/flowerpower_io/loader/sqlite.py`
- **Example**:
  ```python
  from flowerpower_io.loader import SQLiteReader
  import pandas as pd

  sqlite_reader = SQLiteReader(path="my_database.db", table_name="my_table")
  df = sqlite_reader.to_pandas()
  ```

### `DuckDBReader`

Reads data from DuckDB databases.
- **Path**: `src/flowerpower_io/loader/duckdb.py`
- **Example**:
  ```python
  from flowerpower_io.loader import DuckDBReader
  import polars as pl

  duckdb_reader = DuckDBReader(path="my_duckdb.db", table_name="another_table")
  df = duckdb_reader.to_polars()
  ```

### `PostgreSQLReader`

Reads data from PostgreSQL databases.
- **Path**: `src/flowerpower_io/loader/postgres.py`
- **Example**:
  ```python
  from flowerpower_io.loader import PostgreSQLReader
  import pandas as pd

  pg_reader = PostgreSQLReader(
      database="mydb",
      user="myuser",
      password="mypassword",
      host="localhost",
      table_name="users"
  )
  df = pg_reader.to_pandas()
  ```

### `MySQLReader`

Reads data from MySQL databases.
- **Path**: `src/flowerpower_io/loader/mysql.py`
- **Example**:
  ```python
  from flowerpower_io.loader import MySQLReader
  import pandas as pd

  mysql_reader = MySQLReader(
      database="mydb",
      user="myuser",
      password="mypassword",
      host="localhost",
      table_name="products"
  )
  df = mysql_reader.to_pandas()
  ```

### `MSSQLReader`

Reads data from Microsoft SQL Server databases.
- **Path**: `src/flowerpower_io/loader/mssql.py`
- **Example**:
  ```python
  from flowerpower_io.loader import MSSQLReader
  import pandas as pd

  mssql_reader = MSSQLReader(
      database="mydb",
      user="myuser",
      password="mypassword",
      host="localhost",
      table_name="orders"
  )
  df = mssql_reader.to_pandas()
  ```

### `OracleDBReader`

Reads data from Oracle databases.
- **Path**: `src/flowerpower_io/loader/oracle.py`
- **Example**:
  ```python
  from flowerpower_io.loader import OracleDBReader
  import pandas as pd

  oracle_reader = OracleDBReader(
      database="mydb",
      user="myuser",
      password="mypassword",
      host="localhost",
      table_name="inventory"
  )
  df = oracle_reader.to_pandas()