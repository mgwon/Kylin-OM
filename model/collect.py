import influxdb_client, os, time,datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd
import psutil
import pytz
import argparse



# 函数systeminfo_write()读取系统的cpu，内存，磁盘，网络信息，生成并写入文件systeminfo.csv中
def systeminfo_write():
    # 时间戳
    timestamp = time.time()
    # CPU信息
    cpu_time = psutil.cpu_times()
    cpu_avg = psutil.getloadavg()
    cpu_stats = psutil.cpu_stats()
    # Memory信息
    mem = psutil.virtual_memory()
    men_swap = psutil.swap_memory()
    # Disk信息存储
    disk_usage = psutil.disk_usage('/')
    disk_io = psutil.disk_io_counters()
    # 由 字典data1 生成 DataFrame类型df1
    data1 = {"时间戳": [timestamp], "CPU逻辑数量": [psutil.cpu_count()],
             "CPU物理核心": [psutil.cpu_count(logical=False)], "CPU使用率": [psutil.cpu_percent()],
             "CPU频率": [psutil.cpu_freq().current],
             "用户态运行时间": [cpu_time.user], "核心态运行时间": [cpu_time.system], "IO等待时间": [cpu_time.idle],
             "1min内平均负载": [cpu_avg[0]], "5min内平均负载": [cpu_avg[1]], "15min内平均负载": [cpu_avg[2]],
             "中断次数": [cpu_stats[1]], "软中断次数": [cpu_stats[2]], "系统调用次数": [cpu_stats[3]],
             "总内存": [mem.total / 1024 / 1024], "已用内存": [mem.used / 1024 / 1024],
             "空闲内存": [mem.free / 1024 / 1024], "使用内存占比": [mem.percent],
             "交换内存大小": [men_swap.total], "交换内存已用大小": [men_swap.used], "交换内存空闲大小": [men_swap.free],
             "交换内存使用占比": [men_swap.percent],
             "磁盘总空间": [disk_usage.total / 1024 / 1024], "磁盘已使用大小": [disk_usage.used / 1024 / 1024],
             "磁盘空闲大小": [disk_usage.free / 1024 / 1024],
             "磁盘使用占比": [disk_usage.percent], "读IO量": [disk_io.read_bytes / 1024 / 1024],
             "写IO量": [disk_io.write_bytes / 1024 / 1024],
             "磁盘读时间": [disk_io.read_time], "磁盘写时间": [disk_io.write_time]}
    df1 = pd.DataFrame(data1, index=["a"])
    # 记录所有网卡信息与流量 并接入df1
    io_stats = psutil.net_io_counters(pernic=True)
    for name, stats in io_stats.items():
        data_tem = {"网卡" + name + "发送数据大小": [stats.bytes_sent / 1024 / 1024],
                    "网卡" + name + "发送数据包数量": [stats.packets_sent],
                    "网卡" + name + "接收数据大小": [stats.bytes_recv / 1024 / 1024],
                    "网卡" + name + "接收数据包数量": [stats.packets_recv],
                    "网卡" + name + "接收包出错数": [stats.errin],
                    "网卡" + name + "发送包出错数": [stats.errout]}
        df_tem = pd.DataFrame(data_tem, index=["a"])
        df1 = pd.concat([df1, df_tem], axis=1)
        return df1




# 函数processinfo_write(cpupercent,mempercent)读取同一时间戳下系统中 cpu占用率大于cpupercent 或者 内存占用率大于mempercent 的所有进程，生成并写入文件processinfo.csv中
def processinfo_write(cpupercent,mempercent):
    # 进程的信息列表，便于之后构造字典

    # 时间戳
    timestamp = time.time()
    timestamp_list=[]
    # 进程名
    name_list=[]
    # 进程pid
    pid_list=[]
    # 进程cpu占用率
    cpupercent_list=[]
    # 进程内存占用率
    mempercent_list=[]
    # 进程状态
    status_list=[]
    # 进程读流量
    readbytes_list=[]
    # 进程写流量
    writebytes_list=[]
    # vms大小
    vms_list=[]
    # rss大小
    rss_list=[]
    # 使用线程数
    threads_list = []
    # 进程创建时间戳
    createtime_list = []
    # 遍历进程pid列表，寻找满足条件的进程存入列表
    for i in psutil.pids():
        if psutil.pid_exists(i):
            p = psutil.Process(i)
            if p.cpu_percent() >= cpupercent or p.memory_percent() >= mempercent:
                timestamp_list.append(timestamp)
                name_list.append(p.name())
                pid_list.append(i)
                cpupercent_list.append(p.cpu_percent())
                mempercent_list.append(p.memory_percent())
                status_list.append(p.status())
                readbytes_list.append(p.io_counters().read_bytes)
                writebytes_list.append(p.io_counters().write_bytes)
                vms_list.append(p.memory_info().vms)
                rss_list.append(p.memory_info().rss)
                threads_list.append(p.num_threads())
                createtime_list.append(p.create_time())
    # 构建字典以构建DataFrame类型的df
    data={"时间戳":timestamp_list,
    "进程名":name_list,
    "进程号":pid_list,
    "cpu占用率":cpupercent_list,
    "内存占用率":mempercent_list,
    "状态":status_list,
    "读取字节数":readbytes_list,
    "写入字节数":writebytes_list,
    "vms":vms_list,
    "rss":rss_list,
    "使用线程数":threads_list,
    "创建时间":createtime_list}
    df = pd.DataFrame(data)
    return df

