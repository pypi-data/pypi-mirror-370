import datetime
import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


def check_diseases(driver):

    driver.switch_to.default_content()
    WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH, '//*[@id="ext-gen23"]'))).click()

    WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH, "//dt[contains(text(),'随访服务')]"))).click()
    time.sleep(1)
    try:
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, "//li[contains(text(),'慢病随访')]"))).click()
        return True
    except:
        return False

