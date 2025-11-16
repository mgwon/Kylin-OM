import pymysql
import psutil
import pandas as pd
import time
import datetime
import argparse

# MySQL 连接配置
mysql_host = '127.0.0.1'
mysql_port = 3306
mysql_user = 'root'
mysql_password = 'tzb_2024=WIN/'
mysql_db = 'testone'

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
    time_interval = gap
    cpupercent = cpu
    mempercent = mem
    system_df = pd.DataFrame()

    key_d = datetime.datetime.strptime(a, "%Y-%m-%d_%H:%M:%S")
    key_timeStamp = time.mktime(key_d.timetuple())
    val_d = datetime.datetime.strptime(b, "%Y-%m-%d_%H:%M:%S")
    val_timeStamp = time.mktime(val_d.timetuple())
    index_counter = 0  # 次数计时器

    wait_time = int(round(key_timeStamp * 1000))
    wait_gap = wait_time - int(round(time.time() * 1000))
    time.sleep(float(wait_gap) / 1000)

    while time.time() <= val_timeStamp:
        index_counter += 1
        op_start = int(round(time.time() * 1000))  # 每次执行开始的计时器

        system_df = pd.concat([system_df, systeminfo_write1()])

        op_end = int(round(time.time() * 1000))  # 每次执行结束的计时器
        op_gap = op_end - op_start
        op_sleep = 1000 - op_gap

    # 写入文件systeminfo.csv中（隐藏 列表头与行索引）
    system_df.to_csv(time.strftime('%Y-%m-%d', time.localtime(time.time())) + "systeminfo.csv", mode='a+',
                     index=False, header=False)

# # 测试
# if __name__ == "__main__":
#     st = "2024-07-30_17:12:00"
#     et = "2024-07-30_17:13:00"
#     gap = 1
#     cpu = 0
#     mem = 0
#     collect_set(st, et, gap, cpu, mem)