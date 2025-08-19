# -*- coding: utf-8 -*-

from datetime import datetime


def is_valid_format(date_str):
    try:
        # 如果给定的字符串能被正确地解析为日期，那么就认定它是有效的
        datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        return True
    except ValueError:
        # 如果给定的字符串不能被解析为日期，那么就认定它是无效的
        return False


# 测试
date_str = "2024-01-02"
print(is_valid_format(date_str))