from bpfcc import BPF
import random
import subprocess
import time
import datetime


# 加载 eBPF 程序
bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>

BPF_HASH(start, struct request *);
BPF_HISTOGRAM(dist);

void trace_start(struct pt_regs *ctx, struct request *req) {
    u64 ts = bpf_ktime_get_ns();
    start.update(&req, &ts);
}

void trace_completion(struct pt_regs *ctx, struct request *req) {
    u64 *tsp, delta;

    tsp = start.lookup(&req);
    if (tsp != 0) {
        delta = bpf_ktime_get_ns() - *tsp;
        dist.increment(bpf_log2l(delta / 1000));
        start.delete(&req);
    }
}
"""

def attach_probes(b):
    try:
        b.attach_kprobe(event="blk_start_request", fn_name="trace_start")
    except Exception:
        print("Failed to attach to blk_start_request, trying blk_mq_start_request")
        try:
            b.attach_kprobe(event="blk_mq_start_request", fn_name="trace_start")
        except Exception:
            print("Failed to attach to blk_mq_start_request, trying __blk_account_io_start")
            try:
                b.attach_kprobe(event="__blk_account_io_start", fn_name="trace_start")
            except Exception as e:
                print(f"Failed to attach to any start request events: {e}")
                return False

    try:
        b.attach_kprobe(event="blk_account_io_done", fn_name="trace_completion")
    except Exception as e:
        print(f"Failed to attach to blk_account_io_done: {e}")
        return False

    return True

def get_iostat():
    result = subprocess.run(['iostat', '-dx'], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout
    else:
        return None

def write_ebpfio_to_file(start_tsp, end_tsp, gap, output_file):

    key_timeStamp = start_tsp
    val_timeStamp = end_tsp
    index_counter = 0  # 次数计时器
    wait_time = int(round(key_timeStamp * 1000))
    wait_gap = wait_time - int(round(time.time() * 1000))
    time.sleep(float(wait_gap) / 1000)

    start_dt = datetime.datetime.fromtimestamp(start_tsp)
    end_dt = datetime.datetime.fromtimestamp(end_tsp)
    start_str=start_dt.strftime("%Y-%m-%d_%H:%M:%S")
    end_str=end_dt.strftime("%Y-%m-%d_%H:%M:%S")

    with open(output_file, 'w') as f:
        f.write(f"IO 统计时间为 {start_str} 至 {end_str} ，每次间隔 {gap} s \n\n")
        while time.time() <= val_timeStamp:
            index_counter += 1
            op_start = int(round(time.time() * 1000))  # 每次执行开始的计时器

            iostat_output = get_iostat()
            if iostat_output:
                t_str= datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d_%H:%M:%S")
                f.write(f"时间: {t_str}\n")
                f.write(iostat_output)
                f.write("\n\n")


            op_end = int(round(time.time() * 1000))  # 每次执行结束的计时器
            op_gap = op_end - op_start
            op_sleep = 1000 - op_gap
            if (op_gap < 1000 * gap):
                time.sleep(float(op_sleep) / 1000)  # 单位 秒
                print('第', index_counter, '次存取IO数据，执行时间：', op_gap, ',等待时间：', float(op_sleep) / 1000)


def record_io_data(start_time, end_time, output_file):
    start_dt = datetime.datetime.fromtimestamp(start_time)
    end_dt = datetime.datetime.fromtimestamp(end_time)

    print(f"Recording IO data from {start_dt} to {end_dt}")

    while datetime.datetime.now() < start_dt:
        time.sleep(1)

    print("Starting data collection")

    with open(output_file, "w") as f:
        f.write("IO statistics from {} to {}\n".format(start_dt, end_dt))

        while datetime.datetime.now() < end_dt:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break

        print("Ending data collection")

        dist = b.get_table("dist")
        dist_items = [(k.value, v.value) for k, v in dist.items()]
        dist_items.sort(key=lambda x: x[0])  # 根据 key 进行排序

        for key, value in dist_items:
            f.write(f"{key}: {value}\n")

def eBPF_main(st_tsp, ed_tsp, gap, output_file):
    global b
    b = BPF(text=bpf_text)

    write_ebpfio_to_file(st_tsp, ed_tsp, gap, output_file)

# 示例调用
if __name__ == "__main__":
    start_time = "2024-07-31_17:53:00"  # 示例开始时间
    end_time = "2024-07-31_17:53:20"  # 示例结束时间
    gap = 5  # 测量间隔时间，单位为秒

    st_dt = datetime.datetime.strptime(start_time, "%Y-%m-%d_%H:%M:%S")
    st_tsp = time.mktime(st_dt.timetuple())
    ed_dt = datetime.datetime.strptime(end_time, "%Y-%m-%d_%H:%M:%S")
    ed_tsp = time.mktime(ed_dt.timetuple())

    output_file = "iobcc.txt"  # 输出文件

    eBPF_main(st_tsp, ed_tsp, gap ,output_file)