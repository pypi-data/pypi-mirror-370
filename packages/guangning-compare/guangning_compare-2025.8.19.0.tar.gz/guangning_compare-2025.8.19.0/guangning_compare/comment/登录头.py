import datetime
import time

import ddddocr
from selenium.webdriver.support import expected_conditions as ec
from mylib.main import CustomBrowser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


def is_software_expired():
    expiration_date = datetime.date(2099, 2, 22)
    current_date = datetime.date.today()
    if current_date >= expiration_date:
        return True
    else:
        return False


def login(driver):
    with open("./文档/admin.txt", 'r', encoding='utf-8') as file:
        content = file.readlines()

    my_list = []
    for content in content:
        my_list.append(content)

    urls = my_list[0]
    account = my_list[1].strip()
    password = my_list[2].strip()
    name = my_list[3].strip()

    driver.get(urls)

    driver.maximize_window()

    time.sleep(1.5)
    try:
        driver.switch_to.alert.accept()
    except:
        pass

    try:
        driver.switch_to.alert.accept()
    except:
        pass
    try:
        time.sleep(1)
        WebDriverWait(driver, 5).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="verifyCode"]')))
        yes_verify_code(driver, account, password)
    except Exception as e:
        print("没有验证码")
        no_verifyCode(driver, account, password, name)


def yes_verify_code(driver, account, password):

    """
    查询文档中是否有验证码.txt 有的话，就跳过验证码 没有就不跳
    """
    try:
        with open("./文档/验证码.txt", 'r', encoding='utf-8') as file:
            content = file.readlines()
        print("验证码跳过")

        """
        过验证码版本
        """
        while True:
            WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="phisname"]'))).clear()
            WebDriverWait(driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, '//*[@id="phisname"]'))).send_keys(account)
            time.sleep(1)
            try:
                driver.switch_to.alert.accept()
            except:
                print('没有弹窗')
            WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="password"]'))).clear()
            WebDriverWait(driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, '//*[@id="password"]'))).send_keys(password)
            time.sleep(1)

            captcha_element = driver.find_element("id", "img")
            captcha_element.screenshot("captcha.png")

            ocr = ddddocr.DdddOcr()
            with open('captcha.png', 'rb') as f:
                img_bytes = f.read()
            res = ocr.classification(img_bytes)
            print('识别出的验证码为：' + res)
            WebDriverWait(driver, 10).until(ec.visibility_of_element_located(
                (By.XPATH, '//*[@id="verifyCode"]'))).clear()
            WebDriverWait(driver, 10).until(ec.visibility_of_element_located(
                (By.XPATH, '//*[@id="verifyCode"]'))).send_keys(res)
            time.sleep(1)
            WebDriverWait(driver, 10).until(ec.visibility_of_element_located(
                (By.XPATH, '//*[@id="submitBtn"]'))).click()

            try:
                WebDriverWait(driver, 3).until(ec.visibility_of_element_located(
                    (By.XPATH, '//span[text()="健康档案"]')))
                break
            except:
                pass

    except:
        """
        不过验证码版本
        """

        WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="phisname"]'))).send_keys(
            account)
        time.sleep(1)
        try:
            driver.switch_to.alert.accept()
        except:
            print('没有弹窗')
        WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="password"]'))).send_keys(
            password)
        time.sleep(1)
        # driver.maximize_window()
        while True:
            try:
                WebDriverWait(driver, 3).until(ec.visibility_of_element_located(
                    (By.XPATH, '//span[text()="健康档案"]')))
                break
            except:
                pass

    """
    二者共用部分
    """
    WebDriverWait(driver, 10).until(ec.visibility_of_element_located(
        (By.XPATH, '//span[text()="健康档案"]'))).click()
    try:
        WebDriverWait(driver, 5).until(
            ec.visibility_of_element_located((By.XPATH, '//*[@id="button-1005-btnIconEl"]'))).click()
    except Exception as e:
        print('没有弹窗', e)


def no_verifyCode(driver, account, password, name):

    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.ID, "j_username"))).send_keys(account)
    time.sleep(.5)

    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.ID, "j_password"))).send_keys(password)
    time.sleep(.5)
    try:
        WebDriverWait(driver, 3).until(ec.visibility_of_element_located((By.CLASS_NAME, "submit-btn"))).click()
    except:
        print('无需点击登录')
    time.sleep(.5)
    try:
        WebDriverWait(driver, 10).until(ec.presence_of_element_located(
            (By.XPATH, f'//div[contains(text(), "{name}")]'))).click()
    except:
        pass
    print('进入科室')
    try:
        driver.switch_to.alert.accept()
        driver.switch_to.alert.accept()
    except:
        pass
    WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//*[@id="dd65-ddheader"]'))).click()
    driver.close()
    time.sleep(1)
    handles = driver.window_handles
    latest_handle = handles[-1]
    driver.switch_to.window(latest_handle)
    try:
        WebDriverWait(driver, 5).until(
            ec.visibility_of_element_located((By.XPATH, '//*[@id="button-1005-btnIconEl"]'))).click()
    except Exception as e:
        pass
    driver.maximize_window()

