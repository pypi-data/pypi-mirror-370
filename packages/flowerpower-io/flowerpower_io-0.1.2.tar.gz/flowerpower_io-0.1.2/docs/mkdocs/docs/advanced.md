# Advanced Usage

This section delves into advanced features of `flowerpower-io`, covering performance optimization, integration with external systems, and specific database integrations like DuckDB and DataFusion.

## 1. Performance Optimization

`flowerpower-io` is designed for efficiency, but you can further optimize performance with these tips:

- **Batch Processing**: For large datasets, consider processing data in batches to manage memory usage and improve throughput. `flowerpower-io` loaders and savers often support internal batching mechanisms.
- **Lazy Loading with Polars**: When working with Polars, leverage LazyFrames (`to_polars(lazy=True)`) to defer computation until necessary, which can significantly reduce memory footprint and improve performance for complex transformations.
- **Efficient File Formats**: Utilize binary file formats like Parquet over text-based formats like CSV for better performance due to columnar storage and compression.
- **Storage Options**: Properly configure `storage_options` for remote storage (e.g., S3, GCS) to optimize network transfers and authentication.

## 2. Integration with External Systems

`flowerpower-io` can be integrated into larger data pipelines and workflows.

### Message Queues (e.g., MQTT)

The `PayloadReader` can consume data from message queues, allowing `flowerpower-io` to act as a data ingress point for real-time data streams.

```python
from flowerpower_io.loader import PayloadReader
import paho.mqtt.client as mqtt
import time

# This is a simplified example. In a real scenario, you'd handle
# MQTT client setup, connection, and message consumption more robustly.

# class MockMQTTClient:
#     def __init__(self):
#         self.payload = None
#     def subscribe(self, topic): pass
#     def on_message(self, client, userdata, msg):
#         self.payload = msg.payload.decode('utf-8')

# # Simulate an MQTT client and message
# mock_client = MockMQTTClient()
# # Simulate a message being received
# # In a real system, this would be triggered by an actual MQTT message
# # mock_client.on_message(None, None, type('obj', (object,), {'payload': b'{"sensor_id": "A1", "temperature": 25.5}'})())

# # payload_reader = PayloadReader(mqtt_client=mock_client)

# # # In a real application, you would continuously check for new payloads
# # # For this example, we'll just simulate one message
# # time.sleep(1) # Give some time for the "message" to arrive
# # if payload_reader.has_new_payload():
# #     data = payload_reader.read_payload()
# #     print("Received data from MQTT:", data)
```

### Cloud Storage (S3, GCS, Azure Blob)

Utilize `fsspec_utils` for seamless interaction with various cloud storage providers.

```python
# Example of reading from S3 (requires appropriate AWS credentials configured)
# from flowerpower_io.loader import ParquetFileReader

# s3_reader = ParquetFileReader(
#     path="s3://your-bucket/path/to/data.parquet",
#     storage_options={"key": "YOUR_ACCESS_KEY", "secret": "YOUR_SECRET_KEY"}
# )
# df_s3 = s3_reader.to_pandas()
# print("Data read from S3:")
# print(df_s3.head())
```

## 3. SQL Integration

`flowerpower-io` provides robust integration with SQL databases, including advanced features for querying and data manipulation.

### DuckDB Integration

Leverage DuckDB for in-process analytical processing with SQL. `flowerpower-io` can read directly into or write from DuckDB.

```python
import duckdb
import pandas as pd
from flowerpower_io.loader import DuckDBReader
from flowerpower_io.saver import DuckDBWriter
import os

# Create a dummy DuckDB file for demonstration
db_path = "my_duckdb.db"
conn = duckdb.connect(database=db_path, read_only=False)
conn.execute("CREATE TABLE users (id INTEGER, name VARCHAR)")
conn.execute("INSERT INTO users VALUES (1, 'Alice'), (2, 'Bob')")
conn.close()

# Read from DuckDB
duckdb_reader = DuckDBReader(path=db_path, table_name="users")
df_users = duckdb_reader.to_pandas()
print("Users from DuckDB:")
print(df_users)

# Write to DuckDB
new_users = pd.DataFrame({"id": [3, 4], "name": ["Charlie", "Diana"]})
duckdb_writer = DuckDBWriter(path=db_path, table_name="users")
duckdb_writer.write(data=new_users, if_exists="append") # Append new users

# Verify appended data
conn = duckdb.connect(database=db_path, read_only=True)
print("\nAll users after append:")
print(conn.execute("SELECT * FROM users").fetchdf())
conn.close()

# Clean up
os.remove(db_path)
```

### DataFusion Integration (via PyArrow)

`flowerpower-io` can work with data that DataFusion can process, often through PyArrow Tables. This allows for powerful query planning and execution.

```python
# from flowerpower_io.loader import ParquetFileReader
# from pyarrow import dataset as pa_dataset
# from datafusion import SessionContext

# # Assuming you have a Parquet file
# # parquet_reader = ParquetFileReader(path="path/to/your/large_data.parquet")
# # arrow_table = parquet_reader.to_pyarrow_table()

# # # Create a DataFusion context
# # ctx = SessionContext()
# # ctx.register_record_batches("my_table", [arrow_table.to_batches()])

# # # Execute a query using DataFusion
# # result = ctx.sql("SELECT COUNT(*) FROM my_table").collect()
# # print("Count from DataFusion query:", result)
```

## 4. Customizing I/O Behavior

- **Custom Schemas**: When writing, you can often provide a schema to ensure data types are correctly interpreted by the target system.
- **Error Handling**: Implement robust error handling around `flowerpower-io` calls to manage file not found errors, permission issues, or data conversion problems.
- **Logging**: Integrate `flowerpower-io` operations with your application's logging framework to monitor data flows and troubleshoot issues.

This section provides a glimpse into the advanced capabilities of `flowerpower-io`. By combining these features, you can build sophisticated and high-performance data processing solutions.