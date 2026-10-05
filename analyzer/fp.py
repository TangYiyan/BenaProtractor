#----------------------------------------
# 解析定点数
#----------------------------------------
# 解析定点数，返回浮点数
def analyze_fp(fp_data: dict):
    if "_serializedValue" not in fp_data:
        return 0.
    serialized_value = fp_data["_serializedValue"]
    return float(serialized_value) / 4294967296.