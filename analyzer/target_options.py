#----------------------------------------
# 解析目标选项
#----------------------------------------
from bena import ask_bena_character, ask_bena_enemy
from dictionary import anne_dictionary

# 解析目标选项的详细信息
# 返回结构体
def analyze_target_options(option,relative_side=True):
    conditions = []
    # 阵营
    if not option["enableAdvancedOptions"] or not option["ignoreTargetSide"]:
        if relative_side:
            conditions.append(anne_dictionary("side_type_relative",option["targetSide"]))
        else:
            conditions.append(anne_dictionary("side_type",option["targetSide"]))
    # 实体类型
    if option["targetCategory"] != "DEFAULT":
        conditions.append(anne_dictionary("entity_category",option["targetCategory"]))
    # 行动方式
    if option["targetMotion"] != "ALL":
        conditions.append(anne_dictionary("motion",option["targetMotion"]))
    # 单位类型
    if option["checkUnitType"]:
        conditions.append(anne_dictionary("unit_type",option["unitTypeMask"]))

    # 开始处理进阶选项
    descriptions = []
    advanced = option["enableAdvancedOptions"]
    # 如果没有额外选项，一些选项就没意义了
    if not advanced:
        descriptions.append("不启用额外可选判定")
    # 无视无法选择
    if advanced and option["ignoreTargetFree"]:
        if option["onlyIgnoreSomeOfTargetFreeCase"]:
            if option["abnormalFlag"] != "E_NUM":
                abnormal_flag = anne_dictionary("abnormal",option["abnormalFlag"])
                if option["abnormalCombo"] != "E_NUM":
                    abnormal_combo = anne_dictionary("abnormal",option["abnormalCombo"])
                    descriptions.append("无视"+abnormal_flag+"/"+abnormal_combo)
                else:
                    descriptions.append("无视"+abnormal_flag)
            if option["abnormalCombo"] != "E_NUM":
                abnormal_combo = anne_dictionary("abnormal",option["abnormalCombo"])
                descriptions.append("无视"+abnormal_combo)
        else:
            descriptions.append("无视无法选择")
    # 无视孤立
    if advanced and option["ignoreAllyTargetFree"]:
        descriptions.append("无视孤立")
    # 无视禁疗
    if advanced and option["ignoreHealFree"]:
        descriptions.append("无视禁疗")
    # 排除特定有异常效果单位
    if advanced and "excludeSomeAbnormalFlags" in option and option["excludeSomeAbnormalFlags"]:
        abnormal_flag = anne_dictionary("abnormal",option["excludeAbnormalFlag"])
        descriptions.append(f"不选择持有{abnormal_flag}异常的单位")
    # 必须含有特定异常效果单位
    if advanced and "containSomeAbnormalFlags" in option and option["containSomeAbnormalFlags"]:
        abnormal_flag = anne_dictionary("abnormal",option["containAbnormalFlag"])
        descriptions.append(f"必须为持有{abnormal_flag}异常的单位")
    # 行为覆写
    if advanced and option["purposeMask"] != "NONE":
        purpose = anne_dictionary("purpose",option["purposeMask"])
        descriptions.append(f"视为一次{purpose}")
    unit_name = "单位"
    # 职业筛选
    if advanced and option["professionMask"] != "NONE":
        if option["professionMask"] == "WARRIOR, SNIPER, TANK, MEDIC, SUPPORT, CASTER, SPECIAL, PIONEER":
            #descriptions.append(f"必须是干员")
            unit_name = f"干员"
        elif option["professionMask"] == "WARRIOR, SNIPER, TANK, MEDIC, SUPPORT, CASTER, SPECIAL, TOKEN, PIONEER":
            #descriptions.append(f"必须是干员或召唤物")
            unit_name = f"干员/召唤物"
        elif option["professionMask"] == "WARRIOR, SNIPER, TANK, MEDIC, SUPPORT, CASTER, SPECIAL, TRAP, PIONEER":
            #descriptions.append(f"必须是干员或装置")
            unit_name = f"干员/装置"
        elif option["professionMask"] != "WARRIOR, SNIPER, TANK, MEDIC, SUPPORT, CASTER, SPECIAL, TOKEN, TRAP, PIONEER":
            classes = "/".join([anne_dictionary("profession",_cls) for _cls in option["professionMask"].split(", ")])
            #descriptions.append(f"必须是{classes}单位")
            unit_name = f"{classes}单位"

    # 一些藏品相关的参数
    # 必须为特定部署类型的单位
    if "_buildableType" in option and option["_buildableType"]:
        buildable = anne_dictionary("buildable_type",option["_buildableType"])
        descriptions.append(f"必须是{buildable}的单位")
    # 必须是含有特定id的角色类单位
    if "_charId" in option and option["_charId"]:
        char_name = ask_bena_character(option["_charId"])
        if char_name != option["_charId"]:
            char_name += f"（{option['_charId']}）"
        #descriptions.append(f"必须是名为 {char_name} 的角色类单位")
        conditions.append(f"名为 {char_name} 的角色类")
    # 必须是特定地位级别的单位
    if "_enemyLevelMask" in option and option["_enemyLevelMask"]:
        enemy_level = anne_dictionary("enemy_level",option["_enemyLevelMask"])
        descriptions.append(f"必须是地位级别为{enemy_level}的单位")
    # 必须是含有特定id的敌人类单位
    if "_enemyId" in option and option["_enemyId"]:
        enemy_name = ask_bena_enemy(option["_enemyId"])
        if enemy_name != option["_enemyId"]:
            enemy_name += f"（{option['_enemyId']}）"
        #descriptions.append(f"必须是名为 {enemy_name} 的敌人类单位")
        conditions.append(f"名为 {enemy_name} 的敌人类")
    # 排除特定id的敌人类单位
    if "_excludeEnemyId" in option and option["_excludeEnemyId"]:
        enemy_name = ask_bena_enemy(option["_excludeEnemyId"])
        if enemy_name != option["_excludeEnemyId"]:
            enemy_name += f"（{option['_excludeEnemyId']}）"
        descriptions.append(f"不选择名为 {enemy_name} 的敌人类单位")

    if len(descriptions) > 0:
        return {
            "main" : "".join(conditions)+unit_name,
            "description" : "；".join(descriptions)
        }
    #最朴实无华的选择，没有任何附加条件
    return {
        "main" : "".join(conditions)+unit_name
    }