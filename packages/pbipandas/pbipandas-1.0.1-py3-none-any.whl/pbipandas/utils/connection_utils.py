import pandas as pd
import ast
from typing import Union


def extract_connection_details(x: Union[str, dict]) -> pd.Series:
    """
    Extract connection details from a stringified dictionary or a dictionary.

    Args:
        x (Union[str, dict]): The input value to extract connection details from.

    Returns:
        pd.Series: A series with connection details such as server, database, etc.
    """
    try:
        if isinstance(x, str):
            details = ast.literal_eval(x)
        elif isinstance(x, dict):
            details = x
        else:
            return pd.Series(
                [None] * 5,
                index=["server", "database", "connectionString", "url", "path"],
            )

        return pd.Series(
            {
                "server": details.get("server"),
                "database": details.get("database"),
                "connectionString": details.get("connectionString"),
                "url": details.get("url"),
                "path": details.get("path"),
            }
        )
    except Exception as e:
        print(f"Error parsing connectionDetails: {e}")
        return pd.Series(
            [None] * 5,
            index=["server", "database", "connectionString", "url", "path"],
        )
