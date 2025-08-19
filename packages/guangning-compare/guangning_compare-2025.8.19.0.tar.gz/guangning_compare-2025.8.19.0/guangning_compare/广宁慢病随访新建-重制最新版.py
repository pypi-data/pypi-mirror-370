import pandas as pd
from selenium.common import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from comment.check_element import check_element
from comment.envWrite import env_write
from comment.excle_create import check_and_create_excel
from comment.write_excle import excel_append
from comment.登录头 import *
from compements.assemblies.check_diseases import check_diseases
from compements.assemblies.check_sf_date import check_sf_date
from compements.assemblies.check_sf_date_same_day import check_sf_date_same_day
from compements.assemblies.get_mb_data import get_mb_data
from compements.assemblies.get_mz_data import get_mz_data
from compements.assemblies.get_mz_time import get_mz_time
from compements.assemblies.get_new_sf_data import get_new_sf_data
from compements.assemblies.get_new_sf_date import get_new_sf_time
from compements.assemblies.get_sf_data import get_sf_data
from compements.assemblies.get_tj_data import get_tj_data
from compements.assemblies.has_current_quarter import has_current_quarter
from compements.new_assessment import new_follow_up
from compements.quarterly_statistics import quarterly_statistics
from compements.tool import safe_key, process_date

if is_software_expired():
    print("软件已到期")
