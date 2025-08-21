from msgspec import field

from ..base import BaseDatasetReader


# @attrs.define
class PydalaDatasetReader(BaseDatasetReader, gc=False):
    """Pydala dataset loader.

    This class is responsible for loading dataframes from Pydala dataset.

    Examples:
        ```python
        loader = PydalaDatasetReader("pydala_data/")
        df = df = loader.to_polars()
        # or
        # df = loader.to_pandas()
        # df = loader.to_pyarrow_table()
        # df = loader.to_duckdb()
        ```
    """

    format: str = field(default="parquet")
