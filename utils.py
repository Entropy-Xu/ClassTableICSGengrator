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
    """格式化周数列表为字符串，连续的周数用'-'表示"""
    if not weeks:
        return ''
    weeks = sorted(weeks)
    ranges = []
    start = prev = weeks[0]
    for week in weeks[1:]:
        if week == prev + 1:
            prev = week
        else:
            if start == prev:
                ranges.append(f"{start}")
            else:
                ranges.append(f"{start}-{prev}")
            start = prev = week
    if start == prev:
        ranges.append(f"{start}")
    else:
        ranges.append(f"{start}-{prev}")
    return ','.join(ranges)

def parse_weeks_input(weeks_input):
    """解析周数输入字符串，返回周数列表"""
    weeks = set()
    for part in weeks_input.split(','):
        part = part.strip()
        if '-' in part:
            try:
                start, end = part.split('-')
                weeks.update(range(int(start), int(end) + 1))
            except ValueError:
                continue
        else:
            try:
                weeks.add(int(part))
            except ValueError:
                continue
    return sorted(weeks)

def get_time_from_period(period_str):
    """根据节次信息获取开始时间和结束时间"""
    try:
        times = period_str.split('\n')[1]
        start_time_str, end_time_str = times.split('-')
        return start_time_str.strip(), end_time_str.strip()
    except IndexError:
        return "08:00", "09:00"  # 默认时间