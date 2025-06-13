from enum import Enum

class OutputFormat(Enum):
    """Enum for output file formats."""
    JSON = "json"
    CSV = "csv"
    JSON_AND_CSV = "json_and_csv"