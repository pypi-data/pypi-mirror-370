import random
import time

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from comment.excle_write import excel_append2
from comment.write_excle import excel_append
from compements.assemblies.check_sf_date import check_sf_date
from compements.assemblies.introducing_medication import introducing_medication
from compements.tool import update_exercise_time, update_staple_food, parse_date


def quarterly_statistics(driver, sfzh, mz_time):
    # 获取新建时间范围
    with open("./文档/admin.txt", 'r', encoding='utf-8') as file:
        content = file.readlines()
    start_date_str = content[4].replace("：", ":").split(":")[1].strip()
    end_date_str = content[5].replace("：", ":").split(":")[1].strip()

    start_date = parse_date(start_date_str)
    start_year = start_date.year
    end_date = parse_date(end_date_str)
    end_year = end_date.year

    driver.switch_to.default_content()
    WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH, "//dt[contains(text(),'随访服务')]"))).click()
    time.sleep(1)

    sf_time = check_sf_date(driver)
    print("现有随访记录:", sf_time)

    # 初始化每年季度计数器
    yearly_counts = {
        year: [0, 0, 0, 0]  # [Q1, Q2, Q3, Q4]
        for year in range(start_year, end_year + 1)
    }

    # 遍历日期进行统计
    for date_str in sf_time:
        try:
            date = parse_date(date_str)
            year = date.year
            month = date.month
            quarter = (month - 1) // 3  # 计算季度索引0-3

            if year in yearly_counts:
                yearly_counts[year][quarter] += 1
        except Exception as e:
            print(f"日期解析失败: {date_str}, 错误: {str(e)}")

    # 生成动态表头
    column_headers = ["身份证号"]
    for year in range(start_year, end_year + 1):
        for q in range(1, 5):
            column_headers.append(f"{year}年第{q}季度")
    column_headers.extend(["随访日期", "符合条件的门诊日期"])

    # 生成数据内容
    contents = [sfzh]
    for year in range(start_year, end_year + 1):
        contents.extend(yearly_counts[year])
    contents.append(f"已经建立随访的日期-{sf_time}")
    contents.append(f"符合条件的门诊日期-{mz_time}")

    # 写入Excel
    file_path = "执行结果/慢病随访季度统计结果.xlsx"
    excel_append2(file_path, column_headers, contents)
    print("季度统计结果已保存至:", file_path)



