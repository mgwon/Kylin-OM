from django.shortcuts import render
from django.http import HttpResponse
from .forms import MyForm
import random
import time
# from .models import mysysteminfo
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os,psutil
import pandas as pd
from .collect import collect_set
from django.conf import settings
# from .FlameGraph_Create_Module.FlameGraph_create import FlameGraphCreate


def csv_to_content(csv_name):
    df=pd.read_csv(csv_name)
    timestamps = [obj[1] for obj in df.itertuples()]
    clocktime = [time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(obj[1]))) for obj in df.itertuples()]
    cpu_logics_num = [obj[2] for obj in df.itertuples()]
    cpu_physicals_num = [obj[3] for obj in df.itertuples()]
    cpu_usages = [obj[4] for obj in df.itertuples()]
    cpu_freq = [obj[5] for obj in df.itertuples()]
    usermode_runtime = [obj[6] for obj in df.itertuples()]
    corestate_runtime = [obj[7] for obj in df.itertuples()]
    IOwait_time = [obj[8] for obj in df.itertuples()]
    averload_in1min = [obj[9] for obj in df.itertuples()]
    averload_in5min = [obj[10] for obj in df.itertuples()]
    averload_in15min = [obj[11] for obj in df.itertuples()]
    interruptions_num = [obj[12] for obj in df.itertuples()]
    softinterruptions_num = [obj[13] for obj in df.itertuples()]
    systemcalls_num = [obj[14] for obj in df.itertuples()]

    Totalmemory_size = [obj[15] for obj in df.itertuples()]
    Usedmemory_size = [obj[16] for obj in df.itertuples()]
    Freememory_size = [obj[17] for obj in df.itertuples()]
    Memory_usage = [obj[18] for obj in df.itertuples()]
    Swapmemory_size = [obj[19] for obj in df.itertuples()]
    UsedSwapmemory_size = [obj[20] for obj in df.itertuples()]
    FreeSwapmemory_size = [obj[21] for obj in df.itertuples()]
    Swapmemory_usage = [obj[22] for obj in df.itertuples()]

    Totaldisk_size = [obj[23] for obj in df.itertuples()]
    Useddisk_size = [obj[24] for obj in df.itertuples()]
    Freedisk_size = [obj[25] for obj in df.itertuples()]
    Disk_usage = [obj[26] for obj in df.itertuples()]
    readIO_size = [obj[27] for obj in df.itertuples()]
    writeIO_size = [obj[28] for obj in df.itertuples()]
    readdisk_time = [obj[29] for obj in df.itertuples()]
    writedisk_time = [obj[30] for obj in df.itertuples()]


    context = {
        'timestamps': timestamps,
        'clocktime': clocktime,
        'cpu_usages': cpu_usages,
        'cpu_freq': cpu_freq,
        'usermode_runtime': usermode_runtime,
        'corestate_runtime': corestate_runtime,
        'IOwait_time': IOwait_time,
        'averload_in1min': averload_in1min,
        'averload_in5min': averload_in5min,
        'averload_in15min': averload_in15min,
        'interruptions_num': interruptions_num,
        'cpu_logics_num': cpu_logics_num,
        'cpu_physicals_num': cpu_physicals_num,
        'softinterruptions_num': softinterruptions_num,
        'systemcalls_num': systemcalls_num,

        'Totalmemory_size': Totalmemory_size,
        'Usedmemory_size': Usedmemory_size,
        'Freememory_size': Freememory_size,
        'Memory_usage': Memory_usage,
        'Swapmemory_size': Swapmemory_size,
        'UsedSwapmemory_size': UsedSwapmemory_size,
        'FreeSwapmemory_size': FreeSwapmemory_size,
        'Swapmemory_usage': Swapmemory_usage,

        'Totaldisk_size': Totaldisk_size,
        'Useddisk_size': Useddisk_size,
        'Freedisk_size': Freedisk_size,
        'Disk_usage': Disk_usage,
        'readIO_size': readIO_size,
        'writeIO_size': writeIO_size,
        'readdisk_time': readdisk_time,
        'writedisk_time': writedisk_time
    }
    return context





def cpu_graph(request):
    context = {}
    context.update(csv_to_content("2024-07-17systeminfo.csv"))
    value_i = 0
    value_ii = 0
    value_iii = 0
    value_iv = 0
    value_v = 0
    for tem in context["cpu_usages"]:
        if tem <= 20.0 and tem >= 0.0:
            value_i += 1
        elif tem <= 40.0 and tem > 20.0:
            value_ii += 1
        elif tem <= 60.0 and tem > 40.0:
            value_iii += 1
        elif tem <= 80.0 and tem > 60.0:
            value_iv += 1
        else:
            value_v += 1
    context.update(
        {"value_i": value_i, "value_ii": value_ii, "value_iii": value_iii, "value_iv": value_iv, "value_v": value_v})
    return render(request, 'cpu_graph.html', context)



def mem_graph(request):
    context = {}
    context.update(csv_to_content("2024-07-17systeminfo.csv"))
    return render(request, 'mem_graph.html', context)

def disk_graph(request):
    context = {}
    context.update(csv_to_content("2024-07-17systeminfo.csv"))
    return render(request, 'disk_graph.html', context)

