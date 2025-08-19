from datetime import datetime, timedelta


def get_quarter(date):
    """获取日期所属的季度"""
    month = date.month
    if month in [1, 2, 3]:
        return 1
    elif month in [4, 5, 6]:
        return 2
    elif month in [7, 8, 9]:
        return 3
    else:
        return 4


# def get_new_sf_time(visit_dates, followup_dates):
#     """找出缺失的季度随访日期"""
#
#     # 获取新建时间范围
#     with open("./文档/admin.txt", 'r', encoding='utf-8') as file:
#         content = file.readlines()
#     # 使用 split() 方法分割字符串
#     start_date = content[4].replace("：", ":").split(":")[1].strip()
#     end_date = content[5].replace("：", ":").split(":")[1].strip()
#     print("随访新建起始时间:", start_date)
#     print("随访新建结束时间:", end_date)
#
#     # 将日期字符串转换为 datetime 对象
#     visit_dates = [datetime.strptime(date, "%Y-%m-%d") for date in visit_dates]
#     followup_dates = [datetime.strptime(date, "%Y-%m-%d") for date in followup_dates]
#     print("门诊日期:", visit_dates)
#     print("随访日期:", followup_dates)
#
#     # 按季度将门诊日期分类
#     quarters = {1: [], 2: [], 3: [], 4: []}
#     for visit in visit_dates:
#         quarter = get_quarter(visit)
#         quarters[quarter].append(visit)
#
#     # 确定已建随访的季度
#     followup_quarters = set()
#     for followup in followup_dates:
#         followup_quarters.add(get_quarter(followup))
#     print("已建随访的季度:", followup_quarters)
#
#     # 获取当前季度（动态计算当前日期）
#     current_date = datetime.now()
#     current_quarter = get_quarter(current_date)
#     print("当前季度:", current_quarter)
#
#     # 检查缺失的季度随访
#     missing_quarters = set(range(1, current_quarter + 1)) - followup_quarters
#     print("缺失的季度:", missing_quarters)
#
#     # 为缺失的季度选择门诊日期
#     missing_followups_dates = []
#
#     # 初始化前一个随访日期为已有的随访日期中的最晚日期
#     previous_followup_date = max(followup_dates) if followup_dates else None
#
#     # 按季度顺序处理缺失的季度
#     for quarter in sorted(missing_quarters):
#         # 获取当前季度的门诊日期，并按日期排序
#         quarter_visits = sorted(quarters[quarter])
#
#         # 如果没有门诊日期，跳过该季度
#         if not quarter_visits:
#             continue
#
#         # 判断缺失的季度是在已有季度的前面还是后面
#         if followup_quarters and quarter < min(followup_quarters):
#             # 如果缺失的季度在已有季度的前面，选择该季度最晚的日期
#             selected_date = quarter_visits[-1]
#         else:
#             # 如果缺失的季度在已有季度的后面，选择该季度最早的日期
#             selected_date = quarter_visits[0]
#
#         # 检查日期间隔是否超过30天
#         if previous_followup_date:
#             time_diff = (selected_date - previous_followup_date).days
#             if abs(time_diff) < 30:
#                 # 如果间隔小于30天，选择下一个合适的日期
#                 if quarter < min(followup_quarters):
#                     # 如果在前面的季度，选择比前一个随访日期早30天以上的最晚日期
#                     for date in reversed(quarter_visits):
#                         if (previous_followup_date - date).days > 30:
#                             selected_date = date
#                             break
#                 else:
#                     # 如果在后面的季度，选择比前一个随访日期晚30天以上的最早日期
#                     for date in quarter_visits:
#                         if (date - previous_followup_date).days > 30:
#                             selected_date = date
#                             break
#
#         # 添加选中的日期到缺失随访日期列表
#         missing_followups_dates.append(selected_date.strftime("%Y-%m-%d"))
#         previous_followup_date = selected_date
#
#     return missing_followups_dates

