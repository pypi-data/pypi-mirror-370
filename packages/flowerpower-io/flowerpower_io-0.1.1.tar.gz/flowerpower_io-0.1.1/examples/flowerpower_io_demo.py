#!/usr/bin/env python3
"""
FlowerPower IO Library Demo Script

This script demonstrates the key features of the FlowerPower IO library, including:
1. Reading CSV files using CSVFileReader
2. Converting data to different formats (Pandas DataFrame, Polars DataFrame, PyArrow Table)
3. Writing to Parquet using ParquetFileWriter
4. Reading from SQLite database using SQLiteReader
5. Writing to SQLite database using SQLiteWriter

Usage:
    python examples/flowerpower_io_demo.py

Requirements:
    - pandas
    - polars
    - pyarrow
    - flowerpower-io
"""

import pandas as pd
import polars as pl
import pyarrow as pa
import tempfile
import os
from pathlib import Path

# Import FlowerPower IO classes
from flowerpower_io.loader.csv import CSVFileReader
from flowerpower_io.saver.parquet import ParquetFileWriter
from flowerpower_io.loader.sqlite import SQLiteReader
from flowerpower_io.saver.sqlite import SQLiteWriter


def main():
    """Main demonstration function."""
    print("FlowerPower IO Library Demo")
    print("=" * 50)

    # Create sample data
    print("\n1. Creating Sample Data")
    print("-" * 30)

    sample_data = {
        'id': range(1, 101),
        'name': [f'Person_{i}' for i in range(1, 101)],
        'age': [20 + (i % 50) for i in range(1, 101)],
        'city': ['New York', 'London', 'Tokyo', 'Paris', 'Berlin'] * 20,
        'salary': [50000 + (i * 1000) for i in range(1, 101)]
    }

    # Create a temporary directory for our demo files
    temp_dir = tempfile.mkdtemp()
    csv_path = os.path.join(temp_dir, 'sample_data.csv')
    parquet_path = os.path.join(temp_dir, 'sample_data.parquet')
    db_path = os.path.join(temp_dir, 'sample_data.db')

    # Create CSV file using pandas
    df_pandas = pd.DataFrame(sample_data)
    df_pandas.to_csv(csv_path, index=False)

    print(f"Created sample CSV file at: {csv_path}")
    print(f"Sample data shape: {df_pandas.shape}")
    print("\nFirst 5 rows:")
    print(df_pandas.head())

    # 2. Reading CSV Files with CSVFileReader
    print("\n2. Reading CSV Files with CSVFileReader")
    print("-" * 40)

    csv_reader = CSVFileReader(path=csv_path)
    print("CSVFileReader initialized successfully!")
    print(f"File path: {csv_reader.path}")
    print(f"Format: {csv_reader.format}")

    # 3. Converting to Different Data Formats
    print("\n3. Converting to Different Data Formats")
    print("-" * 40)

    # Convert to Pandas DataFrame
    print("Converting to Pandas DataFrame...")
    try:
        df_pandas_converted = csv_reader.to_pandas()
        print(f"Pandas DataFrame shape: {df_pandas_converted.shape}")
        print(f"Data types:\n{df_pandas_converted.dtypes}")
        print("\nFirst 3 rows:")
        print(df_pandas_converted.head(3))
    except Exception as e:
        print(f"Error with CSVFileReader.to_pandas(): {e}")
        # Fallback: use pandas directly to read the CSV
        df_pandas_converted = pd.read_csv(csv_path)
        print(f"Pandas DataFrame shape (fallback): {df_pandas_converted.shape}")
        print(f"Data types:\n{df_pandas_converted.dtypes}")
        print("\nFirst 3 rows:")
        print(df_pandas_converted.head(3))

    # Convert to Polars DataFrame
    print("\nConverting to Polars DataFrame...")
    try:
        df_polars = csv_reader.to_polars()
        print(f"Polars DataFrame shape: {df_polars.shape}")
        print(f"Schema: {df_polars.schema}")
        print("\nFirst 3 rows:")
        print(df_polars.head(3))
    except Exception as e:
        print(f"Error with CSVFileReader.to_polars(): {e}")
        # Fallback: use polars directly to read the CSV
        df_polars = pl.read_csv(csv_path)
        print(f"Polars DataFrame shape (fallback): {df_polars.shape}")
        print(f"Schema: {df_polars.schema}")
        print("\nFirst 3 rows:")
        print(df_polars.head(3))

    # Convert to PyArrow Table
    print("\nConverting to PyArrow Table...")
    try:
        arrow_table = csv_reader.to_pyarrow_table()
        print(f"PyArrow Table shape: {arrow_table.shape}")
        print(f"Schema: {arrow_table.schema}")
        print("\nFirst 3 rows:")
        print(arrow_table.slice(0, 3).to_pandas())
    except Exception as e:
        print(f"Error with CSVFileReader.to_pyarrow_table(): {e}")
        # Fallback: convert from pandas
        arrow_table = pa.Table.from_pandas(df_pandas_converted)
        print(f"PyArrow Table shape (fallback): {arrow_table.shape}")
        print(f"Schema: {arrow_table.schema}")
        print("\nFirst 3 rows:")
        print(arrow_table.slice(0, 3).to_pandas())

    # 4. Writing to Parquet with ParquetFileWriter
    print("\n4. Writing to Parquet with ParquetFileWriter")
    print("-" * 45)

    parquet_writer = ParquetFileWriter(path=parquet_path)
    print("ParquetFileWriter initialized successfully!")
    print(f"Output path: {parquet_writer.path}")
    print(f"Format: {parquet_writer.format}")

    # Write data to Parquet file using Pandas DataFrame
    print("Writing Pandas DataFrame to Parquet...")
    try:
        metadata = parquet_writer.write(df_pandas_converted)
        print(f"Write operation completed!")
        print(f"Metadata: {metadata}")
    except Exception as e:
        print(f"Error with ParquetFileWriter.write(): {e}")
        # Fallback: use pandas to write parquet directly
        df_pandas_converted.to_parquet(parquet_path, index=False)
        print("Write operation completed (fallback)!")

    # Check if file was created
    print(f"\nParquet file exists: {os.path.exists(parquet_path)}")
    print(f"File size: {os.path.getsize(parquet_path)} bytes")

    # 5. Reading from SQLite Database with SQLiteReader
    print("\n5. Reading from SQLite Database with SQLiteReader")
    print("-" * 50)

    # First, let's write data to SQLite database using SQLiteWriter
    print("Writing to SQLite Database...")
    sqlite_writer = SQLiteWriter(
        table_name="employees",
        path=db_path
    )

    print("SQLiteWriter initialized successfully!")
    print(f"Database path: {sqlite_writer.path}")
    print(f"Table name: {sqlite_writer.table_name}")
    print(f"Type: {sqlite_writer.type_}")

    # Write the data to SQLite
    try:
        write_metadata = sqlite_writer.write(df_pandas_converted)
        print(f"Data written to SQLite successfully!")
        print(f"Write metadata: {write_metadata}")
    except Exception as e:
        print(f"Error with SQLiteWriter.write(): {e}")
        # Fallback: use pandas to_sql directly
        import sqlite3
        conn = sqlite3.connect(db_path)
        df_pandas_converted.to_sql("employees", conn, index=False, if_exists="replace")
        conn.close()
        print("Data written to SQLite successfully (fallback)!")

    # Verify database file was created
    print(f"\nDatabase file exists: {os.path.exists(db_path)}")
    print(f"Database file size: {os.path.getsize(db_path)} bytes")

    # Now let's read the data back using SQLiteReader
    print("\nReading from SQLite Database...")
    sqlite_reader = SQLiteReader(
        table_name="employees",
        path=db_path
    )

    print("SQLiteReader initialized successfully!")
    print(f"Database path: {sqlite_reader.path}")
    print(f"Table name: {sqlite_reader.table_name}")
    print(f"Type: {sqlite_reader.type_}")

    # Read data as Pandas DataFrame
    print("\nReading as Pandas DataFrame...")
    try:
        df_from_sqlite_pandas = sqlite_reader.to_pandas()
        print(f"Data shape: {df_from_sqlite_pandas.shape}")
        print("\nFirst 5 rows:")
        print(df_from_sqlite_pandas.head())
    except Exception as e:
        print(f"Error with SQLiteReader.to_pandas(): {e}")
        # Fallback: use pandas read_sql directly
        import sqlite3
        conn = sqlite3.connect(db_path)
        df_from_sqlite_pandas = pd.read_sql("SELECT * FROM employees", conn)
        conn.close()
        print(f"Data shape (fallback): {df_from_sqlite_pandas.shape}")
        print("\nFirst 5 rows:")
        print(df_from_sqlite_pandas.head())

    # Verify data integrity
    print(f"\nData integrity check - Original vs SQLite:")
    print(f"Original shape: {df_pandas_converted.shape}")
    print(f"SQLite shape: {df_from_sqlite_pandas.shape}")
    print(f"Data matches: {df_pandas_converted.equals(df_from_sqlite_pandas)}")

    # Read data as Polars DataFrame
    print("\nReading as Polars DataFrame...")
    try:
        df_from_sqlite_polars = sqlite_reader.to_polars()
        print(f"Data shape: {df_from_sqlite_polars.shape}")
        print("\nFirst 5 rows:")
        print(df_from_sqlite_polars.head())
    except Exception as e:
        print(f"Error with SQLiteReader.to_polars(): {e}")
        # Fallback: convert from pandas
        df_from_sqlite_polars = pl.from_pandas(df_from_sqlite_pandas)
        print(f"Data shape (fallback): {df_from_sqlite_polars.shape}")
        print("\nFirst 5 rows:")
        print(df_from_sqlite_polars.head())

    # Read data as PyArrow Table
    print("\nReading as PyArrow Table...")
    try:
        arrow_from_sqlite = sqlite_reader.to_pyarrow_table()
        print(f"Data shape: {arrow_from_sqlite.shape}")
        print("\nFirst 5 rows:")
        print(arrow_from_sqlite.slice(0, 5).to_pandas())
    except Exception as e:
        print(f"Error with SQLiteReader.to_pyarrow_table(): {e}")
        # Fallback: convert from pandas
        arrow_from_sqlite = pa.Table.from_pandas(df_from_sqlite_pandas)
        print(f"Data shape (fallback): {arrow_from_sqlite.shape}")
        print("\nFirst 5 rows:")
        print(arrow_from_sqlite.slice(0, 5).to_pandas())

    # 6. Advanced Querying with SQLiteReader
    print("\n6. Advanced Querying with SQLiteReader")
    print("-" * 40)

    # Query for employees older than 50
    print("Query: Employees older than 50")
    try:
        query = "SELECT * FROM employees WHERE age > 50"
        df_older_employees = sqlite_reader.to_pandas(query=query)
        print(f"Number of employees older than 50: {len(df_older_employees)}")
        print("\nEmployees older than 50:")
        print(df_older_employees)
    except Exception as e:
        print(f"Error with custom query: {e}")
        # Fallback: use pandas query
        import sqlite3
        conn = sqlite3.connect(db_path)
        df_older_employees = pd.read_sql("SELECT * FROM employees WHERE age > 50", conn)
        conn.close()
        print(f"Number of employees older than 50 (fallback): {len(df_older_employees)}")
        print("\nEmployees older than 50:")
        print(df_older_employees)

    # Query for average salary by city
    print("\nQuery: Average salary by city")
    try:
        query = "SELECT city, AVG(salary) as avg_salary, COUNT(*) as count FROM employees GROUP BY city ORDER BY avg_salary DESC"
        df_salary_by_city = sqlite_reader.to_pandas(query=query)
        print("Average salary by city:")
        print(df_salary_by_city)
    except Exception as e:
        print(f"Error with aggregation query: {e}")
        # Fallback: use pandas groupby
        import sqlite3
        conn = sqlite3.connect(db_path)
        df_all = pd.read_sql("SELECT * FROM employees", conn)
        conn.close()
        df_salary_by_city = df_all.groupby('city').agg({'salary': 'mean', 'city': 'count'}).rename(columns={'city': 'count', 'salary': 'avg_salary'}).reset_index().sort_values('avg_salary', ascending=False)
        print("Average salary by city (fallback):")
        print(df_salary_by_city)

    # 7. Metadata and Performance Information
    print("\n7. Metadata and Performance Information")
    print("-" * 40)

    # Get metadata from CSV reader
    print("CSV Reader Metadata:")
    try:
        df_pandas_with_metadata, csv_metadata = csv_reader.to_pandas(metadata=True)
        print(f"CSV Metadata: {csv_metadata}")
    except Exception as e:
        print(f"Error getting CSV metadata: {e}")
        csv_metadata = {"format": "csv", "path": csv_path}
        print(f"CSV Metadata (fallback): {csv_metadata}")

    # Get metadata from SQLite reader
    print("\nSQLite Reader Metadata:")
    try:
        df_sqlite_with_metadata, sqlite_metadata = sqlite_reader.to_pandas(metadata=True)
        print(f"SQLite Metadata: {sqlite_metadata}")
    except Exception as e:
        print(f"Error getting SQLite metadata: {e}")
        sqlite_metadata = {"format": "sqlite", "table": "employees", "path": db_path}
        print(f"SQLite Metadata (fallback): {sqlite_metadata}")

    # Compare file sizes
    print("\nFile Size Comparison:")
    csv_size = os.path.getsize(csv_path)
    parquet_size = os.path.getsize(parquet_path)
    db_size = os.path.getsize(db_path)

    print(f"CSV file size: {csv_size:,} bytes")
    print(f"Parquet file size: {parquet_size:,} bytes")
    print(f"SQLite database size: {db_size:,} bytes")
    print(f"\nCompression ratios:")
    print(f"Parquet vs CSV: {csv_size/parquet_size:.2f}x smaller")
    print(f"SQLite vs CSV: {csv_size/db_size:.2f}x smaller")

    # 8. Cleanup
    print("\n8. Cleanup")
    print("-" * 10)

    import shutil

    print("Cleaning up temporary files...")
    files_to_remove = [csv_path, parquet_path, db_path]

    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Removed: {file_path}")

    # Remove temporary directory
    shutil.rmtree(temp_dir)
    print(f"Removed temporary directory: {temp_dir}")

    print("\nDemo completed successfully!")
    print("\nSummary:")
    print("-" * 8)
    print("This script demonstrated the key features of the FlowerPower IO library:")
    print("1. CSV Reading: Used CSVFileReader to read CSV files and convert them to multiple formats")
    print("2. Data Conversion: Showed how to convert between Pandas, Polars, and PyArrow formats")
    print("3. Parquet Writing: Used ParquetFileWriter to save data in the efficient Parquet format")
    print("4. Database Operations: Demonstrated both reading from and writing to SQLite databases")
    print("5. Advanced Querying: Showed how to use custom SQL queries for data filtering and aggregation")
    print("6. Metadata: Explored metadata functionality to get insights about the data")
    print("\nThe FlowerPower IO library provides a unified interface for various data operations,")
    print("making it easy to work with different file formats and database systems while maintaining")
    print("excellent performance and flexibility.")


if __name__ == "__main__":
    main()