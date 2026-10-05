#----------------------------------------
# 解析藏品选择器
#----------------------------------------

# 藏品选择器的处理
# 返回选择器的TargetOption
def analyze_relic_selector(blackboard):
    result = {}
    # 部署类型
    if "selector.buildable" in blackboard:
        result["_buildableType"] = blackboard["selector.buildable"].upper()
    # 地位级别
    if "selector.enemy_level_type" in blackboard:
        result["_enemyLevelMask"] = blackboard["selector.enemy_level_type"]
    elif "selector.boss_option" in blackboard: # 另一种写法
        result["_enemyLevelMask"] = "BOSS"
    # 阵营筛选处理
    if "selector.side" in blackboard:
        result["targetSide"] = blackboard["selector.side"].upper()
    # 角色类单位ID筛选
    if "selector.char" in blackboard:
        result["_charId"] = blackboard["selector.char"]
    # 敌人类单位ID筛选
    if "selector.enemy" in blackboard:
        result["_enemyId"] = blackboard["selector.enemy"]
    # 敌人ID反向筛选
    if "selector.enemy_exclude" in blackboard:
        result["_excludeEnemyId"] = blackboard["selector.enemy_exclude"]
    return result