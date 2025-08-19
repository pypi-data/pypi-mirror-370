from datetime import datetime
import datetime
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def runsd(driver,record):
    tijrq = record['体检日期']
    formatted_date = tijrq.strftime('%Y-%m-%d')
    print("体检日期：", formatted_date)
    xinj = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="submitImg"]'))
    )
    xinj.click()
    # 点击确定保存按钮
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="ext-gen78"]'))
    ).click()
    driver.switch_to.default_content()  # 退出全部的表框

    # 先切换到第一个iframe
    first_iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="ext-gen21"]/iframe'))
    )
    driver.switch_to.frame(first_iframe)
    time.sleep(3)

    wait = WebDriverWait(driver, 10, poll_frequency=1, ignored_exceptions=[TimeoutException])
    wait.until(EC.visibility_of_element_located((By.XPATH, f'//div[contains(text(), "{formatted_date}")]')))

    second_iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,
                                        '//*[@id="ext-gen32"]/iframe'))
    )
    # 切换到第二个iframe
    driver.switch_to.frame(second_iframe)
