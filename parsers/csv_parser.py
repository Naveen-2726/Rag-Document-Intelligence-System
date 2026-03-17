from pathlib import Path

import pandas as pd


def parse_csv(file_path: str | Path) -> str:
    """Extract CSV content as normalized plain text rows."""
    dataframe = pd.read_csv(file_path, dtype=str, keep_default_na=False)
    return dataframe.to_csv(index=False)