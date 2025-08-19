from pathlib import Path
import shutil

CR = Path(__file__).resolve().parent


def main():
    cwd = Path.cwd()
    current_folder_name = cwd.name

    yes = (
        input(f"确定将广宁的代码与 {current_folder_name} 进行比较吗 (y/n): ")
        .strip()
        .lower()
    )
    if yes != "y":
        print("操作已取消。")
        return

    folder_compements = CR / "compements"

    # shutil.rmtree(cwd / "compements", ignore_errors=True)
    shutil.copytree(folder_compements, cwd / "compements", dirs_exist_ok=True)
    folder_comment = CR / "comment"
    # shutil.rmtree(cwd / "comment", ignore_errors=True)
    shutil.copytree(folder_comment, cwd / "comment", dirs_exist_ok=True)
    print(f"已将 {folder_compements} 和 {folder_comment} 复制到 {cwd}。")

    main_followup_file = list(cwd.glob("*.py"))
    main_followup_file = list(filter(lambda x: "随访" in x.name, main_followup_file))
    if len(main_followup_file) != 1:
        print("无法找到随访新建文件。")
        return

    main_followup_file = main_followup_file[0]
    shutil.copy(CR / "广宁慢病随访新建-重制最新版.py", main_followup_file)
    print("已覆盖随访新建文件。")


if __name__ == "__main__":
    main()
