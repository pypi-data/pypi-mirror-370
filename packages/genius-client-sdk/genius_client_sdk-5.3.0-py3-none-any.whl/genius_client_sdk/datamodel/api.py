from enum import Enum

type DictResponse = dict[str, str | dict | list]


class BinningStrategy(Enum):
    """
    Enumeration of binning strategies for automatic binning.

    Attributes:
        quantile: Bins have approximately the same number of observations.
        fixed_width: Bins have the same width.
        k_cluster: Bins are created by clustering the data.
    """

    quantile = "quantile"  # Bins have approximately the same number of observations.
    fixed_width = "fixed_width"  # Bins have the same width.
    k_cluster = "k_cluster"  # Bins are created by clustering the data.


class AutoBinVariable(dict):
    """
    Represents a variable for the automatic binning process.

    Attributes:
        binning_strategy (BinningStrategy): The strategy used for binning the variable.
        num_bins (int): The number of bins to create.
        x_column (str): The column name of the variable in the dataset.
    """

    binning_strategy: BinningStrategy
    num_bins: int
    x_column: str
