from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
import pandas as pd

MIN_CELL_DEFAULT = 10


@dataclass
class FeatureConfig:
    min_cell: int = MIN_CELL_DEFAULT


def _to_key(value: Any) -> Any:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def map_value(
    series: Optional[pd.Series],
    labels: Optional[Dict[Any, str]],
    index: Optional[pd.Index] = None,
) -> pd.Series:
    if series is None:
        if index is None:
            return pd.Series(dtype=object)
        return pd.Series([None] * len(index), index=index)
    if labels is None:
        return pd.Series([None] * len(series), index=series.index)

    def mapper(value: Any) -> Optional[str]:
        key = _to_key(value)
        if key is None:
            return None
        label = labels.get(key)
        return label

    return series.map(mapper)


def age_bucket(age: Any) -> Optional[str]:
    if age is None or (isinstance(age, float) and np.isnan(age)):
        return None
    try:
        age_int = int(age)
    except (TypeError, ValueError):
        return None
    if age_int < 18:
        return None
    if age_int <= 24:
        return "18-24"
    if age_int <= 34:
        return "25-34"
    if age_int <= 44:
        return "35-44"
    if age_int <= 54:
        return "45-54"
    if age_int <= 64:
        return "55-64"
    return "65+"


def ideology_bucket(value: Any) -> Optional[str]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    try:
        value_int = int(value)
    except (TypeError, ValueError):
        return None
    if value_int == 99:
        return None
    if value_int <= 3:
        return "left"
    if value_int <= 6:
        return "center"
    return "right"


def urban_rural_bucket(code: Any) -> Optional[str]:
    if code is None or (isinstance(code, float) and np.isnan(code)):
        return None
    try:
        code_int = int(code)
    except (TypeError, ValueError):
        return None
    if code_int in {111, 112, 113}:
        return "urban"
    if code_int in {221, 222, 223, 224, 225}:
        return "rural/remote"
    return None


def normalize_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    if cleaned == "":
        return None
    return cleaned


def filter_missing(label: Optional[str], missing_tokens: Iterable[str]) -> Optional[str]:
    if label is None:
        return None
    lowered = label.lower()
    if any(token in lowered for token in missing_tokens):
        return None
    return label


def apply_privacy_filter(df: pd.DataFrame, fields: List[str], min_cell: int) -> pd.DataFrame:
    filtered = df.copy()
    for field in fields:
        counts = filtered[field].value_counts(dropna=True)
        rare_values = set(counts[counts < min_cell].index)
        if not rare_values:
            continue
        filtered[field] = filtered[field].apply(
            lambda value: "Other" if value in rare_values else value
        )
    return filtered


def build_features(df: pd.DataFrame, labels: Dict[str, Any], config: FeatureConfig | None = None) -> pd.DataFrame:
    if config is None:
        config = FeatureConfig()

    values = labels.get("values", {})

    gender = map_value(df.get("H1"), values.get("H1"), index=df.index)
    gender = gender.map(lambda v: normalize_text(v))

    age_source = df.get("H3c")
    if age_source is None:
        age_source = df.get("mage")
    age = age_source.map(age_bucket)

    ethnicity = map_value(df.get("methnic"), values.get("methnic"), index=df.index)
    ethnicity = ethnicity.map(lambda v: filter_missing(normalize_text(v), ["unknown"]))

    education = map_value(df.get("meducate"), values.get("meducate"), index=df.index)
    education = education.map(lambda v: normalize_text(v))

    housing = map_value(df.get("H22"), values.get("H22"), index=df.index)
    housing = housing.map(lambda v: normalize_text(v))

    urban_rural = df.get("murbrur")
    if urban_rural is not None:
        urban_rural = urban_rural.map(urban_rural_bucket)

    party_vote = map_value(df.get("mvpartyvote"), values.get("mvpartyvote"), index=df.index)
    party_vote = party_vote.map(lambda v: filter_missing(normalize_text(v), ["missing", "dk"]))

    ideology = df.get("B6")
    if ideology is not None:
        ideology = ideology.map(ideology_bucket)

    out = pd.DataFrame(
        {
            "respondent_id": df.get("amcase").astype(str),
            "age_bucket": age,
            "gender": gender,
            "ethnicity": ethnicity,
            "education": education,
            "housing": housing,
            "urban_rural": urban_rural,
            "party_vote": party_vote,
            "ideology": ideology,
        }
    )

    # Drop rows without an id
    out = out.dropna(subset=["respondent_id"]).copy()

    categorical_fields = [
        "gender",
        "ethnicity",
        "education",
        "housing",
        "urban_rural",
        "party_vote",
        "ideology",
    ]

    out = apply_privacy_filter(out, categorical_fields, config.min_cell)

    return out
