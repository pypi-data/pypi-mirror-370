__version__ = "1.4.0"
__description__ = "General-Validator is a universal batch data validator."

# 导入主要的校验函数
from .checker import (
    check,
    check_not_empty,
    check_when,
    check_when_each,
    check_list_when,
    check_list,
    check_nested,
    checker
)

__all__ = [
    "__version__", 
    "__description__",
    "check", # 通用校验函数
    "check_not_empty", # 非空校验函数
    "check_when", # 严格条件校验
    "check_when_each", # 逐项条件校验
    "check_list_when", # check_when_each的简化版，专门用于列表数据
    "check_list", # 列表校验函数
    "check_nested", # 嵌套校验函数
    "checker" # 链式校验函数
]