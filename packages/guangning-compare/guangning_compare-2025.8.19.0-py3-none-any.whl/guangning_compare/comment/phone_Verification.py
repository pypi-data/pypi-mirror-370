import re
import pandas as pd

def is_valid_phone_number(phone_number):
    # 先检查手机号码是否为空或者是NaN
    if pd.isna(phone_number):
        return False  # 空值或NaN被认为是无效的手机号码

    # 如果phone_number是浮点数（由于Excel的处理），先转换为整数
    if isinstance(phone_number, float):
        phone_number = str(int(phone_number))
    else:
        phone_number = str(phone_number)

    # 清除可能出现的空格
    phone_number = phone_number.strip()

    # 中国大陆的手机号码正则表达式规则
    pattern = re.compile(r'^1[3456789]\d{9}$')
    if pattern.match(phone_number):
        return True
    else:
        return False