def optimization(request):

    # 获取项目的根目录
    base_dir = os.path.dirname(__file__)
    # 定义文本文件的路径
    file_path1 = os.path.join(base_dir, 'txt', 'project1.txt')
    file_path2 = os.path.join(base_dir, 'txt', 'project2.txt')
    file_path3 = os.path.join(base_dir, 'txt', 'project3.txt')
    # 读取文件内容
    with open(file_path1, 'r', encoding='utf-8') as file1:
        file_content1 = file1.read()
    with open(file_path2, 'r', encoding='utf-8') as file2:
        file_content2 = file2.read()
    with open(file_path3, 'r', encoding='utf-8') as file3:
        file_content3 = file3.read()
    # 将文件内容传递给模板
    context = {
        'page_name': 'landing_page',
        'file_content1': file_content1,
        'file_content2': file_content2,
        'file_content3': file_content3
    }
    context.update(csv_to_content("2024-07-17systeminfo.csv"))
    return render(request, 'optimization.html', context)

def show_demo(request):
    context = {}
    context.update(csv_to_content("2024-07-17systeminfo.csv"))
    value_i = 0
    value_ii = 0
    value_iii = 0
    value_iv = 0
    value_v = 0
    for tem in context["cpu_usages"]:
        if tem <= 20.0 and tem >= 0.0:
            value_i += 1
        elif tem <= 40.0 and tem > 20.0:
            value_ii += 1
        elif tem <= 60.0 and tem > 40.0:
            value_iii += 1
        elif tem <= 80.0 and tem > 60.0:
            value_iv += 1
        else:
            value_v += 1
    context.update(
        {"value_i": value_i, "value_ii": value_ii, "value_iii": value_iii, "value_iv": value_iv, "value_v": value_v})

    records = read_time_records()
    context.update({'records': records})
    return render(request, 'demo.html',context)

def home(request):
    # 获取项目的根目录
    base_dir = os.path.dirname(__file__)
    # 定义文本文件的路径
    file_path = os.path.join(base_dir, 'start_end', 'start_end.txt')
    # 读取文件的最后一行
    with open(file_path, 'r', encoding='UTF-8') as file:
        lines = file.readlines()
        last_line = lines[-1] if lines else ""
        start_time, end_time = last_line.strip().split(',') if last_line else ("", "")

    button_text = '（Unsetting/Setting)Go to demo'  # 默认按钮文本
    target_url = '../show_demo'  # 默认目标 URL
    # 检查两个CSV文件是否存在
    processinfo_csv_path = os.path.join(settings.MEDIA_ROOT, '2024-07-17processinf.csv')
    systeminfo_csv_path = os.path.join(settings.MEDIA_ROOT, '2024-07-17systeminf.csv')
    # 如果两个文件都存在，则更新按钮文本和目标 URL
    if os.path.exists(processinfo_csv_path) and os.path.exists(systeminfo_csv_path):
        button_text = '（OK）Go to 可视化'
        target_url = '../show'  # 更新目标 URL
    # 将按钮文本和目标 URL 传递到 home.html 模板
    context = {
        'page_name': 'landing_page',
        'start_time': start_time,
        'end_time': end_time,
        'button_text': button_text,
        'target_url': target_url
    }
    return render(request, 'home.html', context)


# 定义一个函数来读取时间记录
def read_time_records():
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, 'start_end', 'start_end.txt')
    records = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                start_time, end_time = line.strip().split(',')
                records.append((i+1, start_time, end_time))
    return records

def select(request):
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']

            # 转换为时间戳
            start_tsp = int(time.mktime(start_time.timetuple()))
            end_tsp = int(time.mktime(end_time.timetuple()))
            # csv生成函数
            # collect_set(start_tsp,end_tsp,1,0.0,0.0)
            # 火焰图生成函数
            #FlameGraphCreate(time.localtime(time.time()) + "flame_graph",99,"-a",int(end_tsp-start_tsp))
            # 将新的时间记录追加到文件
            base_dir = os.path.dirname(__file__)
            file_path = os.path.join(base_dir, 'start_end', 'start_end.txt')
            with open(file_path, 'a') as file:
                file.write(f"{start_time},{end_time}\n")
            return HttpResponse('<script>alert("输入完毕!"); window.location.href="../";</script>')
    else:
        form = MyForm()

    # 读取所有时间记录
    records = read_time_records()
    context = {
        'form': form,
        'records': records
    }
    return render(request, 'select.html', context)


def ebpf(request):
    # 获取项目的根目录
    base_dir = os.path.dirname(__file__)
    # 定义文本文件的路径
    file_path1 = os.path.join(base_dir, 'eBPF', 'iobcc.txt')
    # 读取文件内容
    with open(file_path1, 'r', encoding='utf-8') as file1:
        file_content1 = file1.read()
    # 将文件内容传递给模板
    context = {
        'file_content1': file_content1,
    }
    return render(request, 'eBPF.html',context)

def show(request):
    records = read_time_records()
    context = {
        'records': records
    }
    return render(request, 'show.html', context)

def big_UI(request):
    context = {}
    context.update(csv_to_content("2024-07-17systeminfo.csv"))
    # context.update(csv_to_content(time.strftime('%Y-%m-%d', time.localtime(time.time()))+"systeminfo.csv"))
    value_i = 0
    value_ii = 0
    value_iii = 0
    value_iv = 0
    value_v = 0
    for tem in context["cpu_usages"]:
        if tem <= 20.0 and tem >= 0.0:
            value_i += 1
        elif tem <= 40.0 and tem > 20.0:
            value_ii += 1
        elif tem <= 60.0 and tem > 40.0:
            value_iii += 1
        elif tem <= 80.0 and tem > 60.0:
            value_iv += 1
        else:
            value_v += 1
    context.update({"value_i": value_i, "value_ii": value_ii,"value_iii": value_iii, "value_iv": value_iv ,"value_v": value_v})

    records = read_time_records()
    context.update({ 'records': records })
    return render(request, 'big_UI.html', context)

