import requests
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import logging
from datetime import datetime
import os
import traceback

folder_name = "执行日志"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
else:
    pass

log_filename = '执行日志/' + datetime.now().strftime('%Y-%m-%d') + '-log.txt'

# 创建一个自定义的文件处理器，设置编码为 'utf-8'
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setLevel(logging.ERROR)

# 获取根日志记录器，并添加自定义的文件处理器
root_logger = logging.getLogger()
root_logger.addHandler(file_handler)

def log_exception(message, error=None):
    start_time = datetime.now()
    try:
        if error and isinstance(error, BaseException):
            raise error
    except NoSuchElementException as e:
        end_time = datetime.now()
        tb_str = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
        logging.error(f"出现错误 {start_time} to {end_time}, 类型 {type(e).__name__}: {e}。可能是因为找不到某个元素或者Xpath。\n{''.join(tb_str)}")
    except WebDriverException as e:
        end_time = datetime.now()
        tb_str = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
        logging.error(f"出现错误 {start_time} to {end_time}, 类型 {type(e).__name__}: {e}。可能是因为网络问题或者WebDriver问题。\n{''.join(tb_str)}")
    except requests.exceptions.RequestException as e:
        end_time = datetime.now()
        tb_str = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
        logging.error(f"出现错误 {start_time} to {end_time}, 类型 {type(e).__name__}: {e}。可能是因为网络问题。\n{''.join(tb_str)}")
    except Exception as e:
        end_time = datetime.now()
        tb_str = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
        logging.error(f"出现错误 {start_time} to {end_time}, 类型 {type(e).__name__}: {e}\n{''.join(tb_str)}")
    finally:
        pass
