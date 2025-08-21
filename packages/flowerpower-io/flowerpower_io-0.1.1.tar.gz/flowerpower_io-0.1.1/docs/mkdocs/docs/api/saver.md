# Savers

The `flowerpower-io` library provides a comprehensive set of saver classes, each specialized for writing data to specific file formats or database systems. These savers extend `BaseFileWriter` or `BaseDatabaseWriter` and offer tailored functionalities for efficient data persistence.

## File-based Savers

### `CSVFileWriter`

Writes data to CSV files.
- **Path**: `src/flowerpower_io/saver/csv.py`
- **Example**:
  ```python
  from flowerpower_io.saver import CSVFileWriter
  import pandas as pd

  df = pd.DataFrame({'col1': [1, 2], 'col2': ['A', 'B']})
  csv_writer = CSVFileWriter(path="output.csv")
  csv_writer.write(data=df)
  ```

### `ParquetFileWriter`

Writes data to Parquet files.
- **Path**: `src/flowerpower_io/saver/parquet.py`
- **Example**:
  ```python
  from flowerpower_io.saver import ParquetFileWriter
  import polars as pl

  df = pl.DataFrame({'col1': [1, 2], 'col2': ['A', 'B']})
  parquet_writer = ParquetFileWriter(path="output.parquet")
  parquet_writer.write(data=df)
  ```

### `JsonFileWriter`

Writes data to JSON files.
- **Path**: `src/flowerpower_io/saver/json.py`
- **Example**:
  ```python
  from flowerpower_io.saver import JsonFileWriter
  import pyarrow as pa

  table = pa.table({'col1': [1, 2], 'col2': ['A', 'B']})
  json_writer = JsonFileWriter(path="output.json")
  json_writer.write(data=table)
  ```

### `DeltaTableWriter`

Writes data to Delta Lake tables.
- **Path**: `src/flowerpower_io/saver/deltatable.py`
- **Example**:
  ```python
  from flowerpower_io.saver import DeltaTableWriter
  import pandas as pd

  df = pd.DataFrame({'col1': [1, 2], 'col2': ['A', 'B']})
  delta_writer = DeltaTableWriter(path="path/to/delta_table")
  delta_writer.write(data=df)
  ```

### `MQTTWriter` (Conceptual)

Writes data as MQTT messages.
- **Path**: `src/flowerpower_io/saver/mqtt.py`
- **Example**:
  ```python
  # This example is conceptual, as MQTT integration requires a running broker and client setup.
  # from flowerpower_io.saver import MQTTWriter
  # import pandas as pd

  # df = pd.DataFrame({'sensor_id': ['A1'], 'value': [10.5]})
  # mqtt_writer = MQTTWriter(topic="sensor/data", host="localhost")
  # mqtt_writer.write(data=df)
  ```

## Database Savers

### `SQLiteWriter`

Writes data to SQLite databases.
- **Path**: `src/flowerpower_io/saver/sqlite.py`
- **Example**:
  ```python
  from flowerpower_io.saver import SQLiteWriter
  import pandas as pd

  df = pd.DataFrame({'id': [1, 2], 'name': ['Alice', 'Bob']})
  sqlite_writer = SQLiteWriter(path="my_database.db", table_name="users")
  sqlite_writer.write(data=df)
  ```

### `DuckDBWriter`

Writes data to DuckDB databases.
- **Path**: `src/flowerpower_io/saver/duckdb.py`
- **Example**:
  ```python
  from flowerpower_io.saver import DuckDBWriter
  import polars as pl

  df = pl.DataFrame({'id': [1, 2], 'product': ['Apple', 'Banana']})
  duckdb_writer = DuckDBWriter(path="my_duckdb.db", table_name="products")
  duckdb_writer.write(data=df)
  ```

### `PostgreSQLWriter`

Writes data to PostgreSQL databases.
- **Path**: `src/flowerpower_io/saver/postgres.py`
- **Example**:
  ```python
  from flowerpower_io.saver import PostgreSQLWriter
  import pandas as pd

  df = pd.DataFrame({'id': [1, 2], 'event': ['login', 'logout']})
  pg_writer = PostgreSQLWriter(
      database="mydb",
      user="myuser",
      password="mypassword",
      host="localhost",
      table_name="events"
  )
  pg_writer.write(data=df)
  ```

### `MySQLWriter`

Writes data to MySQL databases.
- **Path**: `src/flowerpower_io/saver/mysql.py`
- **Example**:
  ```python
  from flowerpower_io.saver import MySQLWriter
  import pandas as pd

  df = pd.DataFrame({'id': [1, 2], 'customer': ['John', 'Jane']})
  mysql_writer = MySQLWriter(
      database="mydb",
      user="myuser",
      password="mypassword",
      host="localhost",
      table_name="customers"
  )
  mysql_writer.write(data=df)
  ```

### `MSSQLWriter`

Writes data to Microsoft SQL Server databases.
- **Path**: `src/flowerpower_io/saver/mssql.py`
- **Example**:
  ```python
  from flowerpower_io.saver import MSSQLWriter
  import pandas as pd

  df = pd.DataFrame({'id': [1, 2], 'order_id': [101, 102]})
  mssql_writer = MSSQLWriter(
      database="mydb",
      user="myuser",
      password="mypassword",
      host="localhost",
      table_name="orders"
  )
  mssql_writer.write(data=df)
  ```

### `OracleDBWriter`

Writes data to Oracle databases.
- **Path**: `src/flowerpower_io/saver/oracle.py`
- **Example**:
  ```python
  from flowerpower_io.saver import OracleDBWriter
  import pandas as pd

  df = pd.DataFrame({'id': [1, 2], 'item': ['Pen', 'Book']})
  oracle_writer = OracleDBWriter(
      database="mydb",
      user="myuser",
      password="mypassword",
      host="localhost",
      table_name="items"
  )
  oracle_writer.write(data=df)