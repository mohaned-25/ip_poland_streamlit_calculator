from __future__ import annotations

from datetime import datetime

import pandas as pd


def result_to_dataframe(result: dict) -> pd.DataFrame:
    rows = []

    for key, value in result.items():
        rows.append({
            "Metric": key.replace("_", " ").title(),
            "Value": value
        })

    return pd.DataFrame(rows)


def make_quote_dataframe(
    product: str,
    inputs: dict,
    result: dict
) -> pd.DataFrame:
    rows = [
        {
            "Section": "Meta",
            "Field": "Product",
            "Value": product
        },
        {
            "Section": "Meta",
            "Field": "Generated at",
            "Value": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    ]

    rows += [
        {
            "Section": "Input",
            "Field": key,
            "Value": value
        }
        for key, value in inputs.items()
    ]

    rows += [
        {
            "Section": "Result",
            "Field": key,
            "Value": value
        }
        for key, value in result.items()
    ]

    return pd.DataFrame(rows)
