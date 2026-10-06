#----------------------------------------
# 程序绝对路径逻辑
#----------------------------------------
from pathlib import Path
import sys

BASE_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent

# 获取绝对路径
def app_path(*parts):
    return BASE_DIR.joinpath(*parts)
