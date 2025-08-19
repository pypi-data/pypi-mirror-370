import random
import time

from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from comment.write_excle import excel_append
from compements.assemblies.introducing_medication import introducing_medication
from compements.tool import update_exercise_time, update_staple_food, hypertension_assessment, diabetes_assessment


def new_follow_up(driver, new_sf_data, sfzh, record, headers):
    if "随访方式" in headers:
        sf_method = record['随访方式']
    else:
        sf_method = "门诊"

    driver.switch_to.default_content()

    WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH, "//li[contains(text(),'慢病随访')]"))).click()
    time.sleep(1)

    # 切换到第一个 iframe
    first_iframe = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH, '//*[@id="ext-gen21"]/iframe')))
    driver.switch_to.frame(first_iframe)

    # 切换到第二个 iframe
    second_iframe = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH, '//*[@id="ext-gen32"]/iframe')))
    driver.switch_to.frame(second_iframe)

    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="document_title"]/tbody/tr/td[3]/img')))
    element.click()

    # 获取慢病类型
    element = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH, '//*[@id="divOne_1"]/tbody/tr[2]/td/input[1]')))
    mb_type = element.get_attribute('value')

    # 获取人群分类
    element = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH, '//*[@id="divOne_1"]/tbody/tr[1]/td/input[4]')))
    mb_group = element.get_attribute('value')

    # 随访日期
    follow_date = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="dateCreated"]')))
    driver.execute_script("document.getElementById('dateCreated').removeAttribute('readonly');")
    follow_date.clear()
    follow_date.send_keys(new_sf_data['随访日期'])

    # 是否加入国家标准版
    WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH,
                                        "//td[contains(text(),'是否加入国家标准版')]//input[@name='isGj' and @value='1']"))).click()
    time.sleep(.5)

    # 随访方式
    wait = WebDriverWait(driver, 10)  # 等待最多10秒
    select_element = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="followWay"]')))
    select = Select(select_element)
    select.select_by_visible_text(sf_method)

    # 无症状处理
    sentences = {}
    if "高血压" in mb_type and "糖尿病" not in mb_type:
        # 高血压患者适用的句子
        sentences = {
            1: "患者无头晕、视物模糊等不适，按时服药，未出现药物不良反应，血压稳定，饮食作息有规律。",
            2: "患者无耳鸣、视物模糊等症状，定期服药，无药物副作用，血压稳定，生活起居规律。",
            3: "患者无头痛、眩晕等不适，服药规律，无药物过敏反应，血压保持平稳，生活作息有条不紊。",
            4: "患者无四肢乏力、胸痛等不适，按时服用降压药，未出现不良反应，血压控制理想，作息正常。",
            5: "患者无浮肿、乏力等症状，遵医嘱服药，未出现药物副作用，血压控制平稳，饮食搭配合理。",
            6: "患者无呼吸困难、咳嗽等不适，定期服药，无药物不耐受，血压保持平稳，生活起居规律。",
            7: "患者无头晕、恶心等不适，按时服用降压药，无药物副作用，血压控制在目标范围内，作息健康。",
            8: "患者无胸痛、心悸等症状，遵医嘱用药，无药物不耐受反应，血压保持良好，饮食睡眠有规律。",
            9: "患者无便秘、腹胀等不适，按时服用降压药，未出现副作用，血压维持在正常水平，饮食睡眠正常。",
        }
    elif "糖尿病" in mb_type and "高血压" not in mb_type:
        # 糖尿病患者适用的句子
        sentences = {
            1: "患者无口干、多饮等症状，遵医嘱服药，无药物副作用，血糖波动不大，饮食规律。",
            2: "患者无多饮、多尿等症状，遵医嘱服药，无药物过敏现象，血糖监测平稳，作息规律。",
            3: "患者无腹痛、腹胀等不适，按时服用降糖药，未出现副作用，血糖控制在正常范围，作息良好。",
            4: "患者无手足麻木、四肢无力等症状，服药依从性好，无药物不良反应，血糖管理较好，作息稳定。",
            5: "患者无头晕、视物模糊等症状，服药规律，无药物过敏反应，血糖水平平稳，饮食习惯良好。",
            6: "患者无恶心、呕吐等症状，服药依从性良好，无明显药物不良反应，血糖水平正常，饮食健康。",
            7: "患者无消化不良、食欲下降等不适，服药依从性良好，无药物过敏反应，血糖控制理想，饮食睡眠良好。",
            8: "患者无皮疹、瘙痒等症状，服药规律，无不良反应，血糖管理得当，饮食清淡，作息正常。",
            9: "患者无四肢乏力、胸痛等不适，按时服用降糖药，未出现不良反应，血糖保持稳定，生活规律。",
            10: "患者无晕厥、乏力等症状，按时服药，未出现药物不耐受反应，血糖保持稳定，睡眠充足。"
        }
    elif "高血压" in mb_type and "糖尿病" in mb_type:
        # 高血压和糖尿病患者都适用的句子
        sentences = {
            1: "患者无乏力、四肢麻木等不适，遵医嘱用药，无明显不良反应，血压和血糖控制稳定，睡眠质量较好。",
            2: "患者无恶心、呕吐等不适，服药依从性良好，未出现不良反应，血压和血糖控制良好，饮食习惯规律。",
            3: "患者无便秘、腹泻等症状，定期服药，无明显药物不良反应，血压和血糖保持平稳，睡眠情况正常。",
            4: "患者无头痛、眼花等不适，服药依从性高，未出现不良反应，血压和血糖保持平稳，生活作息有序。",
            5: "患者无头晕、视物模糊等不适，按时服药，未出现药物不良反应，血压和血糖保持在理想范围内，作息健康。",
            6: "患者无胸部不适、呼吸困难，服药规范，无药物不良反应，血压和血糖控制良好，睡眠状态佳。",
            7: "患者无四肢麻木、乏力等症状，按时服药，无药物副作用，血压和血糖控制在理想范围内，作息规律。",
            8: "患者无晕厥、恶心等症状，遵医嘱用药，无不良反应，血压和血糖控制较好，饮食清淡，作息正常。",
            9: "患者无头痛、眩晕等不适，服药规律，无药物不良反应，血压和血糖管理稳定，生活起居有条不紊。",
            10: "患者无乏力、头晕等症状，服药规律，无明显不良反应，血压和血糖保持在目标范围，作息健康。"
        }
    random_hypertension_sentence = sentences[random.randint(1, 9)]

    wait = WebDriverWait(driver, 10)
    checkbox = wait.until(ec.element_to_be_clickable((By.XPATH,
                                                      "//label[contains(text(), '无症状')]/preceding-sibling::input")))
    if not checkbox.is_selected():
        checkbox.click()

        try:
            element = WebDriverWait(driver, 3).until(
                ec.visibility_of_element_located((By.XPATH, '//span[contains(text(), "是否确认清除其他症状")]')))
            print("是否确认清除其他症状")
            time.sleep(.5)
            yes_element = WebDriverWait(driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, '//button[contains(text(), "是")]')))
            driver.execute_script("arguments[0].click();", yes_element)
        except TimeoutException:
            pass

    # checkbox = wait.until(ec.element_to_be_clickable((By.XPATH,
    #                                                   "//label[contains(text(), '其他')]/preceding-sibling::input")))
    #
    # if not checkbox.is_selected():
    #     checkbox.click()
    #     input_element = WebDriverWait(driver, 10).until(
    #         ec.visibility_of_element_located((By.XPATH, "//label[contains(text(), '其他')]/following-sibling::textarea")))
    #
    #     time.sleep(1)
    #
    #     # input_element.clear()
    #     # input_element.send_keys(random_hypertension_sentence)
    #     # 使用 JavaScript 填充文本框
    #     driver.execute_script("arguments[0].value = arguments[1];", input_element, random_hypertension_sentence)

    # 收缩压sbp
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="sbp"]')))
    element.clear()
    sbp = str(int(float(new_sf_data['收缩压'])))
    element.send_keys(sbp)

    # 舒张压dbp
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="dbp"]')))
    element.clear()
    dbp = str(int(float(new_sf_data['舒张压'])))
    element.send_keys(dbp)

    # 身高
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="height"]')))
    element.clear()
    element.send_keys(new_sf_data['身高'])

    # 体重
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="weightCur"]')))
    element.clear()
    element.send_keys(new_sf_data['体重'])

    # 目标体重
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="bmiCur"]')))
    bmi = element.get_attribute('value')
    bmi = float(bmi)

    target_weight = new_sf_data['体重']
    if bmi >= 24:
        target_weight = new_sf_data['体重'] - random.randint(1, 2)
    elif bmi < 18.5:
        target_weight = new_sf_data['体重'] + random.randint(1, 2)
    elif bmi >= 28:
        target_weight = new_sf_data['体重'] - random.randint(2, 3)
    target_weight = str(round(float(target_weight), 1))
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="weightTar"]')))
    element.clear()
    element.send_keys(target_weight)

    # 心率
    try:
        element = WebDriverWait(driver, 3).until(
            ec.visibility_of_element_located((By.XPATH, '//*[@id="heartRateCur"]')))
        element.clear()
        element.send_keys(new_sf_data['心率'])

        # 目标心率
        element = WebDriverWait(driver, 3).until(
            ec.visibility_of_element_located((By.XPATH, '//*[@id="heartRateTar"]')))
        element.clear()
        element.send_keys(new_sf_data['心率'])
    except:
        pass

    # 其他体征
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="otherSign"]')))
    element.clear()
    # waist = new_sf_data['腰围']
    # other_signs = f'腰围:{waist}cm,双下肢未见水肿'
    # element.send_keys(other_signs)

    # 日吸烟量
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="smAmountCur"]')))
    element.clear()
    element.send_keys(new_sf_data['日吸烟量'])

    target_smoke_amount = 0
    # 目标日吸烟量
    if int(new_sf_data['日吸烟量']) >= 1:
        target_smoke_amount = int(new_sf_data['日吸烟量']) - 1
    target_smoke_amount = str(target_smoke_amount)

    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="smAmountTar"]')))
    element.clear()
    element.send_keys(target_smoke_amount)

    # 日饮酒量
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="dkAmountCur"]')))
    element.clear()
    element.send_keys(new_sf_data['日饮酒量'])

    # 目标日饮酒量
    target_drink_amount = 0
    if int(new_sf_data['日饮酒量']) >= 5:
        target_drink_amount = int(new_sf_data['日饮酒量']) - random.randint(2, 3)
    target_drink_amount = str(target_drink_amount)
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="dkAmountTar"]')))
    element.clear()
    element.send_keys(target_drink_amount)

    # 运动次数
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="exCycleCur"]')))
    element.clear()
    element.send_keys(new_sf_data['运动次数'])

    # 目标运动次数
    target_sport_times = 7
    if int(new_sf_data['运动次数']) < 7:
        target_sport_times = int(new_sf_data['运动次数']) + 1
    target_sport_times = str(target_sport_times)

    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="exCycleTar"]')))
    element.clear()
    element.send_keys(target_sport_times)

    # 运动时间
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="exTimeCur"]')))
    element.clear()
    element.send_keys(new_sf_data['运动时间'])

    # 目标运动时间
    target_sport_time = update_exercise_time(sfzh, new_sf_data['运动时间'], bmi)

    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="exTimeTar"]')))
    element.clear()
    element.send_keys(target_sport_time)

    # 摄盐情况
    try:
        salt = new_sf_data['摄盐情况']
        if salt == '重':
            element = WebDriverWait(driver, 3).until(
                ec.visibility_of_element_located((By.XPATH, '//*[@id="stAmountCurTypeCur3"]')))
            element.click()
        else:
            element = WebDriverWait(driver, 3).until(
                ec.visibility_of_element_located((By.XPATH, '//*[@id="stAmountCurTypeCur1"]')))
            element.click()
    except:
        pass

    # 建议摄盐情况
    try:
        element = WebDriverWait(driver, 3).until(
            ec.visibility_of_element_located((By.XPATH, '//*[@id="stAmountCurTypeTar1"]')))
        element.click()
    except:
        pass

    # 主食量
    try:
        element = WebDriverWait(driver, 3).until(
            ec.visibility_of_element_located((By.XPATH, '//*[@id="fhAmountCur"]')))
        element.clear()
        element.send_keys(new_sf_data['主食量'])

        # 目标主食量
        target_fh_amount = update_staple_food(bmi, new_sf_data['主食量'])
        element = WebDriverWait(driver, 3).until(
            ec.visibility_of_element_located((By.XPATH, '//*[@id="fhAmountTar"]')))
        element.clear()
        element.send_keys(target_fh_amount)
    except:
        pass

    # 空腹血糖
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="fbg"]')))

    with open("./执行结果/env.txt", 'r', encoding='utf-8') as file:
        content = file.readlines()
    # 使用 split() 方法分割字符串
    place = content[6].replace("：", ":").split(":")[1]
    place = place.strip()
    print("无糖尿病是否录入空腹血糖:", place)
    if place == "否":
        element.clear()
        # 方法1：直接执行JS清空并触发事件（推荐）
        js_script = """
            var input = document.getElementById('fbg');
            input.value = '';
            // 创建并触发keyup事件
            var event = new Event('keyup');
            input.dispatchEvent(event);
        """
        driver.execute_script(js_script)
        # 执行JS清空隐藏输入框的值
        driver.execute_script("document.getElementById('fbg_hidden').value = '';")
    if place == '是':
        element.clear()
        element.send_keys(new_sf_data['空腹血糖'])
    if "糖尿病" in mb_type:
        element.clear()
        element.send_keys(new_sf_data['空腹血糖'])

    # 餐后血糖
    try:
        element = WebDriverWait(driver, 3).until(
            ec.visibility_of_element_located((By.XPATH, '//*[@id="pbg"]')))
        element.clear()
        element.send_keys("未查")
    except:
        pass

    # 糖化血红蛋白
    try:
        element = WebDriverWait(driver, 3).until(
            ec.visibility_of_element_located((By.XPATH, '//*[@id="hba1c"]')))
        element.clear()
        element.send_keys("未查")

        element = WebDriverWait(driver, 3).until(
            ec.visibility_of_element_located((By.XPATH, '//*[@id="hba1cDate"]')))
        element.clear()
    except:
        pass

    # TC
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="tc"]'))).clear()
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="tc"]'))).send_keys('未查')

    # TG
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="tg"]'))).clear()
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="tg"]'))).send_keys('未查')

    # HDL-C
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="hdlC"]'))).clear()
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="hdlC"]'))).send_keys(
        '未查')

    # LDL-C
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="ldlC"]'))).clear()
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="ldlC"]'))).send_keys(
        '未查')

    # BUN
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="bun"]'))).clear()
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="bun"]'))).send_keys(
        '未查')

    # Cr
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="cr"]'))).clear()
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="cr"]'))).send_keys('未查')

    # 肌酐清除率
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="ccr"]'))).clear()
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="ccr"]'))).send_keys(
        '未查')

    # 尿检
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="uran"]'))).clear()
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="uran"]'))).send_keys(
        '未查')

    # 尿微量白蛋白
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="malb"]'))).clear()
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="malb"]'))).send_keys(
        '未查')

    # 心电图
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="ecg"]'))).clear()
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="ecg"]'))).send_keys(
        '未查')

    # 眼底
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="fundusOculi"]'))).clear()
    WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="fundusOculi"]'))).send_keys('未查')

    # 其他辅助检查
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="otherTest"]'))).clear()
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="otherTest"]'))).send_keys(
        '未查')

    # 是否咳嗽、咳痰≥2周
    WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="isCough2"]'))).click()
    time.sleep(.5)

    # 是否痰中带血或咯血
    WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="isHemoptysis2"]'))).click()
    time.sleep(.5)

    # 患者姓名
    people_element = WebDriverWait(driver, 10).until(
            ec.visibility_of_element_located((By.XPATH, '//*[@id="divOne_1"]/tbody/tr[1]/td/input[1]')))
    people_name = people_element.get_attribute('value')
    print("患者姓名：", people_name)

    # 随访人
    doctor_element = WebDriverWait(driver, 10).until(
            ec.visibility_of_element_located((By.XPATH, '//*[@id="followPerson"]')))
    doctor_name = doctor_element.get_attribute('value')
    print("随访人：", doctor_name)
    # 评估
    pg = ''
    if '高血压' in mb_type:
        # 判断血压是否控制满意
        hypertension_result = hypertension_assessment(dbp, sbp, sfzh, new_sf_data['随访日期'], people_name, doctor_name)
        pg = pg + hypertension_result + ','
        if hypertension_result == "高血压（血压控制不达标）":
            print("高血压（血压控制不达标）")
            if '高血压' in mb_type and '糖尿病' not in mb_type:
                element = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((
                    By.XPATH, '//*[@id="divOne_1"]/tbody/tr[4]/td/label[2]')))
                driver.execute_script("arguments[0].scrollIntoView();", element)
                # element.click()
                driver.execute_script("arguments[0].click();", element)
            elif '高血压' in mb_type and '糖尿病' in mb_type:
                element = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((
                    By.XPATH, '//*[@id="divOne_1"]/tbody/tr[4]/td/label[2]')))
                driver.execute_script("arguments[0].scrollIntoView();", element)
                # element.click()
                driver.execute_script("arguments[0].click();", element)

    if '糖尿病' in mb_type:
        diabetes_result = diabetes_assessment(new_sf_data['空腹血糖'], sfzh, new_sf_data['随访日期'], people_name, doctor_name)
        pg = pg + diabetes_result + ','
        if diabetes_result == "糖尿病（血糖控制不达标）":
            print("糖尿病（血糖控制不达标）")
            if '高血压' not in mb_type and '糖尿病' in mb_type:
                element = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((
                    By.XPATH, '//*[@id="divOne_1"]/tbody/tr[4]/td/label[2]')))
                driver.execute_script("arguments[0].scrollIntoView();", element)
                # element.click()
                driver.execute_script("arguments[0].click();", element)
            elif '高血压' in mb_type and '糖尿病' in mb_type:
                element = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((
                    By.XPATH, '//*[@id="divOne_1"]/tbody/tr[5]/td/label[2]')))
                driver.execute_script("arguments[0].scrollIntoView();", element)
                # element.click()
                driver.execute_script("arguments[0].click();", element)

    if '冠心病' in mb_type:
        pg = pg + '冠心病（控制平稳）' + ','
    if "脑卒中" in mb_type:
        pg = pg + '脑卒中（控制平稳）' + ','

    # if new_sf_data['日吸烟量'] != 0:
    #     pg = pg + '吸烟' + ','
    # if new_sf_data['日饮酒量'] != 0:
    #     pg = pg + '饮酒' + ','
    if 24 <= bmi < 28:
        pg = pg + '超重' + ','
    if bmi >= 28:
        pg = pg + '肥胖' + ','
    # if new_sf_data['运动次数'] == 0 or new_sf_data['运动时间'] == 0:
    #     pg = pg + '运动未达标' + ','

    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="assess"]'))).clear()
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="assess"]'))).send_keys(pg)

    # 生活指导建议项
    advice_items = []
    # 戒烟
    if new_sf_data['日吸烟量'] != 0:
        advice_items.append('戒烟')
    # 控制饮酒
    if new_sf_data['日饮酒量'] != 0:
        advice_items.append('限酒')
    # 饮食调节
    if '无偏好' not in mb_group:
        advice_items.append(
            '饮食调节：以低盐低脂为主，适量胆固醇，避免饱和脂肪，多吃蔬果、高蛋白食物，用植物油替代动物油。')
    # 适量运动
    if '残疾人' not in mb_group and new_sf_data['运动时间'] == 0:
        advice_items.append('适量运动，循序渐进，确保充足睡眠')
    # 锻炼建议（针对超重或肥胖）
    if bmi >= 24:
        advice_items.append(f'每天锻炼{target_sport_time}分钟左右，循序渐进，避免疲劳，注意减轻体重')
        # if new_sf_data['运动时间'] == 0:
        #     sport_time = new_sf_data['运动时间']
        #     advice_items.append(f'每天锻炼{target_sport_time}分钟左右，循序渐进，避免疲劳，注意减轻体重')
        # elif new_sf_data['运动时间'] == target_sport_time:
        #     advice_items.append(f'{target_sport_time}分钟左右，循序渐进，避免疲劳，注意减轻体重')
        # else:
        #     sport_time = new_sf_data['运动时间']
        #     advice_items.append(f'每天锻炼{sport_time}~{target_sport_time}分钟，循序渐进，避免疲劳，注意减轻体重')
    # 老年人特别建议
    if '老年人' in mb_group:
        advice_items.extend([
            '预防跌倒',
            '预防骨质疏松',
            '预防意外伤害及自救',
            '接种流感疫苗、肺炎疫苗'
        ])
    # 规律用药
    advice_items.append('规律用药，注意剂量、用法、时间，勿擅自调整药物。')
    # 卫生习惯
    advice_items.extend(['勤洗手', '出门戴口罩', '多开窗通风'])
    # 定期就医与复诊
    advice_items.append('如有不适及时就医，定期复诊。')

    # 生成最终生活指导建议
    life_suggestions = '\n'.join([f'{i + 1}. {item}' for i, item in enumerate(advice_items)])

    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="lifestyle"]'))).clear()
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="lifestyle"]'))).send_keys(
        life_suggestions)

    # 医生建议
    doctor_advice = ''
    if "高血压" in mb_type and "糖尿病" not in mb_type:
        doctor_advice = '1.定期监测血压、足背动脉;\n'
    elif '糖尿病' in mb_type and "高血压" not in mb_type:
        doctor_advice = '1.定期监测血糖、足背动脉;\n'
    elif "高血压" in mb_type and "糖尿病" in mb_type:
        doctor_advice = '1.定期监测血压、血糖、足背动脉;\n'

    doctor_advice = doctor_advice + '2.规律用药，注意药物剂量、用法、时间、药效等，勿自行更改药物剂量或停药.\n3.低盐低脂饮食，避免血压剧烈波动，适量运动，保证充足睡眠;\n4.预防并发症，如有不适立即就医，定期复诊;\n5.若有异常建议上级医院就诊\n'
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="suggest"]'))).clear()
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="suggest"]'))).send_keys(
        doctor_advice)

    # 点击用药情况
    try:
        medication_element = WebDriverWait(driver, 3).until(
            ec.visibility_of_element_located((By.XPATH, '//font[contains(text(), "用  药  情  况")]')))
    except TimeoutException:
        medication_element = WebDriverWait(driver, 3).until(
            ec.visibility_of_element_located((By.XPATH, '//font[contains(text(), "用药情况")]')))
    driver.execute_script("arguments[0].click();", medication_element)
    time.sleep(1.5)

    try:
        element = WebDriverWait(driver, 5).until(
            ec.visibility_of_element_located((By.XPATH, '//span[contains(text(), "需要先")]')))
        print("需要先保存随访，才能引入用药")
        time.sleep(.5)
        yes_element = WebDriverWait(driver, 10).until(
            ec.visibility_of_element_located((By.XPATH, '//button[contains(text(), "是")]')))
        # driver.execute_script("arguments[0].click();", yes_element)
        driver.execute_script("""
            var element = arguments[0];
            var clickEvent = new MouseEvent('click', { bubbles: true });
            element.dispatchEvent(clickEvent);
            element.dispatchEvent(clickEvent);
        """, yes_element)

        try:
            # 获取本季度已做过慢病随访，是否继续保存
            with open("./执行结果/env.txt", 'r', encoding='utf-8') as file:
                content = file.readlines()
            # 使用 split() 方法分割字符串
            yes = content[5].replace("：", ":").split(":")[1].strip()

            element = WebDriverWait(driver, 3).until(
                ec.visibility_of_element_located((By.XPATH, "//span[contains(text(),'本季度已做过慢病随访')]")))
            print("获取本季度已做过慢病随访，是否继续保存:", yes)

            element_yes = WebDriverWait(driver, 3).until(
                ec.visibility_of_element_located((By.XPATH, f"//button[text()='{yes}']")))
            driver.execute_script("arguments[0].click();", element_yes)

            with open("./执行结果/本季度已做过慢病随访.txt", 'a+', encoding='utf-8') as a:
                a.write(f"{new_sf_data}-本季度已做过慢病随访，是否继续保存:{yes}\n")

            if yes == '否':
                return False

        except TimeoutException:
            pass

        WebDriverWait(driver, 5).until(
            ec.visibility_of_element_located((By.XPATH, "//button[text()='确定']"))).click()
        try:
            element = WebDriverWait(driver, 5).until(
                ec.visibility_of_element_located((By.XPATH, '//span[contains(text(), "是否加入到个人服务计划中")]')))
            WebDriverWait(driver, 5).until(
                ec.visibility_of_element_located((By.XPATH, '//button[contains(text(), "否")]'))).click()
        except:
            pass
        # 点击用药情况
        try:
            medication_element = WebDriverWait(driver, 3).until(
                ec.visibility_of_element_located((By.XPATH, '//font[contains(text(), "用  药  情  况")]')))
        except TimeoutException:
            medication_element = WebDriverWait(driver, 3).until(
                ec.visibility_of_element_located((By.XPATH, '//font[contains(text(), "用药情况")]')))
        driver.execute_script("arguments[0].click();", medication_element)
    except:
        pass

    # 开始引入用药
    result = introducing_medication(driver, mb_type, new_sf_data)
    if result is False or result == set():
        print(f"{sfzh}---没有引入任何药品")
        with open("./执行结果/没有引入任何药品.txt", 'a+', encoding='utf-8') as file:
            file.write(f"{sfzh}---没有引入任何药品\n")
    time.sleep(1.5)

    # 点击保存
    save_button = WebDriverWait(driver, 30).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="saveAction"]')))
    driver.execute_script("arguments[0].click();", save_button)

    try:
        # 获取本季度已做过慢病随访，是否继续保存
        with open("./执行结果/env.txt", 'r', encoding='utf-8') as file:
            content = file.readlines()
        # 使用 split() 方法分割字符串
        yes = content[5].replace("：", ":").split(":")[1].strip()

        element = WebDriverWait(driver, 3).until(
            ec.visibility_of_element_located((By.XPATH, "//span[contains(text(),'本季度已做过慢病随访')]")))
        print("获取本季度已做过慢病随访，是否继续保存:", yes)

        element_yes = WebDriverWait(driver, 3).until(
            ec.visibility_of_element_located((By.XPATH, f"//button[text()='{yes}']")))
        driver.execute_script("arguments[0].click();", element_yes)

        with open("./执行结果/本季度已做过慢病随访.txt", 'a+', encoding='utf-8') as a:
            a.write(f"{new_sf_data}-本季度已做过慢病随访，是否继续保存:{yes}\n")

        if yes == '否':
            return False

    except TimeoutException:
        pass

    try:
        element = WebDriverWait(driver, 3).until(
            ec.visibility_of_element_located((By.XPATH, "//span[contains(text(),'药品名称不能为空或无')]")))
        WebDriverWait(driver, 3).until(
            ec.visibility_of_element_located((By.XPATH, "//button[text()='确定']"))).click()
        excel_append("执行结果/异常名单.xlsx", "身份证号", sfzh + '\t', "异常原因", "药品名称不能为空或无无法保存")
        return False
    except TimeoutException:
        pass

    try:
        element = WebDriverWait(driver, 120).until(
            ec.visibility_of_element_located((By.XPATH, "//span[contains(text(),'保存成功')]")))
        WebDriverWait(driver, 120).until(
            ec.visibility_of_element_located((By.XPATH, "//button[text()='确定']"))).click()
        print(f'{new_sf_data}-随访保存成功')
        excel_append("执行结果/成功名单.xlsx", '身份证号', sfzh, '成功',
                     f"慢病随访新建成功-{new_sf_data}, 引入用药-{result}")
    except TimeoutException:
        print(f'{new_sf_data}-随访保存超时')
        excel_append("执行结果/异常名单.xlsx", "身份证号", sfzh + '\t', "异常原因", "保存超时-需验证重跑")
