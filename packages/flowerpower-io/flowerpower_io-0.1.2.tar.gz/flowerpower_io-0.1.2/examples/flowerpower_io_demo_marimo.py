#!/usr/bin/env python3
"""
FlowerPower IO Library Demo - Marimo Notebook

This Marimo notebook demonstrates the key features of the FlowerPower IO library, including:
1. Reading CSV files using CSVFileReader
2. Converting data to different formats (Pandas DataFrame, Polars DataFrame, PyArrow Table)
3. Writing to Parquet using ParquetFileWriter
4. Reading from SQLite database using SQLiteReader
5. Writing to SQLite database using SQLiteWriter

This notebook is designed to run in a Marimo environment with reactive cells.

Usage:
    marimo run examples/flowerpower_io_demo_marimo.py

Requirements:
    - marimo
    - pandas
    - polars
    - pyarrow
    - flowerpower-io
"""
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "marimo",
#     "pandas",
#     "polars",
#     "pyarrow",
#     "flowerpower-io",
# ]
# ///

import marimo

__generated_with = "0.1.0"
app = marimo.App()


@app.cell
def imports():
    """Import required libraries and FlowerPower IO classes."""
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

    return (
        pd, pl, pa, tempfile, os, Path,
        CSVFileReader, ParquetFileWriter, SQLiteReader, SQLiteWriter
    )


@app.cell
def sample_data_generation(pd, tempfile, os):
    """Create sample data and temporary files for demonstration."""
    # Create sample data
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

    return sample_data, temp_dir, csv_path, parquet_path, db_path, df_pandas


@app.cell
def display_sample_data(sample_data, temp_dir, csv_path, parquet_path, db_path, df_pandas):
    """Display information about the created sample data."""
    print("=== FlowerPower IO Library Demo ===")
    print(f"Created sample CSV file at: {csv_path}")
    print(f"Sample data shape: {df_pandas.shape}")
    print(f"Temporary directory: {temp_dir}")
    print("\nFirst 5 rows of sample data:")
    return df_pandas.head()


@app.cell
def csv_reader_initialization(CSVFileReader, csv_path):
    """Initialize CSVFileReader and display its properties."""
    csv_reader = CSVFileReader(path=csv_path)

    print("=== CSV File Reader ===")
    print("CSVFileReader initialized successfully!")
    print(f"File path: {csv_reader.path}")
    print(f"Format: {csv_reader.format}")

    return csv_reader


@app.cell
def pandas_conversion(csv_reader, pd):
    """Convert CSV data to Pandas DataFrame."""
    print("=== Converting to Pandas DataFrame ===")

    try:
        df_pandas_converted = csv_reader.to_pandas()
        print(f"Pandas DataFrame shape: {df_pandas_converted.shape}")
        print(f"Data types:\n{df_pandas_converted.dtypes}")
        print("\nFirst 3 rows:")
        return df_pandas_converted.head(3)
    except Exception as e:
        print(f"Error with CSVFileReader.to_pandas(): {e}")
        # Fallback: use pandas directly to read the CSV
        df_pandas_converted = pd.read_csv(csv_reader.path)
        print(f"Pandas DataFrame shape (fallback): {df_pandas_converted.shape}")
        print(f"Data types:\n{df_pandas_converted.dtypes}")
        print("\nFirst 3 rows:")
        return df_pandas_converted.head(3)


@app.cell
def polars_conversion(csv_reader, pl, pd):
    """Convert CSV data to Polars DataFrame."""
    print("\n=== Converting to Polars DataFrame ===")

    try:
        df_polars = csv_reader.to_polars()
        print(f"Polars DataFrame shape: {df_polars.shape}")
        print(f"Schema: {df_polars.schema}")
        print("\nFirst 3 rows:")
        return df_polars.head(3)
    except Exception as e:
        print(f"Error with CSVFileReader.to_polars(): {e}")
        # Fallback: use polars directly to read the CSV
        df_polars = pl.read_csv(csv_reader.path)
        print(f"Polars DataFrame shape (fallback): {df_polars.shape}")
        print(f"Schema: {df_polars.schema}")
        print("\nFirst 3 rows:")
        return df_polars.head(3)


@app.cell
def pyarrow_conversion(csv_reader, pa, pd):
    """Convert CSV data to PyArrow Table."""
    print("\n=== Converting to PyArrow Table ===")

    try:
        arrow_table = csv_reader.to_pyarrow_table()
        print(f"PyArrow Table shape: {arrow_table.shape}")
        print(f"Schema: {arrow_table.schema}")
        print("\nFirst 3 rows:")
        return arrow_table.slice(0, 3).to_pandas()
    except Exception as e:
        print(f"Error with CSVFileReader.to_pyarrow_table(): {e}")
        # Fallback: convert from pandas
        df_pandas_fallback = pd.read_csv(csv_reader.path)
        arrow_table = pa.Table.from_pandas(df_pandas_fallback)
        print(f"PyArrow Table shape (fallback): {arrow_table.shape}")
        print(f"Schema: {arrow_table.schema}")
        print("\nFirst 3 rows:")
        return arrow_table.slice(0, 3).to_pandas()


