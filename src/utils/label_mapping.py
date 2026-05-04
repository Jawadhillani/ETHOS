"""
Unified label taxonomy for ETHOS.

FairFace is the native source (7 race classes).
RFW uses 4 classes — handled via FAIRFACE_TO_RFW mapping when needed.
All internal processing uses UNIFIED_TAXONOMY keys.
"""

UNIFIED_TAXONOMY = {
    "race": {
        "classes": [
            "White",
            "Black",
            "Latino_Hispanic",
            "East Asian",
            "Southeast Asian",
            "Indian",
            "Middle Eastern",
        ],
        "unknown": "Unknown",
    },
    "gender": {
        "classes": ["Male", "Female"],
        "unknown": "Unknown",
    },
    "age": {
        "classes": ["0-2", "3-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70+"],
        "unknown": "Unknown",
    },
}

# FairFace CSV uses these exact strings — map to our canonical keys
FAIRFACE_RACE_MAP = {
    "White": "White",
    "Black": "Black",
    "Latino_Hispanic": "Latino_Hispanic",
    "East Asian": "East Asian",
    "Southeast Asian": "Southeast Asian",
    "Indian": "Indian",
    "Middle Eastern": "Middle Eastern",
}

FAIRFACE_GENDER_MAP = {
    "Male": "Male",
    "Female": "Female",
}

FAIRFACE_AGE_MAP = {
    "0-2": "0-2",
    "3-9": "3-9",
    "10-19": "10-19",
    "20-29": "20-29",
    "30-39": "30-39",
    "40-49": "40-49",
    "50-59": "50-59",
    "60-69": "60-69",
    "more than 70": "70+",  # FairFace uses this string
}

# RFW uses 4 race classes — map our 7 to those when RFW data is present
FAIRFACE_TO_RFW = {
    "White": "Caucasian",
    "Black": "African",
    "Latino_Hispanic": "Caucasian",   # closest RFW equivalent
    "East Asian": "Asian",
    "Southeast Asian": "Asian",
    "Indian": "Indian",
    "Middle Eastern": "Caucasian",    # closest RFW equivalent
}

RFW_RACE_MAP = {
    "Caucasian": "Caucasian",
    "African": "African",
    "Asian": "Asian",
    "Indian": "Indian",
}


def normalize_fairface_labels(race: str, gender: str, age: str) -> dict:
    """Convert raw FairFace CSV strings to unified taxonomy."""
    return {
        "race": FAIRFACE_RACE_MAP.get(race, "Unknown"),
        "gender": FAIRFACE_GENDER_MAP.get(gender, "Unknown"),
        "age": FAIRFACE_AGE_MAP.get(age, "Unknown"),
    }


def to_rfw_race(unified_race: str) -> str:
    """Map a unified 7-class race label to the 4-class RFW taxonomy."""
    return FAIRFACE_TO_RFW.get(unified_race, "Unknown")


def get_race_classes(mode: str = "fairface") -> list:
    """Return race class list for a given dataset mode ('fairface' or 'rfw')."""
    if mode == "rfw":
        return list(RFW_RACE_MAP.keys())
    return UNIFIED_TAXONOMY["race"]["classes"]