else:
    # 等待时间设置为10秒，或根据需要调整
    wait_time = 10

    folder_path = '执行结果/异常名单.xlsx'
    check_and_create_excel(folder_path)
    # 检查文件是否包含表头
    try:
        existing_data = pd.read_excel(folder_path)
        required_columns = {'身份证号', '异常原因'}
        if not required_columns.issubset(existing_data.columns):
            # 文件没有表头，需要添加表头
            header_df = pd.DataFrame(columns=['身份证号', '异常原因'])
            header_df.to_excel(folder_path, index=False, header=True)
            print("文件没有表头,已添加表头")
    except pd.errors.EmptyDataError:
        # 文件为空，需要添加表头
        header_df = pd.DataFrame(columns=['身份证号', '异常原因'])
        header_df.to_excel(folder_path, index=False, header=True)
        print("文件为空,已添加表头")

    folder_path = '执行结果/成功名单.xlsx'
    check_and_create_excel(folder_path)
    # 检查文件是否包含表头
    try:
        existing_data = pd.read_excel(folder_path)
        required_columns = {'身份证号', '成功'}
        if not required_columns.issubset(existing_data.columns):
            # 文件没有表头，需要添加表头
            header_df = pd.DataFrame(columns=['身份证号', '成功'])
            header_df.to_excel(folder_path, index=False, header=True)
            print("文件没有表头,已添加表头")
    except pd.errors.EmptyDataError:
        # 文件为空，需要添加表头
        header_df = pd.DataFrame(columns=['身份证号', '成功'])
        header_df.to_excel(folder_path, index=False, header=True)
        print("文件为空,已添加表头")

    # 读取已查询数量
    try:
        with open('执行结果/env.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            fourth_line = lines[2].strip().split(":")
            # 提取查询数量并去除空白字符
            number = int(fourth_line[-1].strip())
            print('已完成数量:', number)
    except FileNotFoundError:
        print("文件不存在，请检查文件路径是否正确。")
    except Exception as e:
        print(f"读取文件时发生错误：{e}")

    df1 = pd.read_excel('文档/名单.xlsx', engine='openpyxl')
    data1 = df1.to_dict('records')
    max_number1 = len(data1)
    # 获取表头（列名）
    headers = df1.columns.tolist()
    print("总操作数:", max_number1)

    env_write('执行结果/env.txt', 1, f"总操作数:{max_number1}")
    df = pd.read_excel('文档/名单.xlsx', engine='openpyxl', skiprows=range(1, number + 1))
    data = df.to_dict('records')
    sy_number = len(data)
    print("剩余操作数:", sy_number)

    driver = CustomBrowser()
    login(driver)

    time.sleep(1)
    element = WebDriverWait(driver, wait_time).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/span/div/div/div[4]/ul/li[2]')))
    element.click()

    iframe_element = WebDriverWait(driver, wait_time).until(
        EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, '/phis/app/ehr')]")))
    driver.switch_to.frame(iframe_element)

    # 包含子机构
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
        (By.XPATH, '/html/body/div[1]/div/div/div/table/tbody/tr[2]/td/table/tbody/tr/td[4]/label/input'))).click()

    # 输入身份证号
    for index, record in enumerate(data):
        sfzh = record['身份证号']
        sfzh = str(sfzh).replace("x", "X").strip()
        timeout_occurred = False  # 设置一个标志变量
        print('当前处理身份证号:', sfzh)
        env_write('执行结果/env.txt', 2, f'当前处理身份证号:{sfzh}')

        id_number = f"{sfzh}"

        shen_fen = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="idNumber"]')))
        shen_fen.clear()  # 清除输入框
        shen_fen.send_keys(str(id_number))

        # 执行JavaScript代码点击查询
        time.sleep(1)
        driver.execute_script("""
                    var xpath = '//*[@id="chaxun"]';
                    var matchingElement = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    if (matchingElement) {
                        matchingElement.click();
                    }
                    """)
        print('点击查询')

        # 使用一个无限循环，直到找不到元素
        while True:
            try:
                # 如果找不到元素，break跳出循环
                if not check_element(driver):
                    break
            except:
                print('元素不存在')
                break
        try:
            # 等待元素可见并获取该元素
            tsd = WebDriverWait(driver, 60).until(
                EC.visibility_of_element_located((By.XPATH, f'//div[contains(text(), "{id_number}")]')))
        except:
            number = number + 1
            env_write("执行结果/env.txt", 3, f'已完成数量:{number}')
            print(f'无档案')
            excel_append("执行结果/异常名单.xlsx", '身份证号', sfzh + '\t', '异常原因', "暂无建档")
            continue

        # 慢病类型
        # 等待元素可见并获取该元素
        mb_fl = WebDriverWait(driver, wait_time).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="ext-gen27"]/div/table/tbody/tr/td[8]/div')))

        # 获取该元素的文本
        mb_fl_text = mb_fl.text
        print("慢病分类:", mb_fl_text)

        element_xpath = f'//div[contains(text(), "{id_number}")]'
        script = f"""
                    var element = document.evaluate('{element_xpath}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    if (element) {{
                        var event = new MouseEvent('dblclick', {{
                            'view': window,
                            'bubbles': true,
                            'cancelable': true
                        }});
                        element.dispatchEvent(event);
                    }}
                    """
        driver.execute_script(script)  # 双击进入
        time.sleep(1.5)
        original_windows = driver.current_window_handle

        # 切换到最新的窗口
        driver.switch_to.window(driver.window_handles[-1])
        driver.maximize_window()

        # 判断日期是否需要读表
        if '随访日期' in headers:
            skip = False
        else:
            skip = True

        """
        获取档案数据
        """
        print("--------------------获取档案数据--------------------")
        mb_data = get_mb_data(driver)
        print("获取档案数据", mb_data)
        sign = False

        # 检查是否有慢病随访按钮
        s = check_diseases(driver)
        if not s:
            print("没有慢病随访按钮")
            print(f'{sfzh}运行完成')

            number += 1
            env_write("执行结果/env.txt", 3, f'已完成数量:{number}')

            driver.close()
            # 切换回原始窗口
            driver.switch_to.window(original_windows)
            wait = WebDriverWait(driver, 10)  # 等待最长10秒
            iframe_element = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="ext-gen1030"]')))
            driver.switch_to.frame(iframe_element)
            continue

        """
        检查需要新建的随访日期
        """
        print("--------------------检查门诊日期--------------------")
        mz_time = get_mz_time(driver, record, headers)
        print("检查门诊日期", mz_time)
        if not mz_time and skip is True:
            print("无符合条件的门诊日期")
            excel_append("执行结果/异常名单.xlsx", '身份证号', sfzh + '\t', '异常原因', "无符合条件的门诊日期")
        else:
            print("符合条件的门诊日期:", mz_time)
            print("--------------------检查已新建随访日期--------------------")
            sf_time = check_sf_date(driver)
            print("已建随访日期:", sf_time)

            # 判断当前季度是否已有随访
            # 获取本季度已做过慢病随访，是否继续保存
            with open("./执行结果/env.txt", 'r', encoding='utf-8') as file:
                content = file.readlines()
            # 使用 split() 方法分割字符串
            yes = content[5].replace("：", ":").split(":")[1].strip()
            print("获取本季度已做过慢病随访，是否继续保存:", yes)

            if yes == '否':
                result = has_current_quarter(sf_time, record, headers)
            else:
                result = False

            # 判断是否存在同一天的随访日期
            same_result = check_sf_date_same_day(sf_time, record, headers)
            if same_result is True:
                excel_append("执行结果/异常名单.xlsx", '身份证号', sfzh + '\t', '异常原因', "随访日期读表,但同一天已有随访")
            else:
                if result is True and skip is False:
                    print("随访日期读表,但同一季度已有随访")
                    excel_append("执行结果/异常名单.xlsx", '身份证号', sfzh + '\t', '异常原因', "随访日期读表,但同一季度已有随访")
                else:
                    # 根据门诊和随访日期，判断计算出需要新建随访的日期
                    new_sf_time = get_new_sf_time(mz_time, sf_time)
                    if skip is False:
                        new_sf_time = record['随访日期']
                        new_sf_time = [process_date(new_sf_time)]
                    print("需要新建随访日期:", new_sf_time)

                    print("--------------------获取时间范围内所有的随访数据--------------------")
                    sf_data = get_sf_data(driver, sf_time)
                    print("获取时间范围内所有的随访数据:", sf_data)

                    print("--------------------获取门诊数据--------------------")
                    mz_data = get_mz_data(driver, new_sf_time)
                    print("获取门诊数据:", mz_data)

                    print("--------------------获取体检数据--------------------")
                    tj_data = get_tj_data(driver)
                    print("获取体检数据:", tj_data)

                    if new_sf_time:
                        for n_sf_time in new_sf_time:
                            """
                            根据档案、门诊、体检、往次随访数据  确定新建的随访数据
                            """
                            print("--------------------确定随访数据--------------------")
                            new_sf_data = get_new_sf_data(mb_data, mz_data, tj_data, n_sf_time, sf_data, sfzh)
                            print("确定随访数据", new_sf_data)

                            print("--------------------新建随访--------------------")
                            new_follow_up(driver, new_sf_data, sfzh, record, headers)

                            # 合并新随访数据
                            formatted_new_data = {
                                new_sf_data['随访日期']: {
                                    '收缩压': str(new_sf_data['收缩压']),
                                    '舒张压': str(new_sf_data['舒张压']),
                                    '空腹血糖': str(new_sf_data['空腹血糖']),
                                    '心率': str(new_sf_data['心率']),
                                    '身高': str(new_sf_data['身高']),
                                    '体重': str(new_sf_data['体重']),
                                    '腰围': str(new_sf_data['腰围']),
                                    '日吸烟量': str(new_sf_data['日吸烟量']),
                                    '日饮酒量': str(new_sf_data['日饮酒量']),
                                    '运动次数': str(new_sf_data['运动次数']),
                                    '运动时间': str(new_sf_data['运动时间']),
                                    '主食量': new_sf_data['主食量'],  # 保持原样，因为它是字符串类型
                                }
                            }
                            combined_data = {**sf_data, **formatted_new_data}
                            sf_data = dict(sorted(combined_data.items(), key=lambda item: safe_key(item[1])))

                            # 输出结果
                            print("合并后的往次随访数据", sf_data)

                    else:
                        print("不需要新建随访")
                        excel_append("执行结果/异常名单.xlsx", '身份证号',
                                     sfzh + '\t', '异常原因',
                                     f"已建随访日期-{sf_time}, 门诊日期-{mz_time}")
        # 慢病随访季度统计
        print("--------------------随访季度统计--------------------")

        quarterly_statistics(driver, sfzh, mz_time)

        print(f'{sfzh}运行完成')

        number += 1
        env_write("执行结果/env.txt", 3, f'已完成数量:{number}')

        driver.close()
        # 切换回原始窗口
        driver.switch_to.window(original_windows)
        wait = WebDriverWait(driver, 10)  # 等待最长10秒
        iframe_element = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="ext-gen1030"]')))
        driver.switch_to.frame(iframe_element)
    print("程序已执行完成")
    env_write("执行结果/env.txt", 10, f'执行完成:1')
