import pandas as pd
import os

def read_file(path: str):
    """
    Reads a file and returns a pandas DataFrame.
    Supported formats: CSV, Excel, JSON, Parquet, TXT
    """
    ext = os.path.splitext(path)[-1].lower()

    if ext == ".csv":
        return pd.read_csv(path)
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(path)
    elif ext == ".json":
        return pd.read_json(path)
    elif ext == ".parquet":
        return pd.read_parquet(path)
    elif ext == ".txt":
        return pd.read_csv(path, delimiter="\t")
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def write_file(data, path: str):
    """
    Saves a pandas DataFrame to file.
    Supported formats: CSV, Excel, JSON, Parquet, TXT
    """
    ext = os.path.splitext(path)[-1].lower()

    if ext == ".csv":
        data.to_csv(path, index=False)
    elif ext in [".xls", ".xlsx"]:
        data.to_excel(path, index=False)
    elif ext == ".json":
        data.to_json(path, orient="records", indent=2)
    elif ext == ".parquet":
        data.to_parquet(path, index=False)
    elif ext == ".txt":
        data.to_csv(path, sep="\t", index=False)
    else:
        raise ValueError(f"Unsupported file format: {ext}")