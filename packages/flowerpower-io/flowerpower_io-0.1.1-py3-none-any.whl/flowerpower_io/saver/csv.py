from msgspec import field

from ..base import BaseDatasetWriter, BaseFileWriter


# @attrs.define
class CSVFileWriter(BaseFileWriter, gc=False):
    """CSV file writer.

    This class is responsible for writing dataframes to CSV files.

    Examples:
        ```python
        writer = CSVFileWriter(path="data.csv")
        writer.write(df)
        ```
    """

    format: str = field(default="csv")


# @attrs.define
class CSVDatasetWriter(BaseDatasetWriter, gc=False):
    """CSV dataset writer.

    This class is responsible for writing dataframes to CSV dataset.

    Examples:
        ```python
        writer = CSVDatasetWriter("csv_data/")
        writer.write(df)
        ```

    """

    format: str = field(default="csv")
