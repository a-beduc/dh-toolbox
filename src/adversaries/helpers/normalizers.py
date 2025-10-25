from rest_framework.exceptions import ValidationError


def _norm_key(s):
    return str(s or "").strip().upper().replace("-", "_").replace(" ", "_")


DMG_TYPE = {
    None: "UNK", "": "UNK", "UNK": "UNK", "UNKNOWN": "UNK",
    "PHY": "PHY", "PHYSICAL": "PHY",
    "MAG": "MAG", "MAGICAL": "MAG",
    "BTH": "BTH", "BOTH": "BTH", "PHY/MAG": "BTH",
}

BA_RANGE = {
    None: "UNK", "": "UNK", "UNK": "UNK", "UNKNOWN": "UNK",
    "MEL": "MEL", "MELEE": "MEL",
    "CLO": "CLO", "CLOSE": "CLO",
    "FAR": "FAR",
    "VCL": "VCL", "VERY_CLOSE": "VCL", "V_CLOSE": "VCL", "VCLOSE": "VCL",
    "VFA": "VFA", "VERY_FAR": "VFA", "V_FAR": "VFA", "VFAR": "VFA",
}

FEAT_TYPE = {
    None: "UNK", "": "UNK", "UNK": "UNK", "UNKNOWN": "UNK",
    "PAS": "PAS", "PASSIVE": "PAS",
    "ACT": "ACT", "ACTION": "ACT",
    "REA": "REA", "REACTION": "REA",
}

ADV_TYPE = {
    None: "UNK", "": "UNK", "UNK": "UNK", "UNKNOWN": "UNK",
    "BRU": "BRU", "BRUISER": "BRU",
    "HOR": "HOR", "HORDE": "HOR",
    "LEA": "LEA", "LEADER": "LEA",
    "MIN": "MIN", "MINION": "MIN",
    "RAN": "RAN", "RANGED": "RAN",
    "SKU": "SKU", "SKULK": "SKU",
    "SOC": "SOC", "SOCIAL": "SOC",
    "SOL": "SOL", "SOLO": "SOL",
    "STA": "STA", "STANDARD": "STA",
    "SUP": "SUP", "SUPPORT": "SUP",
}

ADV_TIER = {
    None: "UNK", "": "UNK", "UNK": "UNK", "UNKNOWN": "UNK",
    "1": 1, 1: 1, "ONE": 1, "I": 1,
    "2": 2, 2: 2, "TWO": 2, "II": 2,
    "3": 3, 3: 3, "THREE": 3, "III": 3,
    "4": 4, 4: 4, "FOUR": 4, "IV": 4,
}

ADV_STATUS = {
    None: "UNK", "": "UNK", "UNK": "UNK", "UNKNOWN": "UNK",
    "DRA": "DRA", "DRAFT": "DRA",
    "PUB": "PUB", "PUBLISHED": "PUB",
}

TABLES = {
    "DMG_TYPE": DMG_TYPE,
    "BA_RANGE": BA_RANGE,
    "FEAT_TYPE": FEAT_TYPE,
    "ADV_TYPE": ADV_TYPE,
    "ADV_TIER": ADV_TIER,
    "ADV_STATUS": ADV_STATUS,
}


def normalize_choices(value, table_name: str, allow_null: bool = True):
    """Helper that normalize input for canonical TextChoices field at
    the model level.

    Args:
        value: value to normalize
        table_name: key to choose the correct dict map
        allow_null: turn false if case None should throw an error

    Returns:
        The normalized value

    Raises:
        ValidationError: In case of invalid value
    """
    if value in (None, ""):
        if allow_null:
            return None
        raise ValidationError(f"The field '{value}' cannot be empty.")
    table = TABLES[table_name]
    key = _norm_key(value)
    try:
        return table[key]
    except KeyError:
        examples = list(table.keys())
        raise ValidationError(f"Invalid value '{value}'. "
                              f"Try one of {examples}.")
