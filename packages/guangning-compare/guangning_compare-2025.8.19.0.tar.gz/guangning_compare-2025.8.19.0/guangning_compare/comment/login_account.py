import time
from selenium import webdriver
from mylib.main import CustomBrowser
import pandas as pd
from selenium.common import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By


def login():
    """
    万达公卫登录头
    :return:driver
    """

    try:
        with open('文档/admin.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            user_id = lines[1].strip()
            password = lines[2].strip()
    except FileNotFoundError:
        print("文件不存在，请检查admin文件路径是否正确。")
    except Exception as e:
        print(f"读取env文件时发生错误：{e}")

    # driver = webdriver.Firefox()
    driver = CustomBrowser()
    driver.maximize_window()

    # 访问目标网站
    driver.get("http://172.31.68.181:8080/jkdadx/application/modules/jsp/login.jsp")

    skip = True
    try:
        # 现在可以获取所有<option>元素
        option_elements = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.XPATH, "//select[@id='userList']/option"))
        )

        if len(option_elements) > 0:
            print("有子元素存在")

            selected_option = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="userList"]/option'))
            )

            if selected_option:
                doctor_name = selected_option.text
                print(f"当前选中的是: {doctor_name}")
                skip = False
            else:
                print("没有选中任何选项")
        else:
            print("没有子元素")
    except Exception as e:
        print(f"出现错误: {e}")

    if skip is False:
        df = pd.read_excel("文档/登录账号及密码.xlsx")
        # 遍历所有行
        for index, row in df.iterrows():
            if row['医生名'] == doctor_name:
                yh_name = row['账号']
                yh_pws = row['密码']
                break
        else:
            print("没有找到对应的医生名。")

        password_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="userPwd"]'))
        )
        password_element.send_keys(yh_pws)

        print("点击登录...")
        login_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="submit"]'))
        )
        driver.execute_script("arguments[0].click();", login_element)
        if login_element.is_displayed():
            driver.execute_script("arguments[0].click();", login_element)
        else:
            print("元素不可见或不可点击")
    else:
        # 使用 JavaScript 设置输入字段的值
        element1 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="loginId"]'))
        )
        driver.execute_script(f"document.getElementById('loginId').value = '{user_id}';")

        element2 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="password"]'))
        )
        driver.execute_script(f"document.getElementById('password').value = '{password}';")

        e1 = element1.get_attribute('value')
        e2 = element2.get_attribute('value')
        print("写入的账号密码:", e1, e2)

        # 确保 licensedFlag 被设置为 LOGIN_USERNAME_PASSWORD
        driver.execute_script("document.getElementById('licensedFlag').value = 'LOGIN_USERNAME_PASSWORD';")

        # 提交表单进行登录
        driver.execute_script("doLogin();")

    # 检测是否登录成功
    while True:
        time.sleep(.5)
        try:
            # 使用find_element_by_xpath尝试找到特定的元素
            if driver.find_element(By.XPATH, '//*[@id="topFrame"]') is not None:
                print("登录成功")
                break  # 如果找到了元素，break跳出循环
        except NoSuchElementException:
            pass

    return driver

