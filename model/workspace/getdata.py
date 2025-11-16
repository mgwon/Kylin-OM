import re
import subprocess
import pymysql
import psutil
import pandas as pd
import time
import datetime
import argparse
import csv
import numpy as np
import time

# MySQL 连接配置
mysql_host = '127.0.0.1'
mysql_port = 3306
mysql_user = 'root'
mysql_password = 'tzb_2024=WIN/'
mysql_db = 'testone'

def extract_linux_commands(text):
    """
    从文本中提取可能的Linux指令。假设指令以回车分隔，并且指令后可能跟有其他文字。
    参数:
    text (str): 包含可能的Linux指令的文本。
    返回:
    list: 提取的Linux指令列表。
    """
    # 扩展正则表达式，包含更多常见的Linux指令和sudo指令
    pattern = re.compile(r'/i\s*(.*?)\s*/r')
    #print("text:",text)
    #print(type(text))
    commands = pattern.findall(text)
    #print(commands)
    # 去掉多余的空白字符
    commands = [cmd.strip() for cmd in commands]
    #print("commands:",commands)
    #print("_______________________________________")
    return commands

def linux_commands_running(cmd_str):
    commands = extract_linux_commands(cmd_str)
    stdout_list = []
    stderr_list = []
    for tem in commands:
        result = subprocess.run(tem, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout_list.append(result.stdout)
        stderr_list.append(result.stderr)

    #print("errlist:",stderr_list)
    #print("outlist:",stdout_list)
    return stdout_list,stderr_list

def systeminfo_write1():
    # 时间戳
    timestamp = time.time()
    #连接mysql数据库
    conn = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_password, db=mysql_db)
    #tps qps
    with conn.cursor() as cursor:
        cursor.execute("SHOW GLOBAL STATUS LIKE 'Queries'")
        qps_result = cursor.fetchone()
        queries_per_second = int(qps_result[1])
        qps=queries_per_second

        cursor.execute("SHOW GLOBAL STATUS LIKE 'Com_commit'")
        tps_result = cursor.fetchone()
        commits_per_second = int(tps_result[1])
        tps=commits_per_second
    #Disk信息存储
    disk_usage = psutil.disk_usage('/')
    disk_io = psutil.disk_io_counters()

    # 由 字典data1 生成 DataFrame类型df1
    data1 = {"时间戳": [timestamp],"磁盘读IO量": [disk_io.read_bytes / 1024 / 1024],
             "磁盘写IO量": [disk_io.write_bytes / 1024 / 1024],
             "qps":[qps],"tps":[tps]}
    df1 = pd.DataFrame(data1, index=["a"])
    return df1

def collect_set1(start_time, end_time, gap, cpu, mem):
    isover = True
    timedic = {}
    a = start_time
    b = end_time

    system_df = pd.DataFrame()

    key_d = datetime.datetime.strptime(a, "%Y-%m-%d %H:%M:%S")
    key_timeStamp = time.mktime(key_d.timetuple())
    val_d = datetime.datetime.strptime(b, "%Y-%m-%d %H:%M:%S")
    val_timeStamp = time.mktime(val_d.timetuple())
    index_counter = 0  # 次数计时器

    #print(key_timeStamp)
    #print(val_timeStamp)
    #val_timeStamp = int(round(val_timeStamp * 1000))
    #key_timeStamp = int(round(key_timeStamp * 1000))
    gap=val_timeStamp -key_timeStamp
    end=time.time()+gap
    #end=int(end/1000)
    #print(now)
    #wait_gap = end_time - int(round(time.time() * 1000))

    #time.sleep(float(wait_gap) / 1000)

    while time.time() <= end:
        index_counter += 1
        op_start = int(round(time.time() * 1000))  # 每次执行开始的计时器

        system_df = pd.concat([system_df, systeminfo_write1()])

        op_end = int(round(time.time() * 1000))  # 每次执行结束的计时器
        op_gap = op_end - op_start
        op_sleep = 1000 - op_gap

    # 写入文件systeminfo.csv中（隐藏 列表头与行索引）
    system_df.to_csv("UI/APP/csv/"+time.strftime('%Y-%m-%d', time.localtime(time.time())) + "systeminfonew.csv",
                     mode='a+', index=False, header=False)
    #print(time.strftime('%Y-%m-%d', time.localtime(time.time())) + "systeminfonew.csv")


# 读取CSV文件
def read_csv(filename):
    data = []
    with open(filename, 'r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)
    return data


# 计算每列的平均值和最大值
def calculate_stats(data):
    data = np.array(data, dtype=float)
#    print("_____________data__________________________")
#    print(data)
    avg_values = np.mean(data, axis=0)
#    print("------------avg_values--------------")
    avg_values=avg_values[1:]
#    print(avg_values[2])
#    print(avg_values)
    max_values = np.max(data, axis=0)
#    print("------------max_values--------------")
#    print(max_values)

    return avg_values, max_values


# 找出最大值除以平均值最大的那条数据
def find_max_ratio_row(data, avg_values, max_values):
    ratios = max_values / avg_values
    max_index = np.argmax(ratios)
    max_ratio_row = data[max_index]
    return max_ratio_row


def get_mysql_data(str):
    #得到metagpt给出的回答，转为纯指令，将纯指令输入终端，得到标准输出
    #mmd_str = extract_linux_commands(str)
    list1, list2 = linux_commands_running(str)
#    print("------------------------------------------")
    print(list1)
    print(list2)

    #收集调优后的数据

    with open("UI/APP/start_end/start_end.txt", 'r') as file:
        lines = file.readlines()
        if len(lines) >= 2:
            last_line = lines[-1].strip()  # 最后一行
            second_last_line = lines[-2].strip() # 倒数第二行
            time1 = last_line
            time2 = second_last_line

    collect_set1(time2,time1,1,0,0) #调优后的数据写入csv文件

    #比较调优前后的数据
    datas1 = read_csv("UI/APP/csv/"+time.strftime('%Y-%m-%d', time.localtime(time.time())) + "systeminfonew.csv") #修改后
    datas2 = read_csv("UI/APP/csv/"+time.strftime('%Y-%m-%d', time.localtime(time.time())) + "systeminfo.csv")
    #print("datas1:",datas1)

    avg_values1, max_values1 = calculate_stats(datas1)
    avg_values2, max_values2 = calculate_stats(datas2)
    result: bool =False
    if avg_values1[2] > avg_values2[2] and avg_values1[3] > avg_values2[3]:
        result = True
    #print("data: ",datas1)
    #print("upsign： ",result)
    return list1,list2,result, datas1[0],datas1[1],datas1[2],datas1[3]

# 测试
if __name__=="__main__":
    str="下面是我的指令：/isudo ls -l /r/n /iecho hello world /r 我看看你怎么识别这种字符串， /isudo systemctl restart apache2/r"

    get_mysql_data(str)
