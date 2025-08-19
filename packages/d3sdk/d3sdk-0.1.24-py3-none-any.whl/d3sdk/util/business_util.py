import re
from typing import List

def is_number(s: str) -> bool:
    """检查字符串是否为数字"""
    return s.isdigit()

def get_between(start_custom: str, end_custom: str) -> List[str]:
    between_customs = []
    
    # 找到数字部分的起始位置
    i = None
    for l in range(len(start_custom) - 1, 0, -1):
        substring = start_custom[l:]
        if not is_number(substring):
            i = l + 1
            break
        if len(substring) == len(end_custom):
            i = l
            break
    
    if i is None:
        i = 0  # 如果没有找到非数字部分，假设整个字符串都是数字部分
    
    if is_number(end_custom):
        end_custom = start_custom[:i] + end_custom
    
    if len(start_custom) == len(end_custom):
        if start_custom[:i] == end_custom[:i]:
            start_custom_index = start_custom[i:]
            end_custom_index = end_custom[i:]
            num_length = len(end_custom_index)
            format_str = f"%0{num_length}d" if num_length > 1 else "%d"
            
            for index in range(int(start_custom_index), int(end_custom_index) + 1):
                between_customs.append(start_custom[:i] + format_str % index)
        else:
            print(f"Error: {start_custom},{end_custom} 范围解析有误")
    else:
        if start_custom[:i] == end_custom[:i]:
            try:
                start_custom_index = start_custom[start_custom.rfind("_") + 1:] if "_" in start_custom else start_custom[i:]
                end_custom_index = end_custom[end_custom.rfind("_") + 1:] if "_" in end_custom else end_custom[i:]
                
                for index in range(int(start_custom_index), int(end_custom_index) + 1):
                    between_customs.append(start_custom[:i] + str(index))
            except Exception as e:
                print(f"Error: {start_custom},{end_custom} 范围解析有误")
        else:
            print(f"Error: {start_custom},{end_custom} 范围解析有误")
    
    return between_customs

# 测试示例
# print(get_between("DiroutWatTemper3", "12"))
# print(get_between("DiroutWatTemper_3", "12"))
# print(get_between("DiroutWatTemper_003", "008"))
# print(get_between("DiroutWatTemper_003", "101"))
# print(get_between("DiroutWatTemper_0033", "0101"))
# print(get_between("DiroutWatTemper00033", "101"))