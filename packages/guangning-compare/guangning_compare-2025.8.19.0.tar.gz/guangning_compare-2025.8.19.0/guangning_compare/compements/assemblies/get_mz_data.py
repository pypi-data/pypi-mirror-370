import datetime
import re
import time
import random

from selenium.common import StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from comment.check_element import check_element
from compements.tool import safe_find_element


def adjust_values(new_data, all_previous_data):
    keys_to_adjust = ['体重', '心率', '收缩压', '舒张压']

    for key in keys_to_adjust:
        if key in new_data:
            while any(key in prev_data and new_data[key] == prev_data[key] for prev_data in all_previous_data):
                if key == '体重':
                    new_data[key] += random.choice([-1, 1])
                elif key == '心率':
                    new_data[key] += random.choice([-2, -1, 1, 2])
                elif key == '收缩压':
                    new_data[key] += random.choice([-3, -2, -1, 1, 2, 3])
                elif key == '舒张压':
                    new_data[key] += random.choice([-2, -1, 1, 2])

                # 确保值在合理范围内
                if key == '体重':
                    new_data[key] = max(40, min(new_data[key], 200))  # 假设体重范围40-200kg
                elif key == '心率':
                    new_data[key] = max(40, min(new_data[key], 120))  # 假设脉搏范围40-120次/分
                elif key == '收缩压':
                    new_data[key] = max(90, min(new_data[key], 180))  # 假设收缩压范围90-180mmHg
                elif key == '舒张压':
                    new_data[key] = max(60, min(new_data[key], 110))  # 假设舒张压范围60-110mmHg

    return new_data


def get_mz_data(driver, choice_dates):
    # 获取机构名称
    with open("./执行结果/env.txt", 'r', encoding='utf-8') as file:
        content = file.readlines()
    # 使用 split() 方法分割字符串
    place = content[4].replace("：", ":").split(":")[1].strip()

    choice_dates = sorted(choice_dates, key=lambda x: x, reverse=True)
    result = []
    driver.switch_to.default_content()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'门诊服务')]"))).click()

    # 切换到第一个 iframe
    first_iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="ext-gen21"]/iframe')))
    driver.switch_to.frame(first_iframe)

    # 使用一个无限循环，直到找不到元素
    while True:
        try:
            # 如果找不到元素，break跳出循环
            if not check_element(driver):
                break
        except:
            break
    time.sleep(1.5)
    page_number = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="ext-comp-1006"]'))).text
    # 获取总页数
    count_number = re.findall(r'\d+', page_number)
    processed_dates = set()
    print("门诊总页数:", count_number)

    for choice_date in choice_dates:
        found_date = False

        for page_index in range(0, int(count_number[0])):
            try:
                WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '/html/body/div[1]/div/div[1]/div/div[1]/div[2]/div/child::div')))

                div_elements = WebDriverWait(driver, 20).until(
                    EC.visibility_of_all_elements_located(
                        (By.XPATH, '/html/body/div[1]/div/div[1]/div/div[1]/div[2]/div/child::div')
                    )
                )
            except Exception as e:
                print(f'没有门诊记录')
                return result

            for j in range(1, len(div_elements) + 1):
                # 获取门诊机构名称
                try:
                    element = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located(
                            (By.XPATH, f'//*[@id="ext-gen22"]/div[{str(j)}]/table/tbody/tr[1]/td[3]/div'))
                    )
                    name = element.text
                except StaleElementReferenceException:
                    # 如果元素过时，重新定位
                    element = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located(
                            (By.XPATH, f'//*[@id="ext-gen22"]/div[{str(j)}]/table/tbody/tr[1]/td[3]/div'))
                    )
                    name = element.text
                if place in name:
                    # 获取门诊日期
                    try:
                        element = WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located(
                                (By.XPATH, f'//*[@id="ext-gen22"]/div[{str(j)}]/table/tbody/tr[1]/td[2]/div'))
                        )
                        date = element.text
                    except StaleElementReferenceException:
                        # 如果元素过时，重新定位
                        element = WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located(
                                (By.XPATH, f'//*[@id="ext-gen22"]/div[{str(j)}]/table/tbody/tr[1]/td[2]/div'))
                        )
                        date = element.text

                    if choice_date == date and date not in processed_dates:

                        element = WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located(
                                (By.XPATH,
                                 f'//*[@id="ext-gen22"]/div[{str(j)}]/table/tbody/tr[1]/td[2]/div')))
                        ActionChains(driver).double_click(element).perform()
                        time.sleep(1)

                        try:
                            element = WebDriverWait(driver, 10).until(
                                EC.visibility_of_element_located(
                                    (By.XPATH, f'/html/body/div[1]/div/div[1]/div/div[1]/div[2]/div/div[{str(j)}]/table/tbody/tr[2]/td/div/div[1]'))
                            )
                            needData = element.text
                        except StaleElementReferenceException:
                            # 如果元素过时，重新定位
                            element = WebDriverWait(driver, 10).until(
                                EC.visibility_of_element_located(
                                    (By.XPATH, f'/html/body/div[1]/div/div[1]/div/div[1]/div[2]/div/div[{str(j)}]/table/tbody/tr[2]/td/div/div[1]'))
                            )
                            needData = element.text
                        ActionChains(driver).double_click(element).perform()
                        time.sleep(1)

                        # pattern = r'(身高|脉搏|舒张压|体温|收缩压|体重|空腹血糖):(\d+)'
                        pattern = r'(身高|脉搏|舒张压|体温|收缩压|体重|空腹血糖)[:：](\d+)'
                        matches = re.findall(pattern, needData)
                        my_dict = {'随访日期:': choice_date}
                        for key, value in matches:
                            if key == '脉搏':
                                my_dict["心率"] = int(value)
                            else:
                                my_dict[key] = int(value)

                        # if all_previous_data:
                        #     my_dict = adjust_values(my_dict, all_previous_data)

                        result.append(my_dict)
                        processed_dates.add(date)
                        # all_previous_data.append(my_dict.copy())
                        found_date = True
                        break
                    # if current_year not in date:
                    #     print(f"{date}不是当前年份")
                    #     found_date = True
            if found_date:
                break
            if not found_date and page_index < int(count_number[0]) - 1:
                # next_page_button = WebDriverWait(driver, 10).until(
                #     EC.element_to_be_clickable((By.XPATH, '//*[@id="ext-gen43"]'))
                # )
                # next_page_button.click()
                element = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="ext-gen43"]')))
                driver.execute_script("arguments[0].click();", element)
                # 使用一个无限循环，直到找不到元素
                while True:
                    try:
                        # 如果找不到元素，break跳出循环
                        if not check_element(driver):
                            break
                    except:
                        break

                time.sleep(1.5)

        if not found_date:
            print(f"未找到日期 {choice_date}。")

    return result

