from datetime import datetime


def check_sf_date_same_day(sf_time, record, headers):
    """
    判断日期列表中是否包含与需新建日期相同的日期。

    参数：
    - sf_time (list of str): 现有的日期列表，日期格式为 'YYYY-MM-DD'。
    - record (dict): 包含新建记录的字典，需包含 '随访日期' 键。
    - headers (list of str): 记录的字段名列表，用于检查是否包含 '随访日期'。

    返回：
    - bool: 如果存在相同的日期，返回 True；否则返回 False。
    """

    # 将 sf_time 列表中的日期字符串转换为 datetime.date 对象，并存储在集合中以提高查找效率
    try:
        sf_time_dates = set(datetime.strptime(date_str, '%Y-%m-%d').date() for date_str in sf_time)
    except ValueError as e:
        print(f"日期格式错误: {e}")
        return False

    # 初始化 new_sf_time 为一个空集合
    new_sf_time_dates = set()

    # 检查 '随访日期' 是否在 headers 中
    if '随访日期' in headers:
        # 获取 record 中的 '随访日期'
        record_dates = record.get('随访日期')

        if isinstance(record_dates, list):
            # 如果 '随访日期' 是列表，遍历所有日期
            for date_item in record_dates:
                if isinstance(date_item, datetime):
                    new_sf_time_dates.add(date_item.date())
                elif isinstance(date_item, str):
                    try:
                        new_sf_time_dates.add(datetime.strptime(date_item, '%Y-%m-%d').date())
                    except ValueError as e:
                        print(f"日期格式错误: {e}")
        elif isinstance(record_dates, datetime):
            # 如果 '随访日期' 是单个 datetime 对象
            new_sf_time_dates.add(record_dates.date())
        elif isinstance(record_dates, str):
            # 如果 '随访日期' 是单个日期字符串
            try:
                new_sf_time_dates.add(datetime.strptime(record_dates, '%Y-%m-%d').date())
            except ValueError as e:
                print(f"日期格式错误: {e}")
        else:
            print("未知的 '随访日期' 数据类型。")

    # 检查是否有相同的日期
    intersection = sf_time_dates.intersection(new_sf_time_dates)
    if intersection:
        print(f"存在相同的日期: {intersection}")
        return True  # 存在相同的日期

    print("没有相同的日期。")
    return False  # 没有相同的日期
