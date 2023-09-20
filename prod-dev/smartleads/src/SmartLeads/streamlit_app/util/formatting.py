import humanize
import numpy as np
import pandas as pd


def int_space(x):
    """Format an integer with spaces between thousands.

    Args:
        x (int): The integer to format.

    Returns:
        str: The formatted integer."""
    return humanize.intcomma(x).replace(",", " ")


def human(x):
    try:
        if x > 1:
            return int_space(int(float(x)))
        elif x > 0:
            return f"{x:.2%}"
        elif x == 0:
            return "0"
        else:
            return int_space(int(float(x)))
    except TypeError:
        return x


def guess_humanize_from_series(series: pd.Series) -> pd.Series:
    """Guess the humanize type from the series.

    Args:
        series (pd.Series): Series to guess the humanize type from.

    Returns:
        pd.Series: Series with the humanize type guessed.
    """

    if series.dtype == np.int64:
        return series.apply(lambda x: humanize.intcomma(x, 0).replace(",", " "))
    elif (series.dtype == np.float64) and (series.max() > 2):
        return series.apply(
            lambda x: humanize.intcomma(int(float(x)), 0).replace(",", " ")
        )
    elif (series.dtype == np.float64) and (series.max() <= 2):
        return series.apply(lambda x: f"{x:.2%}")
    else:
        return series
