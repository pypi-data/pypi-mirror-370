import datetime
import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from compements.tool import parse_date


def check_sf_date(driver):

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

    # 获取已有随访的日期
    sf_sj = []

    driver.switch_to.default_content()

    WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH, "//dt[contains(text(),'随访服务')]"))).click()
    time.sleep(1)
    try:
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, "//li[contains(text(),'慢病随访')]"))).click()
    except:
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, "//dt[contains(text(),'随访服务')]"))).click()
        time.sleep(1)
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, "//li[contains(text(),'慢病随访')]"))).click()
    time.sleep(1)

    # 切换到第一个 iframe
    first_iframe = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH, '//*[@id="ext-gen21"]/iframe')))
    driver.switch_to.frame(first_iframe)

    for year in range(start_year, end_year + 1):
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
        for element in elements:
            year = year
            month_and_day = element.text.split("-")
            day = int(month_and_day[1].split('(')[0])
            month = int(month_and_day[0])
            # 构造日期
            date_string = "{}-{}-{}".format(year, month, day)
            sf_sj.append(date_string)

    return sf_sj