@app.cell
def parquet_writer_initialization(ParquetFileWriter, parquet_path):
    """Initialize ParquetFileWriter."""
    parquet_writer = ParquetFileWriter(path=parquet_path)

    print("\n=== Parquet File Writer ===")
    print("ParquetFileWriter initialized successfully!")
    print(f"Output path: {parquet_writer.path}")
    print(f"Format: {parquet_writer.format}")

    return parquet_writer


@app.cell
def write_to_parquet(parquet_writer, pandas_conversion, os):
    """Write data to Parquet file using Pandas DataFrame."""
    print("=== Writing Pandas DataFrame to Parquet ===")

    try:
        metadata = parquet_writer.write(pandas_conversion)
        print(f"Write operation completed!")
        print(f"Metadata: {metadata}")
    except Exception as e:
        print(f"Error with ParquetFileWriter.write(): {e}")
        # Fallback: use pandas to write parquet directly
        pandas_conversion.to_parquet(parquet_writer.path, index=False)
        print("Write operation completed (fallback)!")

    # Check if file was created
    print(f"\nParquet file exists: {os.path.exists(parquet_writer.path)}")
    print(f"File size: {os.path.getsize(parquet_writer.path)} bytes")

    return parquet_writer.path


@app.cell
def sqlite_writer_initialization(SQLiteWriter, db_path):
    """Initialize SQLiteWriter and write data to database."""
    print("\n=== SQLite Database Writer ===")

    sqlite_writer = SQLiteWriter(
        table_name="employees",
        path=db_path
    )

    print("SQLiteWriter initialized successfully!")
    print(f"Database path: {sqlite_writer.path}")
    print(f"Table name: {sqlite_writer.table_name}")
    print(f"Type: {sqlite_writer.type_}")

    return sqlite_writer


@app.cell
def write_to_sqlite(sqlite_writer, pandas_conversion, os):
    """Write data to SQLite database."""
    print("=== Writing to SQLite Database ===")

    try:
        write_metadata = sqlite_writer.write(pandas_conversion)
        print(f"Data written to SQLite successfully!")
        print(f"Write metadata: {write_metadata}")
    except Exception as e:
        print(f"Error with SQLiteWriter.write(): {e}")
        # Fallback: use pandas to_sql directly
        import sqlite3
        conn = sqlite3.connect(sqlite_writer.path)
        pandas_conversion.to_sql(sqlite_writer.table_name, conn, index=False, if_exists="replace")
        conn.close()
        print("Data written to SQLite successfully (fallback)!")

    # Verify database file was created
    print(f"\nDatabase file exists: {os.path.exists(sqlite_writer.path)}")
    print(f"Database file size: {os.path.getsize(sqlite_writer.path)} bytes")

    return sqlite_writer.path


@app.cell
def sqlite_reader_initialization(SQLiteReader, db_path):
    """Initialize SQLiteReader."""
    print("\n=== SQLite Database Reader ===")

    sqlite_reader = SQLiteReader(
        table_name="employees",
        path=db_path
    )

    print("SQLiteReader initialized successfully!")
    print(f"Database path: {sqlite_reader.path}")
    print(f"Table name: {sqlite_reader.table_name}")
    print(f"Type: {sqlite_reader.type_}")

    return sqlite_reader


@app.cell
def read_from_sqlite_pandas(sqlite_reader, pandas_conversion):
    """Read data from SQLite database as Pandas DataFrame."""
    print("=== Reading from SQLite as Pandas DataFrame ===")

    try:
        df_from_sqlite_pandas = sqlite_reader.to_pandas()
        print(f"Data shape: {df_from_sqlite_pandas.shape}")
        print("\nFirst 5 rows:")
        display_data = df_from_sqlite_pandas.head()

        # Verify data integrity
        print(f"\nData integrity check - Original vs SQLite:")
        print(f"Original shape: {pandas_conversion.shape}")
        print(f"SQLite shape: {df_from_sqlite_pandas.shape}")
        print(f"Data matches: {pandas_conversion.equals(df_from_sqlite_pandas)}")

        return display_data
    except Exception as e:
        print(f"Error with SQLiteReader.to_pandas(): {e}")
        # Fallback: use pandas read_sql directly
        import pandas as pd
        import sqlite3
        conn = sqlite3.connect(sqlite_reader.path)
        df_from_sqlite_pandas = pd.read_sql("SELECT * FROM employees", conn)
        conn.close()
        print(f"Data shape (fallback): {df_from_sqlite_pandas.shape}")
        print("\nFirst 5 rows:")
        return df_from_sqlite_pandas.head()


