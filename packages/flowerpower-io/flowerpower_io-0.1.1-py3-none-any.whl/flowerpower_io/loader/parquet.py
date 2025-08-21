from msgspec import field

from ..base import BaseDatasetReader, BaseFileReader


# @attrs.define
class ParquetFileReader(BaseFileReader, gc=False):
    """Parquet file loader.

    This class is responsible for loading dataframes from Parquet files.

    Examples:
        ```python
        loader = ParquetFileReader("data.parquet")
        df = loader.to_polars()
        # or
        # df = loader.to_pandas()
        # df = loader.to_pyarrow_table()
        # df = loader.to_duckdb()
        ```
    """

    format: str = field(default="parquet")


# @attrs.define
class ParquetDatasetReader(BaseDatasetReader, gc=False):
    """Parquet dataset loader.

    This class is responsible for loading dataframes from Parquet dataset.

    Examples:
        ```python
        loader = ParquetDatasetReader("parquet_data/")
        df = df = loader.to_polars()
        # or
        # df = loader.to_pandas()
        # df = loader.to_pyarrow_table()
        # df = loader.to_duckdb()
        ```
    """

    format: str = field(default="parquet")
