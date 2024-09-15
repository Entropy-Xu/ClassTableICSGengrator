"""
===========================
@Time : 2024/9/15 下午6:38
@Author : Entropy.Xu
@File : utils.py
@Software: PyCharm
============================
"""
# utils.py

def format_weeks(weeks):
    """
    将周数列表格式化为范围字符串，例如 [1,2,3,5,6,7] -> "1-3,5-7"
    """
    if not weeks:
        return ""
    weeks = sorted(set(weeks))
    ranges = []
    start = prev = weeks[0]
    for week in weeks[1:]:
        if week == prev + 1:
            prev = week
        else:
            if start == prev:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{prev}")
            start = prev = week
    if start == prev:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}-{prev}")
    return ','.join(ranges)
