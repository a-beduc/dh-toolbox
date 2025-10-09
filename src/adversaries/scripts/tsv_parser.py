import csv
import re


def safe_split_threshold(value):
    if value == "None":
        return 0, 0
    parts = value.split("/")
    major = int(parts[0])
    severe = int(parts[1]) if len(parts) > 1 and parts[1] != 'None' else 0
    return major, severe


def clean_damage_input(damage_input):
    damage, damage_type = damage_input.split(" ")
    damage_type = "BTH" if "phy/mag" in damage_type else damage_type.upper()

    if "d" not in damage:
        dice_number = 0
        dice_type = 0
        bonus = int(damage)

    else:
        dn_str, tail = damage.split("d")
        dice_number = int(dn_str)

        bonus = 0

        if "+" in tail:
            dice_type, bonus = map(int, tail.split("+"))
        elif "-" in tail:
            dice_type, bonus = map(int, tail.split("-"))
            bonus = -bonus
        else:
            dice_type = int(tail)

    return {
        "dice_number": dice_number,
        "dice_type": dice_type,
        "bonus": bonus,
        "damage_type": damage_type
    }


def clean_experience_input(experience_input):
    experiences = experience_input.split(",")
    output = []
    for experience in experiences:
        name, value = experience.split(" +")
        output.append({"name": name.lower(), "bonus": int(value)})
    return output


def clean_feature_input(feature_input):
    pattern = re.compile(
        r"([\w\s]+(?:\s\(\d+\))?)\s*-\s*(Passive|Action|Reaction):"
        r"\s*(.*?)(?=(?:[\w\s]+(?:\s\(\d+\))?\s*-\s*"
        r"(?:Passive|Action|Reaction):)|\Z)", re.S)
    matches = pattern.findall(feature_input)

    return [
        {
            "name": name.lower(),
            "type": feat_type.upper(),
            "description": desc
        } for name, feat_type, desc in matches
    ]


def parse_tsv(filepath):
    with open(filepath, 'r', encoding="utf-8") as file:
        tsv_reader = csv.reader(file, delimiter="\t")
        headers, *rows = list(tsv_reader)
        output = []
        for row in rows:
            major, severe = safe_split_threshold(row[7])
            data = {
                "name": row[0].lower(),
                "tier": int(row[1].split()[-1]),
                "type": row[2].lower(),
                "horde_hit_point": row[3].split("/")[0] or None,
                "description": row[4],
                "tactics": row[5],
                "difficulty": int(row[6]),
                "threshold_major": major,
                "threshold_severe": severe,
                "hit_point": int(row[8]),
                "stress_point": int(row[9]),
                "atk_bonus": int(row[10].replace("+", "")),
                "basic_attack": {
                    "name": row[11].lower(),
                    "range": row[12].lower(),
                    "damage": clean_damage_input(row[13])
                },
                "experience": clean_experience_input(row[14]) if row[14] else [],
                "feature": clean_feature_input(row[15])
            }
            output.append(data)
        return output
