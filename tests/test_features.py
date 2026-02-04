import pandas as pd

from src.features import FeatureConfig, build_features


def test_build_features_and_privacy_filter():
    df = pd.DataFrame(
        {
            "amcase": [1, 2, 3],
            "H1": [1, 2, 1],
            "H3c": [23, 45, 70],
            "methnic": [3, 0, 0],
            "meducate": [4, 4, 1],
            "H22": [1, 3, 3],
            "murbrur": [111, 221, 111],
            "mvpartyvote": [1, 2, 2],
            "B6": [2, 7, 5],
        }
    )
    labels = {
        "values": {
            "H1": {1: "Male", 2: "Female"},
            "methnic": {0: "European", 3: "Māori"},
            "meducate": {1: "Level 1", 4: "University"},
            "H22": {1: "Own mortgage free", 3: "Rent privately"},
            "mvpartyvote": {1: "Labour", 2: "National"},
        }
    }

    features = build_features(df, labels, FeatureConfig(min_cell=2))

    # Rare categories should be grouped into Other
    assert "Other" in features["ethnicity"].values
    assert "Other" in features["housing"].values

    # Age buckets should be derived
    assert set(features["age_bucket"].values) == {"18-24", "45-54", "65+"}
