import os

def check_and_create_file(file_path):
    try:
        if not os.path.exists(file_path):
            with open(file_path, 'w',encoding='utf-8') as file:
                print(f"文件 '{file_path}' 不存在，已创建新文件。")
        else:
            print(f"文件 '{file_path}' 已存在。")
    except Exception as e:
        print(f"处理文件时出现异常: {str(e)}")