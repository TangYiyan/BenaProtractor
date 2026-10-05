#----------------------------------------
# 解析肉鸽道具
#----------------------------------------
import math

from bena import ask_bena
from dictionary import anne_dictionary

# 道具的处理
# 返回道具类
def analyze_rogue_item(blackboard):
    if "id" in blackboard:
        item = ask_bena("rogue_item",blackboard["id"])
        return item
    return None

# 道具奖励的处理
# 返回结构体，可能会带有链接
def analyze_rogue_item_reward(blackboard):
    item = analyze_rogue_item(blackboard)
    if item == None:
        if "id" in blackboard:
            if blackboard["id"].startswith("pool"):
                return {
                    "main" : f"给予玩家  {blackboard['id']} 奖池中的随机一个物品"
                }
            else:
                return {
                    "main" : f"给予玩家  {blackboard['id']} × {math.floor(blackboard.get('count',0))}",
                    "link" : blackboard['id']
                }
        else:
            return {
                "main" : "给予玩家 棍木",
                "link" : "minecraft.air"
            }
    if item.type == "COPPER": # 界园钱的特殊处理
        return {
            "main" : f"让 {item.display_name} 加入玩家钱盒",
            "link" : blackboard['id']
        }
    return {
        "main" : f"给予玩家 {item.display_name} × {math.floor(blackboard.get('count',0))}",
        "link" : blackboard['id']
    }