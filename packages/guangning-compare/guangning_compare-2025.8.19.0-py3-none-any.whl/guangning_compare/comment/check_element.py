import time


def check_element(driver):
    time.sleep(1.5)
    # print('开始检测,读取元素存在...')//div[text()="读取中..."]
    script = """
    let elements = document.evaluate('//div[contains(text(),'读取中')]', document, null, XPathResult.ANY_TYPE, null);
    return elements.iterateNext();
    """
    return driver.execute_script(script) is not None