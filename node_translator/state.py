#----------------------------------------
# 状态机相关Node
#----------------------------------------
from dictionary import anne_dictionary

# 检查角色类单位是否为阻挡状态机
def node_CheckCharacterInBornState(node,blackboard):
    owner_name = anne_dictionary("target",node["_ownerType"])
    return {
        "main" : f"检查{owner_name}（角色类）的状态机",
        "true" : "若处于部署（Born）状态机",
        "false" : "若不处于部署（Born）状态机或不为角色类"
    }

# 检查敌人类单位是否为阻挡状态机
def node_CheckEnemyInBornState(node,blackboard):
    owner_name = anne_dictionary("target",node["_ownerType"])
    return {
        "main" : f"检查{owner_name}（敌人类）的状态机",
        "true" : "若处于出场（Born）状态机",
        "false" : "若不处于出场（Born）状态机或不为敌人类"
    }

# 检查是否为阻挡状态机
def node_CheckUnitInCombatState(node,blackboard):
    owner_name = anne_dictionary("target",node["_ownerType"])
    return {
        "main" : f"检查{owner_name}的状态机",
        "true" : "若处于阻挡（Combat）状态机",
        "false" : "若不处于阻挡（Combat）状态机"
    }

# 检查是否为攻击状态机
def node_CheckUnitInAttackState(node,blackboard):
    owner_name = anne_dictionary("target",node["_ownerType"])
    return {
        "main" : f"检查{owner_name}的状态机",
        "true" : "若处于攻击（Attack）状态机",
        "false" : "若不处于攻击（Attack）状态机"
    }

# 检查是否为重生状态机
def node_CheckUnitInRebornState(node,blackboard):
    owner_name = anne_dictionary("target",node["_ownerType"])
    return {
        "main" : f"检查{owner_name}的状态机",
        "true" : "若处于重生（Reborn）状态机",
        "false" : "若不处于重生（Reborn）状态机"
    }

# 检查是否为消失状态机
def node_CheckUnitInDisappearState(node,blackboard):
    owner_name = anne_dictionary("target",node["_ownerType"])
    return {
        "main" : f"检查{owner_name}的状态机",
        "true" : "若处于消失（Disappear）状态机",
        "false" : "若不处于消失（Disappear）状态机"
    }

# 检查是否为移动状态机
def node_CheckUnitInMoveState(node,blackboard):
    owner_name = anne_dictionary("target",node["_ownerType"])
    return {
        "main" : f"检查{owner_name}的状态机",
        "true" : "若处于移动（Move）状态机",
        "false" : "若不处于移动（Move）状态机"
    }