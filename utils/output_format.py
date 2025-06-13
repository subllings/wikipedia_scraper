"""
Defines the OutputFormat enumeration for specifying supported export formats.

This module provides an Enum class used to indicate the desired output file format
when exporting data from the scraper or other processing pipelines.
The supported formats are:
- JSON: for structured data (e.g. API-compatible)
- CSV: for tabular data
- JSON_AND_CSV: for exporting in both formats simultaneously
"""
from enum import Enum


class OutputFormat(Enum):
    """
    Enum for output file formats.

    """
    JSON = "json"
    CSV = "csv"
    JSON_AND_CSV = "json_and_csv"