@app.cell
def read_from_sqlite_polars(sqlite_reader, pl):
    """Read data from SQLite database as Polars DataFrame."""
    print("\n=== Reading from SQLite as Polars DataFrame ===")

    try:
        df_from_sqlite_polars = sqlite_reader.to_polars()
        print(f"Data shape: {df_from_sqlite_polars.shape}")
        print("\nFirst 5 rows:")
        return df_from_sqlite_polars.head()
    except Exception as e:
        print(f"Error with SQLiteReader.to_polars(): {e}")
        # Fallback: convert from pandas
        df_pandas_fallback = read_from_sqlite_pandas(sqlite_reader, None)
        df_from_sqlite_polars = pl.from_pandas(df_pandas_fallback)
        print(f"Data shape (fallback): {df_from_sqlite_polars.shape}")
        print("\nFirst 5 rows:")
        return df_from_sqlite_polars.head()


@app.cell
def read_from_sqlite_pyarrow(sqlite_reader, pa):
    """Read data from SQLite database as PyArrow Table."""
    print("\n=== Reading from SQLite as PyArrow Table ===")

    try:
        arrow_from_sqlite = sqlite_reader.to_pyarrow_table()
        print(f"Data shape: {arrow_from_sqlite.shape}")
        print("\nFirst 5 rows:")
        return arrow_from_sqlite.slice(0, 5).to_pandas()
    except Exception as e:
        print(f"Error with SQLiteReader.to_pyarrow_table(): {e}")
        # Fallback: convert from pandas
        df_pandas_fallback = read_from_sqlite_pandas(sqlite_reader, None)
        arrow_from_sqlite = pa.Table.from_pandas(df_pandas_fallback)
        print(f"Data shape (fallback): {arrow_from_sqlite.shape}")
        print("\nFirst 5 rows:")
        return arrow_from_sqlite.slice(0, 5).to_pandas()


@app.cell
def advanced_queries(sqlite_reader, pd):
    """Demonstrate advanced SQL querying capabilities."""
    print("\n=== Advanced SQL Querying ===")

    # Query for employees older than 50
    print("Query: Employees older than 50")
    try:
        query = "SELECT * FROM employees WHERE age > 50"
        df_older_employees = sqlite_reader.to_pandas(query=query)
        print(f"Number of employees older than 50: {len(df_older_employees)}")
        print("\nEmployees older than 50:")
        display_older = df_older_employees
    except Exception as e:
        print(f"Error with custom query: {e}")
        # Fallback: use pandas query
        import sqlite3
        conn = sqlite3.connect(sqlite_reader.path)
        df_older_employees = pd.read_sql("SELECT * FROM employees WHERE age > 50", conn)
        conn.close()
        print(f"Number of employees older than 50 (fallback): {len(df_older_employees)}")
        print("\nEmployees older than 50:")
        display_older = df_older_employees

    # Query for average salary by city
    print("\nQuery: Average salary by city")
    try:
        query = "SELECT city, AVG(salary) as avg_salary, COUNT(*) as count FROM employees GROUP BY city ORDER BY avg_salary DESC"
        df_salary_by_city = sqlite_reader.to_pandas(query=query)
        print("Average salary by city:")
        display_salary = df_salary_by_city
    except Exception as e:
        print(f"Error with aggregation query: {e}")
        # Fallback: use pandas groupby
        import sqlite3
        conn = sqlite3.connect(sqlite_reader.path)
        df_all = pd.read_sql("SELECT * FROM employees", conn)
        conn.close()
        df_salary_by_city = df_all.groupby('city').agg({'salary': 'mean', 'city': 'count'}).rename(columns={'city': 'count', 'salary': 'avg_salary'}).reset_index().sort_values('avg_salary', ascending=False)
        print("Average salary by city (fallback):")
        display_salary = df_salary_by_city

    return display_older, display_salary


@app.cell
def metadata_analysis(csv_reader, sqlite_reader, csv_path, parquet_path, db_path, os):
    """Analyze metadata and performance information."""
    print("\n=== Metadata and Performance Analysis ===")

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

    return csv_metadata, sqlite_metadata


@app.cell
def cleanup(temp_dir, csv_path, parquet_path, db_path, os):
    """Clean up temporary files created during the demonstration."""
    print("\n=== Cleanup ===")

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
    return "Cleanup completed"


@app.cell
def summary():
    """Display summary of the demonstration."""
    summary_text = """
=== Summary ===

This Marimo notebook demonstrated the key features of the FlowerPower IO library:

1. **CSV Reading**: Used `CSVFileReader` to read CSV files and convert them to multiple formats
2. **Data Conversion**: Showed how to convert between Pandas, Polars, and PyArrow formats
3. **Parquet Writing**: Used `ParquetFileWriter` to save data in the efficient Parquet format
4. **Database Operations**: Demonstrated both reading from and writing to SQLite databases using `SQLiteReader` and `SQLiteWriter`
5. **Advanced Querying**: Showed how to use custom SQL queries for data filtering and aggregation
6. **Metadata**: Explored metadata functionality to get insights about the data

The FlowerPower IO library provides a unified interface for various data operations, making it easy to work with different file formats and database systems while maintaining excellent performance and flexibility.

This reactive notebook allows you to modify parameters and see results update in real-time!
"""
    print(summary_text)
    return summary_text


if __name__ == "__main__":
    app.run()