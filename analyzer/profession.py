#----------------------------------------
# 解析职业或职业掩码
#----------------------------------------
from dictionary import anne_dictionary

# 职业筛选的处理
# 返回职业的字符串。说明筛选的职业以及“干员”和“召唤物”这样的称呼
def analyze_profession(profession_mask):
    profession_mask = profession_mask.upper()
    masked_list = [profession_mask]
    if "," in profession_mask:
        masked_list = profession_mask.split(",")
    elif "|" in profession_mask:
        masked_list = profession_mask.split("|")
    # 如果大于等于8职业的话有可能是用于筛所有干员的，进行缩减处理
    if len(masked_list) >= 8 and "PIONEER" in masked_list and "WARRIOR" in masked_list and "TANK" in masked_list and "SNIPER" in masked_list and "CASTER" in masked_list and "SUPPORT" in masked_list and "MEDIC" in masked_list and "SPECIAL" in masked_list:
        if "TOKEN" in masked_list and "TRAP" in masked_list:
            return "干员、召唤物、装置"
        elif "TOKEN" in masked_list:
            return "干员、召唤物"
        elif "TRAP" in masked_list:
            return "干员、装置"
        else:
            return "干员"
    else:
        professions = []
        objects = []
        for masked in masked_list:
            if masked in ["TOKEN","TRAP"]:
                objects.append(anne_dictionary("profession",masked))
            else:
                professions.append(anne_dictionary("profession",masked))
        return "、".join(["/".join(professions)+"干员"] + objects)

# 子职业筛选的处理
# 返回子职业的字符串。说明筛选的子职业以及“干员”
def analyze_sub_profession(sub_profession_mask):
    sub_profession_mask = sub_profession_mask.lower()
    masked_list = [sub_profession_mask]
    if "," in sub_profession_mask:
        masked_list = sub_profession_mask.split(",")
    elif "|" in sub_profession_mask:
        masked_list = sub_profession_mask.split("|")
    sub_professions = []
    for masked in masked_list:
        sub_professions.append(anne_dictionary("sub_profession",masked))
    return "/".join(sub_professions)+"干员"