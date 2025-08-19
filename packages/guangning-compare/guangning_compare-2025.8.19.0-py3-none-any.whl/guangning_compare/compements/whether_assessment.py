from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


def whether_assessment(driver):

    current_year = datetime.now().year
    time = ''
    try:
        # 找到包含日期的元素
        element = WebDriverWait(driver, 10).until(
            ec.visibility_of_element_located((By.XPATH, f'//td/div[contains(text(), "{current_year}")]')))
        time = element.text
        return True, time
    except:
        return False, time







