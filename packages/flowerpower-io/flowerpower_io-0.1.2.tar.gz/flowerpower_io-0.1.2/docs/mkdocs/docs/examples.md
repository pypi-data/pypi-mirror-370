# Examples

This section provides practical examples demonstrating various loading, saving, and conversion scenarios using `flowerpower-io`. These examples showcase the library's flexibility in handling different data formats and I/O operations.

## 1. Reading and Writing CSV Files

This example demonstrates how to read data from a CSV file into a Pandas DataFrame and then write it back to another CSV file.

```python
import pandas as pd
from flowerpower_io.loader import CSVFileReader
from flowerpower_io.saver import CSVFileWriter
import os

# Create a dummy CSV file for demonstration
sample_csv_content = """id,name,value
1,apple,10
2,banana,20
3,orange,15
"""
with open("sample.csv", "w") as f:
    f.write(sample_csv_content)

# Read from CSV
csv_reader = CSVFileReader(path="sample.csv")
df_from_csv = csv_reader.to_pandas()
print("Data read from sample.csv:")
print(df_from_csv)

# Write to CSV
output_csv_path = "output.csv"
csv_writer = CSVFileWriter(path=output_csv_path)
csv_writer.write(data=df_from_csv)
print(f"\nData written to {output_csv_path}")

# Clean up
os.remove("sample.csv")
os.remove(output_csv_path)
```

## 2. Parquet Operations with Data Conversion

This example illustrates reading a Parquet file into a Polars DataFrame and then writing a Polars DataFrame to a new Parquet file. It also shows conversion between data structures.

```python
import polars as pl
import pyarrow as pa
from flowerpower_io.loader import ParquetFileReader
from flowerpower_io.saver import ParquetFileWriter
import os

# Create a dummy Parquet file for demonstration
data_to_parquet = pl.DataFrame({
    "product": ["A", "B", "C"],
    "price": [1.99, 0.50, 2.75]
})
temp_parquet_path = "temp_products.parquet"
data_to_parquet.write_parquet(temp_parquet_path)

# Read from Parquet into Polars DataFrame
parquet_reader = ParquetFileReader(path=temp_parquet_path)
df_polars = parquet_reader.to_polars()
print("Data read from temp_products.parquet (Polars DataFrame):")
print(df_polars)

# Convert Polars DataFrame to PyArrow Table
arrow_table = df_polars.to_arrow()
print("\nConverted to PyArrow Table:")
print(arrow_table)

# Write PyArrow Table to a new Parquet file
output_parquet_path = "new_products.parquet"
parquet_writer = ParquetFileWriter(path=output_parquet_path)
parquet_writer.write(data=arrow_table)
print(f"\nPyArrow Table written to {output_parquet_path}")

# Clean up
os.remove(temp_parquet_path)
os.remove(output_parquet_path)
```

## 3. SQLite Database Interaction

Demonstrates writing a Pandas DataFrame to a SQLite database and then reading data back using a custom SQL query.

```python
import pandas as pd
from flowerpower_io.saver import SQLiteWriter
from flowerpower_io.loader import SQLiteReader
import os

db_file = "my_database.db"
table_name = "sales_data"

# Create a Pandas DataFrame
sales_data = pd.DataFrame({
    "region": ["East", "West", "North", "South"],
    "sales": [1000, 1500, 1200, 900],
    "quarter": [1, 1, 2, 2]
})

# Write to SQLite
sqlite_writer = SQLiteWriter(path=db_file, table_name=table_name)
sqlite_writer.write(data=sales_data, if_exists="replace") # Overwrite if table exists
print(f"Data written to SQLite database '{db_file}' in table '{table_name}'.")

# Read from SQLite with a custom query
sqlite_reader = SQLiteReader(path=db_file)
query = f"SELECT region, SUM(sales) as total_sales FROM {table_name} GROUP BY region ORDER BY total_sales DESC"
df_query_result = sqlite_reader.to_pandas(query=query)
print("\nTotal sales by region (from SQLite query):")
print(df_query_result)

# Clean up
os.remove(db_file)
```

## 4. Loading JSON Data with Metadata

This example shows how to load data from a JSON file and retrieve associated metadata during the process.

```python
from flowerpower_io.loader import JsonFileReader
import pandas as pd
import os

json_file = "user_profiles.json"
profiles_content = '''
[
  {"user_id": 1, "username": "alpha", "status": "active"},
  {"user_id": 2, "username": "beta", "status": "inactive"}
]
'''
with open(json_file, "w") as f:
    f.write(profiles_content)

json_reader = JsonFileReader(path=json_file)
df_profiles, metadata = json_reader.to_pandas(metadata=True)

print("User Profiles Data:")
print(df_profiles)
print("\nMetadata retrieved:")
print(metadata)

# Clean up
os.remove(json_file)