# 将df（只有一行数据的）存到influxdb中
def df_to_influx(df,bucket_name):
    # 设置influxdb中的user参数与信息
    token = "O3lnKZ5sqIRc-XjZ2TDy2mVz_DwDYtmohEZdGKojjJ51-oXA0gLoP16Pc7k8kS7nbnfxwbYZiicqs255TjeWiA=="
    org = "org"
    url = "http://localhost:8086"
    write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    write_api = write_client.write_api(write_options=SYNCHRONOUS)

    data_dict = df.to_dict("list")
    for x, y in data_dict.items():
        data_dict .update([(x, y[0])])

    timestamp = int(data_dict["时间戳"])
    uid=timestamp
    point = Point("001").tag("UID",uid).time(datetime.datetime.utcfromtimestamp(timestamp), WritePrecision.MS)
    for key, values in data_dict.items():
        point.field(key, values)

    write_api.write(bucket=bucket_name, org="org", record=point)
    write_client.close()

# 主控程序
def collect_set(start_time,end_time,gap=1,cpu=0,mem=0):
    print("将在以下时间段收集数据:")
    cpupercent=cpu
    mempercent=mem
    system_df = pd.DataFrame()
    process_df = pd.DataFrame()

    # ————————api接口换为时间戳——————————
    key_timeStamp = start_time
    val_timeStamp = end_time
    # key_d = datetime.datetime.strptime(a, "%Y-%m-%d_%H:%M:%S")
    # time.mktime(key_d.timetuple()))
    # val_d = datetime.datetime.strptime(b, "%Y-%m-%d_%H:%M:%S")
    # time.mktime(val_d.timetuple()))
    index_counter=0 #次数计时器

    wait_time=int(round(key_timeStamp * 1000))

    wait_gap=wait_time-int(round(time.time() * 1000))
    time.sleep(float(wait_gap) / 1000)

    while time.time() <= val_timeStamp:
        index_counter+=1
        op_start=int(round(time.time() * 1000))#每次执行开始的计时器


        df1=systeminfo_write()
        df2=processinfo_write(cpupercent, mempercent)

        df_to_influx(df1,"systeminfo")
        df_to_influx(df2,"processinfo")

        system_df = pd.concat([system_df, df1])
        process_df = pd.concat([process_df, df2])

        op_end=int(round(time.time() * 1000))#每次执行结束的计时器
        op_gap=op_end-op_start
        op_sleep=1000-op_gap
        if(op_gap<1000*gap):
            time.sleep(float(op_sleep) /1000)# 单位 秒
            print('第',index_counter,'次存取系统数据，执行时间：',op_gap,',等待时间：',float(op_sleep) /1000)


    # 写入文件systeminfo.csv与文件processinfo.csv中（隐藏 列表头与行索引）
    system_df.to_csv(time.strftime('%Y-%m-%d', time.localtime(time.time())) + "systeminfo.csv", mode='a+', index=False,header=False)
    process_df.to_csv(time.strftime('%Y-%m-%d', time.localtime(time.time())) + "processinfo.csv", mode='a+', index=False,header=False)
    return True


# # 测试
if __name__=="__main__":
    st="2024-07-22_15:54:00"
    et="2024-07-22_15:55:20"
    gap=1
    cpu=0
    mem=0
    collect_set(st,et,gap,cpu,mem)

