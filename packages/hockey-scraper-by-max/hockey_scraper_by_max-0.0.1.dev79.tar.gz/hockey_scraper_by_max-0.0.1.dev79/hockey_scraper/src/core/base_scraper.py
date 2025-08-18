# hockey_scraper/src/core/base_scraper.py
# Base class for all scrapers in the hockey scraper project
# This file contains the BaseScraper class which provides common functionality for all scrapers.

import pandas as pd
import polars as pl
from typing import List, Dict, Any, Union

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def convert_to_dataframe(data: Union[Dict, List], format="pandas"):
    """
    Convert data to a DataFrame in the specified format.

    Args:
        data (list or dict): The data to convert.
        format (str): The format of the DataFrame ('pandas' or 'polars').

    Returns:
        pd.DataFrame or pl.DataFrame: The converted DataFrame.
    """

    if isinstance(data, dict):
        if format == "pandas":
            return pd.DataFrame.from_dict(data, orient="index").reset_index()
        elif format == "polars":
            return pl.DataFrame(data)
    elif isinstance(data, list):
        if format == "pandas":
            return pd.json_normalize(data, sep=".").reset_index(drop=True)
        elif format == "polars":
            return pl.json_normalize(data, separator=".")
    else:
        raise ValueError("Data must be a list or a dictionary.")
