#----------------------------------------
# 解析属性加成
#----------------------------------------
from dictionary import anne_dictionary, is_anne_key

# 获取key是否是属性值的方法
# 属性字典里存了所有属性类型，因此直接用了
def is_attribute_key(key: str):
    return is_anne_key("attribute",key.upper())