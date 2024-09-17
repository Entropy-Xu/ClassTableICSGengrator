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
    """将周数列表格式化为范围字符串"""
    if not weeks:
        return ""
    weeks = sorted(set(weeks))
    ranges = []
    start = prev = weeks[0]
    for week in weeks[1:]:
        if week == prev + 1:
            prev = week
        else:
            ranges.append(f"{start}-{prev}" if start != prev else str(start))
            start = prev = week
    ranges.append(f"{start}-{prev}" if start != prev else str(start))
    return ','.join(ranges)

def parse_weeks_input(input_string):
    """解析用户输入的重复周数字符串"""
    weeks = set()
    for part in input_string.split(','):
        part = part.strip()
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                weeks.update(range(start, end + 1))
            except ValueError:
                continue
        else:
            try:
                weeks.add(int(part))
            except ValueError:
                continue
    return sorted(weeks)

def get_time_from_period(period_info):
    """从节次信息中获取开始时间和结束时间"""
    try:
        period_times = period_info.split('\n')[1]
        start_time_str, end_time_str = [t.strip() for t in period_times.split('-')]
        return start_time_str, end_time_str
    except IndexError:
        return None, None
