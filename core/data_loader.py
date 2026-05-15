from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


@lru_cache(maxsize=4)
def load_materials() -> dict:
    with open(DATA_DIR / "materials_catalog() -> dict:    with open(DATA_DIR / "materials.json", "r", encoding="utf-8") as f:
    formula_file = DATA_DIR / "formula_catalog.json"

    if not formula_file.exists():
        return {
            "source": "Not uploaded yet",
            "total_formulas": 0,
            "sheet_stats": [],
            "formulas": []
        }

    with open(formula_file, "r", encoding="utf-8") as f:
        return json.load(f)


def paper_options() -> list[str]:
    return list(load_materials()["paper_types"].keys())


def get_paper(name: str) -> dict:
    papers = load_materials()["paper_types"]

    if name not in papers:
        raise KeyError(f"Unknown paper/material type: {name}")

    return papers[name]
        return json.load(f)


@lru_cache(maxsize=2)
