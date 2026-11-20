def average(values):
    """计算数字列表的平均值。"""
    if not values:
        return 0
    return sum(values) / len(values)