def get_quarters_in_range(start_date, end_date):
    """生成时间范围内的所有季度（年份，季度）"""
    quarters = []
    current_date = start_date
    while current_date <= end_date:
        year = current_date.year
        quarter = (current_date.month - 1) // 3 + 1  # 假设 get_quarter 函数如此实现
        quarters.append((year, quarter))
        # 计算下一个季度的第一天
        if quarter == 1:
            next_date = datetime(year, 4, 1)
        elif quarter == 2:
            next_date = datetime(year, 7, 1)
        elif quarter == 3:
            next_date = datetime(year, 10, 1)
        else:  # Q4
            next_date = datetime(year + 1, 1, 1)
        current_date = next_date

    # 去重并保持顺序
    seen = set()
    unique_quarters = []
    for q in quarters:
        if q not in seen:
            seen.add(q)
            unique_quarters.append(q)

    # 过滤逻辑：检查季度时间段与输入范围是否有交集
    valid_quarters = []
    for q in unique_quarters:
        year, q_num = q
        # 计算季度的开始和结束日期
        quarter_start = datetime(year, (q_num - 1) * 3 + 1, 1)
        if q_num == 1:
            quarter_end = datetime(year, 3, 31)
        elif q_num == 2:
            quarter_end = datetime(year, 6, 30)
        elif q_num == 3:
            quarter_end = datetime(year, 9, 30)
        else:
            quarter_end = datetime(year, 12, 31)

        # 判断季度时间段与输入范围是否有交集
        if (quarter_start <= end_date) and (quarter_end >= start_date):
            valid_quarters.append(q)

    return valid_quarters


def get_new_sf_time(visit_dates, followup_dates):
    """找出缺失的季度随访日期"""

    # 读取时间范围
    with open("./文档/admin.txt", 'r', encoding='utf-8') as file:
        content = file.readlines()
    start_date_str = content[4].split(":")[1].strip()
    end_date_str = content[5].split(":")[1].strip()
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    # 过滤在时间范围内的门诊和随访日期
    visit_dates = [datetime.strptime(d, "%Y-%m-%d") for d in visit_dates]
    followup_dates = [datetime.strptime(d, "%Y-%m-%d") for d in followup_dates]

    valid_visits = [d for d in visit_dates if start_date <= d <= end_date]
    valid_followups = [d for d in followup_dates if start_date <= d <= end_date]

    # 生成时间范围内的所有季度
    quarters_in_range = get_quarters_in_range(start_date, end_date)
    print("时间范围内的季度:", quarters_in_range)

    # 按季度分类门诊日期
    visits_by_quarter = {}
    for date in valid_visits:
        q = (date.year, get_quarter(date))
        if q in visits_by_quarter:
            visits_by_quarter[q].append(date)
        else:
            visits_by_quarter[q] = [date]

    # 确定已建随访的季度
    followup_quarters = set()
    for date in valid_followups:
        q = (date.year, get_quarter(date))
        followup_quarters.add(q)
    print("已建随访季度:", followup_quarters)

    # 确定缺失的季度
    missing_quarters = [q for q in quarters_in_range if q not in followup_quarters]
    print("缺失的季度:", missing_quarters)

    # 按时间顺序处理缺失季度
    missing_quarters_sorted = sorted(missing_quarters, key=lambda x: (x[0], x[1]))
    missing_dates = []
    previous_date = max(valid_followups) if valid_followups else None

    # 初始化 latest_followup_q，避免未赋值的情况
    latest_followup_q = None
    if valid_followups:
        # 已建的最晚季度
        latest_followup_q = max(followup_quarters, key=lambda x: (x[0], x[1]))

    for q in missing_quarters_sorted:
        # 获取该季度的所有门诊日期并排序
        dates = sorted(visits_by_quarter.get(q, []))
        if not dates:
            continue  # 无门诊日期则跳过

        # 确定选择规则
        if valid_followups:
            if q < latest_followup_q:
                selected_date = max(dates)  # 选择最晚
            else:
                selected_date = min(dates)  # 选择最早
        else:
            selected_date = min(dates)  # 首个季度选最早

        # 检查日期间隔
        if previous_date:
            if (selected_date - previous_date).days < 30:
                # 根据是否存在有效随访决定调整策略
                if valid_followups:
                    if q < latest_followup_q:
                        # 找比previous_date早且间隔≥30天的最晚日期
                        candidates = [d for d in dates if (previous_date - d).days >= 30]
                        if candidates:
                            selected_date = max(candidates)
                    else:
                        # 找比previous_date晚且间隔≥30天的最早日期
                        candidates = [d for d in dates if (d - previous_date).days >= 30]
                        if candidates:
                            selected_date = min(candidates)
                else:
                    # 无有效随访时，寻找比previous_date晚且间隔≥30天的最早日期
                    candidates = [d for d in dates if (d - previous_date).days >= 30]
                    if candidates:
                        selected_date = min(candidates)
                    else:
                        # 如果无法满足间隔，跳过该季度或保持原选择？
                        # 根据需求决定，此处示例保持原选择
                        pass

        missing_dates.append(selected_date.strftime("%Y-%m-%d"))
        previous_date = selected_date

    return missing_dates


