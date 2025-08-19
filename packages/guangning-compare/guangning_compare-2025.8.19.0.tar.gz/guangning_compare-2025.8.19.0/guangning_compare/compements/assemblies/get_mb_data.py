import random
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from compements.tool import get_drink_amount


def get_mb_data(driver):

    # 切换到第一个 iframe
    first_iframe = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH, '//*[@id="ext-gen21"]/iframe')))
    driver.switch_to.frame(first_iframe)

    mb_data = {}

    # 收缩压
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="EHRHFINDICATOR.sbpL"]')))
    sbp = element.get_attribute('value')
    mb_data['收缩压'] = sbp

    # 舒张压
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="EHRHFINDICATOR.dbpL"]')))
    dbp = element.get_attribute('value')
    mb_data['舒张压'] = dbp

    # 身高
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="EHRHFINDICATOR.height"]')))
    height = element.get_attribute('value')
    mb_data['身高'] = height

    # 体重
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="EHRHFINDICATOR.weight"]')))
    weight = element.get_attribute('value')
    mb_data['体重'] = weight

    # 腰围
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="EHRHFINDICATOR.waistline"]')))
    waistline = element.get_attribute('value')
    mb_data['腰围'] = waistline

    # 主食量
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="EHRDETAILS.fhAmount"]')))
    fh_amount = element.get_attribute('value')
    mb_data['主食量'] = fh_amount

    # 运动习惯
    sport_frequency = 0
    sport_time = 0
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="exExercise2"]')))
    if element.is_selected():
        pass
    else:
        element = WebDriverWait(driver, 10).until(
            ec.visibility_of_element_located((By.XPATH, '//*[@id="exCycle1"]')))
        if element.is_selected():
            sport_frequency = 7
        else:
            sport_frequency = random.randint(1, 6)

        sport_time = random.randint(1, 2) * 10
        for i in range(1, 4):
            element = WebDriverWait(driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, f'//*[@id="exTime{i}"]')))
            if element.is_selected():
                element = WebDriverWait(driver, 10).until(
                    ec.visibility_of_element_located((By.XPATH, f'//*[@id="exTime{i}"]/following-sibling::span[1]/label')))
                time_interval = element.text
                if time_interval == '<30分钟':
                    sport_time = random.randint(1, 2) * 10
                elif time_interval == '30-60分钟':
                    sport_time = random.randint(3, 6) * 10
                elif time_interval == '1小时以上':
                    sport_time = random.randint(7, 9) * 10
                break

    mb_data['运动次数'] = sport_frequency

    mb_data['运动时间'] = sport_time

    # 吸烟情况
    smoking_number = 0
    for i in range(1, 4):
        element = WebDriverWait(driver, 10).until(
            ec.visibility_of_element_located((By.XPATH, f'//*[@id="smAmount{i}"]')))
        if element.is_selected():
            element = WebDriverWait(driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, f'//*[@id="smAmount{i}"]/following-sibling::span[1]/label')))
            smoking_status = element.text
            if smoking_status == '偶尔（<3支/周）':
                smoking_number = random.randint(1, 2)
            elif smoking_status == '少量（1-4支/日）':
                smoking_number = random.randint(2, 4)
            elif smoking_status == '经常（≥5支/日）':
                smoking_number = random.randint(5, 8)
            break
    quit_smoking_element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="smSmoking3"]')))
    if quit_smoking_element.is_selected():
        smoking_number = 0
    mb_data['日吸烟量'] = smoking_number

    # 饮酒情况
    drink_amount = 0
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="dkDrinking2"]')))
    if element.is_selected():
        pass
    else:

        drink_type = '白酒（酒精含量≥45）'
        for i in range(1, 4):
            element = WebDriverWait(driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, f'//*[@id="dkType{i}"]')))
            if element.is_selected():
                element = WebDriverWait(driver, 10).until(
                    ec.visibility_of_element_located((By.XPATH, f'//*[@id="dkType{i}"]/following-sibling::span[1]/label')))
                drink_type = element.text
                break

        drink_number = '少量（啤酒<250-500ml/次，色酒100-150ml/次，白酒<25-50ml/次）'
        for i in range(1, 4):
            element = WebDriverWait(driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, f'//*[@id="dkAmount{i}"]')))
            if element.is_selected():
                element = WebDriverWait(driver, 10).until(
                    ec.visibility_of_element_located((By.XPATH, f'//*[@id="dkAmount{i}"]/following-sibling::span[1]/label')))
                drink_number = element.text

        # 生成饮酒量
        drink_amount = get_drink_amount(drink_type, drink_number)
    quit_drinking_element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="dkDrinking3"]')))
    if quit_drinking_element.is_selected():
        drink_amount = 0
    mb_data['日饮酒量'] = drink_amount

    # 饮食习惯、摄盐情况
    salt = "轻"
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="fhType1"]')))
    if element.is_selected():
        salt = "重"
    mb_data['摄盐情况'] = salt

    # 疾病史
    element = WebDriverWait(driver, 10).until(
            ec.visibility_of_element_located((By.XPATH, "//font[contains(text(),'既往史')]")))
    element.click()

    disease_histories = []
    try:
        records = WebDriverWait(driver, 10).until(
            ec.visibility_of_all_elements_located((By.XPATH, '//*[@id="ext-gen19"]/div'))
        )
        for index, record in enumerate(records):
            disease = record.find_element(By.XPATH, f'.//table/tbody/tr/td[2]/div').text
            diagnosis_date = record.find_element(By.XPATH, f'.//table/tbody/tr/td[3]/div').text
            description = record.find_element(By.XPATH, f'.//table/tbody/tr/td[4]/div').text

            disease_histories.append({
                '疾病': disease,
                '确诊日期': diagnosis_date,
                '描述': description
            })

        # 提取疾病名称并生成一个新列表
        diseases = [history['疾病'] for history in disease_histories]
        diseases = ','.join(diseases)
    except:
        diseases = ''
    mb_data['疾病史'] = diseases

    return mb_data

