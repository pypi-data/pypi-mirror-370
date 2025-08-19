from datetime import datetime, timedelta


def trans_str_time_to_index(now_time, minute=15):
    """将时间按照minute切换为索引，时间格式为 %H-%M"""
    time_list = [int(i) for i in now_time.split(":")]
    time_int = time_list[0] * 4 + time_list[1] // minute
    return time_int


def get_highest_or_lowest_value(start_time, end_time, hours, price_list, reverse=False):
    start_index = trans_str_time_to_index(start_time)
    end_index = trans_str_time_to_index(end_time)
    arr = price_list[start_index:end_index]
    if None in arr:
        return False
    indices = list(range(end_index - start_index))
    sorted_indices = sorted(indices, key=lambda i: arr[i], reverse=reverse)
    return sorted_indices[: int(hours * 4)], start_index


def get_rounded_times():
    """
    返回距离当前时间最近的15min的整点时间以及后一整点5min时间（天气是预测未来15min的，也就是在00:00时，只能拿到00:15的数据）
    """
    now = datetime.now()
    # 确定当前时间所属的15分钟区间
    index_1 = now.minute // 15
    index_2 = now.minute % 15
    left_time = now.replace(minute=15 * index_1, second=0, microsecond=0)
    right_time = left_time + timedelta(minutes=15)
    if index_2 < 8:
        nearest_time = left_time
    else:
        nearest_time = right_time
    return datetime.strftime(nearest_time, "%Y-%m-%d %H:%M:%S"), datetime.strftime(
        right_time, "%Y-%m-%d %H:%M:%S"
    )
