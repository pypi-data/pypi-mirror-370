import random
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from compements.tool import get_drink_amount, parse_date


def get_tj_data(driver):

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

    driver.switch_to.default_content()
    try:
        WebDriverWait(driver, 3).until(
            ec.presence_of_element_located((By.XPATH, "//dt[contains(text(),'体检服务')]"))).click()
    except:
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, "//dt[contains(text(),'体检')]"))).click()
    time.sleep(1)
    WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH, "//li[contains(text(),'体检服务')]"))).click()
    time.sleep(1)

    tj_data = {}
    # 切换到第一个 iframe
    first_iframe = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH, '//*[@id="ext-gen21"]/iframe')))
    driver.switch_to.frame(first_iframe)

    try:
        # 找到包含日期的元素
        date_divs = WebDriverWait(driver, 5).until(ec.presence_of_all_elements_located(
            (By.XPATH, '//td/div[contains(text(), "-")]')))
    except:
        return tj_data

    FBG = ''
    glycosylated_hemoglobin = ''
    waistline = ''
    target_waistline = ''

    for date_div in date_divs:
        date = date_div.text
        if str(start_date) <= str(date) <= str(end_date):
            date_div.click()  # 点击日期以进入体检详情页面

            # 切换到第二个 iframe
            second_iframe = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.XPATH, '//*[@id="ext-gen32"]/iframe')))
            driver.switch_to.frame(second_iframe)

            tj_data['体检日期'] = date

            # 身高
            element = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
                (By.XPATH, '//*[@id="EXAM1.height"]')))
            height = element.get_attribute('value')
            tj_data['身高'] = height

            # 体重
            element = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
                (By.XPATH, '//*[@id="EXAM1.weight"]')))
            weight = element.get_attribute('value')
            tj_data['体重'] = weight

            # 腰围
            element = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
                (By.XPATH, '//*[@id="EXAM1.waistline"]')))
            waistline = element.get_attribute('value')
            tj_data['腰围'] = waistline

            # 舒张压
            element = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
                (By.XPATH, '//*[@id="EXAM1.sbpL"]')))
            dbp = element.get_attribute('value')
            tj_data['舒张压'] = dbp

            # 收缩压
            element = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
                (By.XPATH, '//*[@id="EXAM1.dbpL"]')))
            sbp = element.get_attribute('value')
            tj_data['收缩压'] = sbp

            # 运动习惯
            sport_frequency = 0
            sport_time = 0
            element = WebDriverWait(driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, '//*[@id="examExCycle4"]')))
            if element.is_selected():
                pass
            else:
                element = WebDriverWait(driver, 10).until(
                    ec.visibility_of_element_located((By.XPATH, '//*[@id="examExCycle1"]')))
                if element.is_selected():
                    sport_frequency = 7
                else:
                    sport_frequency = random.randint(1, 6)

                element = WebDriverWait(driver, 10).until(
                    ec.visibility_of_element_located((By.XPATH, f'//*[@id="examExTime"]'))
                )
                sport_time = element.get_attribute('value')

            tj_data['运动次数'] = sport_frequency

            tj_data['运动时间'] = sport_time

            # 吸烟量
            element = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
                (By.XPATH, '//*[@id="examSmCount"]')))
            smoke_amount = element.get_attribute('value')
            if smoke_amount == '':
                smoke_amount = 0
            tj_data['日吸烟量'] = smoke_amount

            # 饮酒量
            element = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
                (By.XPATH, '//*[@id="examDkCount"]')))
            drink_amount = element.get_attribute('value')
            if drink_amount == '':
                drink_amount = 0
            tj_data['日饮酒量'] = drink_amount

            # 饮食习惯、摄盐情况
            salt = "轻"
            element = WebDriverWait(driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, '//*[@id="examFoodHabit4"]')))
            if element.is_selected():
                salt = "重"
            tj_data['摄盐情况'] = salt

            # 心率
            element = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
                (By.XPATH, '//*[@id="EXAM2.examHeartRate"]')))
            target_heart_rate = element.get_attribute('value')
            tj_data['心率'] = target_heart_rate

            # 空腹血糖
            element = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
                (By.XPATH, '//*[@id="EXAM3.fbg"]')))
            FBG = element.get_attribute('value')

            # 糖化血红蛋白
            element = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
                (By.XPATH, '//*[@id="EXAM3.ghbaic"]')))
            glycosylated_hemoglobin = element.get_attribute('value')
            break

    tj_data['空腹血糖'] = FBG
    tj_data['糖化血红蛋白'] = glycosylated_hemoglobin

    tj_data['腰围'] = waistline

    return tj_data

