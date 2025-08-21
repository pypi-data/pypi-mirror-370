import sys
from typing import Optional

import pandas as pd
from datasets import Dataset, DatasetDict


def load_excel(file_path: str) -> Optional[DatasetDict]:
    try:
        all_sheets = pd.read_excel(file_path, sheet_name=None)
        datasets = {}

        for sheet_name, df in all_sheets.items():
            df = df.ffill().astype(str)
            datasets[sheet_name] = Dataset.from_pandas(df)

        return DatasetDict(datasets)
    except Exception as e:
        print(f"Error loading Excel dataset from {file_path}: {e}", file=sys.stderr)
        return None


if __name__ == "__main__":
    print(load_excel("./../../../testdata/person_info.xlsx"))
