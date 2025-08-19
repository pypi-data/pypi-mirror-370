from datetime import datetime


def get_quarter(date):
    """返回给定日期所在的季度（1, 2, 3, 4）"""
    month = date.month
    if month in [1, 2, 3]:
        return 1
    elif month in [4, 5, 6]:
        return 2
    elif month in [7, 8, 9]:
        return 3
    else:
        return 4


def has_current_quarter(sf_time, record, headers):
    """判断日期列表中是否包含与需新建日期同一季度的日期"""

    sf_time_dates = [datetime.strptime(date_str, '%Y-%m-%d') for date_str in sf_time]

    new_sf_time = []
    if '随访日期' in headers:
        new_sf_time = record['随访日期']
        new_sf_time = [new_sf_time.strftime('%Y-%m-%d')]

    # 检查 new_sf_time 中的日期是否与已有记录中的日期在同一季度
    for new_date in sf_time_dates:
        new_quarter = get_quarter(new_date)
        for existing_date_str in new_sf_time:
            existing_date = datetime.strptime(existing_date_str, '%Y-%m-%d')
            if get_quarter(existing_date) == new_quarter:
                return True  # 如果有同季度的日期，返回 True

    return False  # 没有同季度的日期，返回 False




