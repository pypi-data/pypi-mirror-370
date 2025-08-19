import datetime
import time

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from compements.tool import parse_date


def get_sf_data(driver, sf_time):

    # 获取新建时间范围
    with open("./文档/admin.txt", 'r', encoding='utf-8') as file:
        content = file.readlines()
    # 使用 split() 方法分割字符串
    start_date = content[4].replace("：", ":").split(":")[1].strip()
    end_date = content[5].replace("：", ":").split(":")[1].strip()
    print("随访新建起始时间:", start_date)
    print("随访新建结束时间:", end_date)

    start_date = parse_date(start_date)
    start_year = start_date.year
    print("随访新建起始年份：", start_year)
    end_date = parse_date(end_date)
    end_year = end_date.year
    print("随访新建结束年份：", end_year)

    sf_data_collection = {}

    # 假设 sf_time 是一个日期列表，已经和 year_cells 对应
    i = 0  # 初始化索引

    for year in range(start_year, end_year + 1):

        driver.switch_to.default_content()
        # 切换到第一个 iframe
        first_iframe = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, '//*[@id="ext-gen21"]/iframe')))
        driver.switch_to.frame(first_iframe)

        try:
            year_element = WebDriverWait(driver, 5).until(ec.presence_of_element_located(
                (By.XPATH, f'//*[@id="ext-gen14-gp-year-{year}"]')))
        except:
            print(f"{year}暂无随访记录")
            continue
        year_class = year_element.get_attribute('class')
        if year_class == 'x-grid-group':
            print("年份已展开")
        else:
            print("年份未展开，正在展开...")
            year_element.click()
            time.sleep(1)

        elements = WebDriverWait(driver, 15).until(ec.presence_of_all_elements_located((By.XPATH,
                                                                                        f"//div[@id='ext-gen14-gp-year-{year}-bd']//div[@class='x-grid3-cell-inner x-grid3-col-1 x-unselectable']")))
        num_elements = len(elements)

        # 改为通过索引循环，每次重新获取元素
        for index in range(num_elements):
            # 重新获取当前元素列表
            current_elements = WebDriverWait(driver, 15).until(ec.presence_of_all_elements_located((By.XPATH,
                                                                                                    f"//div[@id='ext-gen14-gp-year-{year}-bd']//div[@class='x-grid3-cell-inner x-grid3-col-1 x-unselectable']")))

            # 检查索引是否有效
            if index >= len(current_elements):
                break
            element = current_elements[index]

            element.click()

            # 切换到第二个 iframe
            second_iframe = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.XPATH, '//*[@id="ext-gen32"]/iframe')))
            driver.switch_to.frame(second_iframe)

            # 获取随访数据
            sf_data = {}

            # 收缩压
            try:
                element = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
                    (By.XPATH, '//*[@id="sbp"]')))
                sbp = element.get_attribute('value')
                sf_data['收缩压'] = sbp
            except:
                sf_data['收缩压'] = '未查'

            # 舒张压
            try:
                element = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
                    (By.XPATH, '//*[@id="dbp"]')))
                dbp = element.get_attribute('value')
                sf_data['舒张压'] = dbp
            except:
                sf_data['舒张压'] = '未查'

            # 空腹血糖
            try:
                element = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
                    (By.XPATH, '//*[@id="fbg"]')))
                FBG = element.get_attribute('value')
                sf_data['空腹血糖'] = FBG
            except:
                sf_data['空腹血糖'] = '未查'

            try:
                element = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
                    (By.XPATH, '//*[@id="heartRateCur"]')))
                target_heart_rate = element.get_attribute('value')
                sf_data['心率'] = target_heart_rate
            except:
                sf_data['心率'] = '未查'

            # 餐后血糖
            try:
                element = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
                    (By.XPATH, '//*[@id="pbg"]')))
                PBG = element.get_attribute('value')
                sf_data['餐后血糖'] = PBG
            except:
                sf_data['餐后血糖'] = '未查'

            # 糖化血红蛋白
            try:
                element = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
                    (By.XPATH, '//*[@id="hba1c"]')))
                glycosylated_hemoglobin = element.get_attribute('value')
                sf_data['糖化血红蛋白'] = glycosylated_hemoglobin
            except:
                sf_data['糖化血红蛋白'] = '未查'

            # 当前体重
            try:
                element = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
                    (By.XPATH, '//*[@id="weightCur"]')))
                weightCur = element.get_attribute('value')
                sf_data['体重'] = weightCur
            except:
                sf_data['体重'] = '未查'

            # 当前身高
            try:
                element = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
                    (By.XPATH, '//*[@id="height"]')))
                height = element.get_attribute('value')
                sf_data['身高'] = height
            except:
                sf_data['身高'] = '未查'

            # 确保sf_time是一个可迭代对象，如果它是单个时间戳，则转换为列表
            if isinstance(sf_time, pd.Timestamp):
                sf_time = [str(sf_time).replace(" 00:00:00", "")]

            # 将日期和随访数据保存到字典中
            if i < len(sf_time):
                sf_data_collection[sf_time[i]] = sf_data
                i += 1  # 更新索引

            driver.switch_to.default_content()
            # 切换到第一个 iframe
            first_iframe = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.XPATH, '//*[@id="ext-gen21"]/iframe')))
            driver.switch_to.frame(first_iframe)

    return sf_data_collection
