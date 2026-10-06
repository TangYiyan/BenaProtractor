#----------------------------------------
# 解析DeckBuff
#----------------------------------------
from analyzer.buff import analyze_buff

# 解析Buff的详细信息
# 返回结构体
def analyze_deckbuff(deck_buff_data: dict,blackboard: dict = {},full_information=False):
    # 未解析参数：showToastWhenAffect
    result = analyze_buff(deck_buff_data["buff"],blackboard,full_information)
    if full_information:
        if deck_buff_data["lifeType"] == "ALL_THE_TIME":
            result["children"].append({"main" : "每次对象部署时生效"})
        else:
            result["children"].append({"main" : "下一次对象部署时生效，仅生效一次"})
        if deck_buff_data["affectInHand"]:
            result["children"].append({"main" : "仅生效于\"位于手卡中\"的对象（即未被隐藏的单位）"})
        if deck_buff_data["affectOutOfHand"]:
            result["children"].append({"main" : "仅生效于\"不位于手卡中\"的对象（即被隐藏的单位）"})
        if deck_buff_data["cardEffectType"] != "NONE":
            result["children"].append({"main" : "为对象增加头像特效" + deck_buff_data["cardEffectType"]})
        if deck_buff_data["cardAnimWhenDeckbuffAdd"] != "":
            result["children"].append({"main" : "添加时增加头像动画" + deck_buff_data["cardAnimWhenDeckbuffAdd"]})
        if deck_buff_data["wontSpawnWhenRallyPointSwitch"]:
            result["children"].append({"main" : "wontSpawnWhenRallyPointSwitch"})
        if deck_buff_data["ignoreSpecialBuild"]:
            result["children"].append({"main" : "ignoreSpecialBuild"})
    return result