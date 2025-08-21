# Quickstart

This guide will help you get started with `flowerpower-io` by demonstrating a simple data loading and saving workflow. We'll cover loading data from a JSON file and saving it to a CSV file.

## 1. Prepare Your Data

First, let's create a sample JSON file that we'll use for loading. Save the following content to a file named `sample_data.json` in your project directory:

```json
[
  {
    "id": 1,
    "name": "Alice",
    "age": 30,
    "city": "New York"
  },
  {
    "id": 2,
    "name": "Bob",
    "age": 24,
    "city": "London"
  },
  {
    "id": 3,
    "name": "Charlie",
    "age": 35,
    "city": "Paris"
  }
]
```

## 2. Load Data from JSON

Now, let's use `JsonFileReader` to load this data into a Pandas DataFrame.

```python
import pandas as pd
from flowerpower_io.loader import JsonFileReader
import os

# Define the path to your sample JSON file
json_file_path = "sample_data.json"

# Create a dummy JSON file for demonstration if it doesn't exist
# In a real scenario, this file would already exist.
if not os.path.exists(json_file_path):
    with open(json_file_path, "w") as f:
        f.write('''
[
  {
    "id": 1,
    "name": "Alice",
    "age": 30,
    "city": "New York"
  },
  {
    "id": 2,
    "name": "Bob",
    "age": 24,
    "city": "London"
  },
  {
    "id": 3,
    "name": "Charlie",
    "age": 35,
    "city": "Paris"
  }
]
''')

# Initialize JsonFileReader
json_reader = JsonFileReader(path=json_file_path)

# Load data into a Pandas DataFrame
df = json_reader.to_pandas()

print("Data loaded from JSON:")
print(df.head())
```

## 3. Save Data to CSV

Next, we'll use `CSVFileWriter` to save the loaded DataFrame to a new CSV file.

```python
from flowerpower_io.saver import CSVFileWriter

# Define the output CSV file path
output_csv_path = "output_data.csv"

# Initialize CSVFileWriter
csv_writer = CSVFileWriter(path=output_csv_path)

# Write the DataFrame to CSV
csv_writer.write(data=df)

print(f"\nData successfully saved to {output_csv_path}")

# Optional: Verify the content of the saved CSV
with open(output_csv_path, 'r') as f:
    print("\nContent of the saved CSV file:")
    print(f.read())

# Clean up the dummy files (optional for your actual project)
os.remove(json_file_path)
os.remove(output_csv_path)
print(f"\nCleaned up {json_file_path} and {output_csv_path}")
```

This quickstart demonstrated a basic workflow of loading data from JSON and saving it to CSV using `flowerpower-io`. You can explore more advanced features and other supported formats in the [Examples](examples.md) and [API Reference](api/index.md) sections.