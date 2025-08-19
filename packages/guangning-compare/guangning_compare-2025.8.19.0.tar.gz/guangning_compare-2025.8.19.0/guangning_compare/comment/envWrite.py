def env_write(file_path, line_number, content):
    # 读取文件并将其内容存储到列表中
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 修改指定行的内容（注意列表是从0开始索引的）
    if 1 <= line_number <= len(lines):
        lines[line_number - 1] = content + '\n'
    elif line_number > len(lines):
        # 如果指定的行数超出了文件的总行数，将在末尾添加新行
        lines.extend(['\n'] * (line_number - len(lines) - 1))
        lines.append(content + '\n')

    # 将修改后的内容写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)


