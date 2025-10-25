def format_basic_attack(name, rge, dice_number, dice_type, bonus,
                        damage_type):
    if not name:
        return None
    dmg = f"{dice_number}d{dice_type}" if dice_number and dice_type else ""
    if bonus:
        sign = "+" if bonus > 0 and dice_number else ""
        dmg += f"{sign}{bonus}"
    return f"{name}: {rge} | {dmg} {damage_type}"


def format_csv_name(items):
    return ", ".join([i.name for i in items]) or None


def format_csv_experience(exps):
    pieces = []
    for e in exps:
        pieces.append(f"{e.experience.name} +{e.bonus}"
                      if e.bonus >= 0
                      else f"{e.experience.name} {e.bonus}")
    return ", ".join(pieces) or None
