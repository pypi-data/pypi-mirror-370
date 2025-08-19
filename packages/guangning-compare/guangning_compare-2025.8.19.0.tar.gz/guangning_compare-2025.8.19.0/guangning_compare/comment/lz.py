import logging
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from typing import Optional

# 设置日志配置以将日志写入文件
logging.basicConfig(filename='log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 初始化查询次数计数器
query_count = 0

def log_and_print(message: str, level: str = 'info'):
    """
    同时将消息记录到日志并打印到控制台
    :param message: 要记录和打印的消息
    :param level: 日志级别 ('info', 'warning', 'error')
    """
    print(message)
    if level == 'info':
        logging.info(message)
    elif level == 'warning':
        logging.warning(message)
    elif level == 'error':
        logging.error(message)
    else:
        logging.info(message)  # Default to 'info' level

def find_element_cross_iframe(
    driver: WebDriver,
    by: By,
    value: str,
    depth: int = 0,
    max_depth: int = 5
) -> Optional[WebElement]:
    global query_count
    query_count += 1
    # log_and_print(f"查询次数: {query_count}, 深度: {depth}, 最大深度: {max_depth}")

    try:
        element = driver.find_element(by, value)
        # log_and_print(f"元素找到: {element}")
        return element
    except NoSuchElementException as e:
        pass
        # log_and_print(f"元素未找到: {e}", level='warning')

    if depth >= max_depth:
        # log_and_print("达到最大搜索深度")
        return None

    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    # log_and_print(f"找到 {len(iframes)} 个 iframe")

    for index, iframe in enumerate(iframes):
        # log_and_print(f"切换到 iframe {index}")
        driver.switch_to.frame(iframe)

        element = find_element_cross_iframe(
            driver,
            by,
            value,
            depth=depth + 1,
            max_depth=max_depth
        )

        if element:
            return element

        driver.switch_to.parent_frame()

    driver.switch_to.default_content()
    return None

'''
使用的方法如下
参数如下：
driver
By
xpath,id,name,class等等
max_depth，这个是设置深度查询的，比如有四个iframe需要查到第四个，可以设置5，当然默认不写也可以
find_element_cross_iframe(driver,By.XPATH,'//*[@id="btnDy"]').click()
这里的driver是继承上述的状态，可以使用xpath或者是name,id都可以，和selenium的使用的方法一样
然后这个每次使用都会记录使用的查询的日志
'''