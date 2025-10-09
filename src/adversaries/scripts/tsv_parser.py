import csv
import re


def safe_split_threshold(value):
    if value == "None":
        return None, None
    parts = value.split("/")
    major = int(parts[0])
    severe = int(parts[1]) if len(parts) > 1 and parts[1] != 'None' else None
    return major, severe


def clean_damage_input(damage_input):
    damage, damage_type = damage_input.split(" ")
    damage_type = "BTH" if "phy/mag" in damage_type else damage_type

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
        output.append({"name": name, "bonus": int(value)})
    return output


def clean_feature_input(feature_input):
    chunks = re.split(r'\s{2,}', feature_input.strip())

    header_pattern = re.compile(r'(.+)\s*-\s*(Passive|Action|Reaction):', re.I)
    header_indexes = []
    for idx, chunk in enumerate(chunks):
        if header_pattern.match(chunk.strip()):
            header_indexes.append(idx)

    out = []
    for i, header_idx in enumerate(header_indexes):
        header = chunks[header_idx].strip()
        name, ftype = header_pattern.match(header).groups()
        name = name.strip()
        ftype = ftype.strip()

        start = header_idx + 1
        end = header_indexes[i + 1] if i + 1 < len(header_indexes) \
            else len(chunks)
        desc = " ".join(chunks[start:end]).strip()

        out.append({
            "name": name,
            "type": ftype,
            "description": desc
        })
    return out


def parse_tsv(filepath):
    with open(filepath, 'r', encoding="utf-8") as file:
        tsv_reader = csv.reader(file, delimiter="\t")
        headers, *rows = list(tsv_reader)
        output = []
        for row in rows:
            major, severe = safe_split_threshold(row[7])
            data = {
                "name": row[0],
                "tier": int(row[1].split()[-1]),
                "type": row[2],
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
                    "name": row[11],
                    "range": row[12],
                    "damage": clean_damage_input(row[13])
                },
                "experience": clean_experience_input(row[14]) if row[14] \
                    else [],
                "feature": clean_feature_input(row[15])
            }
            output.append(data)
        return output
