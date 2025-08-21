from msgspec import field

from ..base import BaseDatasetWriter, BaseFileWriter


# @attrs.define
class ParquetFileWriter(BaseFileWriter, gc=False):
    """Parquet file writer.

    This class is responsible for writing dataframes to Parquet files.

    Examples:
        ```python
        writer = ParquetFileWriter(path="data.parquet")
        writer.write(df) 
        ```
    """

    format: str = field(default="parquet")


# @attrs.define
class ParquetDatasetWriter(BaseDatasetWriter, gc=False):
    """Parquet dataset writer.

    This class is responsible for writing dataframes to Parquet dataset.

    Examples:
        ```python
        writer = ParquetDatasetWriter(path="parquet_data/")
        writer.write(df)
        ```

    """

    format: str = field(default="parquet")
