"""Define a generic files loader.

.. todo::
    I would need to set once and for all the imposed format. Without this I
    cannot do anything.

"""

from pathlib import Path

import pandas as pd

from eemilib.loader.loader import Loader


class PandasLoader(Loader):
    """Define the pandas loader."""

    def __init__(self) -> None:
        """Raise an error for now.

        Ideally, this loader should detect correct input and columns. But it is
        not for now.

        """

    def load_emission_yield(self, *filepath: str | Path) -> pd.DataFrame:
        """Load and format the given emission yield files.

        Parameters
        ----------
        filepath : str | Path
            Path(s) to file holding data under study.

        Returns
        -------
        data : pd.DataFrame
            Structure holding the data. Must have a ``Energy (eV)`` column
            holding PEs energy. And one or several columns ``theta [deg]``,
            where `theta` is the value of the incidence angle and content is
            corresponding emission yield.

        """
        data = [pd.read_csv(path) for path in filepath]
        data = pd.concat(data)
        return data
