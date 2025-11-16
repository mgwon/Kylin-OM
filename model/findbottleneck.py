import csv
import numpy as np
import time

filename=time.strftime('%Y-%m-%d', time.localtime(time.time())) + "systeminfo.csv"
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
    avg_values = np.mean(data, axis=0)
    max_values = np.max(data, axis=0)
    return avg_values, max_values


# 找出最大值除以平均值最大的那条数据
def find_max_ratio_row(data, avg_values, max_values):
    ratios = max_values / avg_values
    max_index = np.argmax(ratios)
    max_ratio_row = data[max_index]
    return max_ratio_row


# 主函数
def getbottleneck(filename):
    datas = read_csv(filename)
    avg_values, max_values = calculate_stats(datas)
    max_ratio_row = find_max_ratio_row(datas, avg_values, max_values)

    # 输出找到的数据信息
#    print("最大值除以平均值最大的数据信息：")
#    for header, value in zip(headers, max_ratio_row):
#        print(f"{header}: {value}")
#    for data in datas:
    max_ratio_row=max_ratio_row[1:]
    return max_ratio_row




# 测试
if __name__ == "__main__":
    filename = 'data.csv'  # 替换成你的CSV文件路径
    #main(filename)
