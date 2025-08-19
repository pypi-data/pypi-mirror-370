import re
from datetime import datetime

def validate_id_number(id_number):
    # 正则表达式匹配身份证号码的模式
    pattern = r'^(\d{6})(\d{4})(\d{2})(\d{2})(\d{3})(\d|X|x)$'
    match = re.match(pattern, id_number)
    if not match:
        return False

    # 提取身份证号码的各个部分
    area_code = match.group(1)
    year = match.group(2)
    month = match.group(3)
    day = match.group(4)
    sequence = match.group(5)
    check_code = match.group(6).upper()

    # 加权因子
    factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    # 校验码对应值
    check_codes = '10X98765432'

    # 计算校验码
    check_sum = sum(int(id_number[i]) * factors[i] for i in range(17)) % 11
    calculated_check_code = check_codes[check_sum]

    # 检查校验码是否匹配
    if check_code != calculated_check_code:
        return False

    # 验证出生日期是否合法
    try:
        birth_date = datetime.strptime(f'{year}-{month}-{day}', '%Y-%m-%d')
    except ValueError:
        return False

    # 返回提取的信息
    return {
        'area_code': area_code,
        'year': year,
        'month': month,
        'day': day,
        'sequence': sequence,
        'check_code': check_code,
        'birth_date': birth_date
    }
