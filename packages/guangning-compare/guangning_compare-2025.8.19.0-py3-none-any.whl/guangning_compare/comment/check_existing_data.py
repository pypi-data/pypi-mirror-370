# 检查已有数据是否包含新数据
import pandas as pd


def check_existing_data(existing_data, new_data):
    if pd.notna(existing_data):
        existing_values = existing_data.split(", ")
        if new_data not in existing_values:
            return f"{existing_data}, {new_data}"
    else:
        return new_data