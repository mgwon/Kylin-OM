import os
import sh
import shutil

def FlameGraphCreate(svg_name,Hz_size,target_object,continue_time):
        # 使用numactl命令将进程迁移到指定的NUMA节点
        os.system(f"sudo perf record -F 99 -a -g -- sleep 20")

        sh.sudo.perf.record('-F', Hz_size, target_object, '-g', '--', 'sleep', continue_time)
        os.system("perf script -i perf.data &> perf.unfold")
        os.system("./FlameGraph-Data/FlameGraph/stackcollapse-perf.pl perf.unfold &> perf.folded")
        os.system(f"./FlameGraph-Data/FlameGraph/flamegraph.pl perf.folded > {svg_name}.svg")
        os.remove("perf.data")
        os.remove("perf.unfold")
        os.remove("perf.folded")
        source = svg_name+".svg"
        destination = '../static/svg/' + svg_name+".svg"
        shutil.move(source, destination)
# FlameGraphCreate("svg_name",99,"-a",10)