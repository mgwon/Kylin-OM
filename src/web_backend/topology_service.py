#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# A-Ops Backend Service (v7.1 - with Data Persistence)
# Implements a detailed RCS model and saves the latest topology snapshot to a JSON file.
# MODIFIED: Automatically sets the status of the top RCS process to 'faulty'.
#

import subprocess
import re
import json
import time
import os
import threading
import collections
from datetime import datetime
from itertools import combinations
import networkx as nx
from flask import Flask, jsonify
from flask_cors import CORS
import psutil

# --- 核心配置 (Core Configuration) ---
DATA_REFRESH_INTERVAL = 30
TOP_N_PROCESSES = 30
API_HOST = '0.0.0.0'
API_PORT = 5002
# --- 新增功能: 数据快照输出路径 ---
OUTPUT_JSON_PATH = '/tmp/aops_latest_topology.json' # 设置为None或空字符串可禁用此功能

# --- 资源得分权重 (RCS Weights) ---
WEIGHTS = {
    "cpu": 0.35,
    "mem": 0.35,
    "disk": 0.20,
    "net": 0.10,
}

# --- 系统性能基准 (System Benchmarks) ---
SYSTEM_BENCHMARKS = {
    "MAX_DISK_BPS": 500 * 1024 * 1024,
    "MAX_NET_BPS": 125 * 1024 * 1024,
}

# --- 全局共享数据 (Global Shared Data) ---
graph_lock = threading.Lock()
G = nx.DiGraph()
latest_timestamp = "Initializing..."
VIRTUAL_ROOT_ID = 'virtual-root-node'
last_io_stats = {}

# --- 系统信息获取类 (System Info Class) ---
class SystemInfo:
    """在启动时获取一次静态的系统信息。"""
    def __init__(self):
        self.cpu_cores = os.cpu_count() or 1
        self.total_memory_bytes = psutil.virtual_memory().total
        print("[INFO] System Baseline Detected:")
        print(f"  - CPU Cores: {self.cpu_cores}")
        print(f"  - Total Memory: {self.total_memory_bytes / (1024**3):.2f} GB")
        if sum(WEIGHTS.values()) != 1.0:
            print(f"[WARNING] Sum of WEIGHTS is {sum(WEIGHTS.values())}, not 1.0. RCS score may not be properly scaled.")

# --- 连接获取模块 ---
def get_all_connections():
    """整合所有类型的连接（TCP, UDS, PIPE），并返回去重后的列表。"""
    all_conns = get_tcp_connections() + get_uds_connections() + get_pipe_connections()
    unique_conns = []
    seen_pairs = set()
    for conn in all_conns:
        pair_key = (conn['type'], tuple(sorted((conn['proc1_pid'], conn['proc2_pid']))))
        if pair_key not in seen_pairs:
            unique_conns.append(conn)
            seen_pairs.add(pair_key)
    return unique_conns

def get_tcp_connections():
    connections = []
    cmd = ["ss", "-tpn"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0: return []
        lines = result.stdout.strip().split('\n')
        socket_to_proc = {}
        conn_tuples = []
        proc_regex = re.compile(r'pid=(\d+)')
        for line in lines[1:]:
            parts = line.split()
            if len(parts) < 6 or 'ESTAB' not in parts[0]: continue
            local_addr_str, peer_addr_str = parts[4], parts[5]
            proc_info_str = parts[6] if len(parts) > 6 else ""
            match = proc_regex.search(proc_info_str)
            if match:
                pid = int(match.group(1))
                try:
                    ip, port = local_addr_str.rsplit(':', 1)
                    socket_to_proc[(ip, int(port))] = pid
                    conn_tuples.append((local_addr_str, peer_addr_str))
                except ValueError: continue
        for local_str, peer_str in conn_tuples:
            try:
                local_ip, local_port = local_str.rsplit(':', 1)
                peer_ip, peer_port = peer_str.rsplit(':', 1)
                local_port, peer_port = int(local_port), int(peer_port)
                pid1 = socket_to_proc.get((local_ip, local_port))
                pid2 = socket_to_proc.get((peer_ip, peer_port))
                if pid1 is not None and pid2 is not None and pid1 != pid2:
                    connections.append({
                        "type": "TCP", "proc1_pid": pid1, "proc2_pid": pid2,
                        "details": {"client": {"ip": local_ip, "port": local_port, "pid": pid1},
                                    "server": {"ip": peer_ip, "port": peer_port, "pid": pid2}}
                    })
            except (ValueError, KeyError): continue
    except (FileNotFoundError, subprocess.CalledProcessError): pass
    return connections

def get_uds_connections():
    connections = []
    cmd = ["ss", "-xpn"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0: return []
        lines = result.stdout.strip().split('\n')
        proc_regex = re.compile(r'pid=(\d+)')
        peer_regex = re.compile(r'peer\s+pid=(\d+)')
        for line in lines[1:]:
            if 'ESTAB' not in line: continue
            pid_match = proc_regex.search(line)
            peer_pid_match = peer_regex.search(line)
            if pid_match and peer_pid_match:
                pid = int(pid_match.group(1))
                peer_pid = int(peer_pid_match.group(1))
                if pid != peer_pid:
                    connections.append({
                        "type": "UDS", "proc1_pid": pid, "proc2_pid": peer_pid,
                        "details": "Anonymous Socket"
                    })
    except (FileNotFoundError, subprocess.CalledProcessError): pass
    return connections

def get_pipe_connections():
    connections = []
    pipe_map = collections.defaultdict(list)
    try:
        pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
        for pid_str in pids:
            pid = int(pid_str)
            fd_dir = f'/proc/{pid}/fd'
            try:
                for fd in os.listdir(fd_dir):
                    link_path = os.path.join(fd_dir, fd)
                    if os.path.islink(link_path):
                        target = os.readlink(link_path)
                        if target.startswith('pipe:'):
                            inode = target.split('[')[1].split(']')[0]
                            pipe_map[inode].append(pid)
            except (PermissionError, FileNotFoundError): continue
        for inode, pids in pipe_map.items():
            unique_pids = sorted(list(set(pids)))
            if len(unique_pids) > 1:
                for pid1, pid2 in combinations(unique_pids, 2):
                    connections.append({
                        "type": "PIPE", "proc1_pid": pid1, "proc2_pid": pid2,
                        "details": {"inode": inode}
                    })
    except Exception: pass
    return connections

# --- 文件保存模块 ---
def save_snapshot_to_file(graph):
    """将当前的节点（进程）的特定详细信息以覆盖写入的方式保存到JSON文件中。"""
    if not OUTPUT_JSON_PATH:
        return
    try:
        process_list = []
        for node_id, attrs in graph.nodes(data=True):
            if node_id == VIRTUAL_ROOT_ID:
                continue
            details = attrs.get('details', {})
            raw_info = details.get('raw', {})
            scores_info = details.get('scores', {})
            proc_info = {
                "进程名": attrs.get('label'), "pid": attrs.get('pid'),
                "状态": attrs.get('status'), "cpu使用率": raw_info.get('cpu'),
                "物理内存": raw_info.get('mem'), "磁盘i/o": raw_info.get('disk_io'),
                "网络链接数": raw_info.get('conns'), "cpu得分": scores_info.get('s_cpu'),
                "内存得分": scores_info.get('s_mem'), "磁盘得分": scores_info.get('s_disk'),
                "网络得分": scores_info.get('s_net'), "资源占用（RCS综合得分）": attrs.get('rcs')
            }
            process_list.append(proc_info)
        
        # 按RCS得分对最终列表进行降序排序
        # 注意：需要将字符串得分转为浮点数进行排序
        process_list.sort(key=lambda p: float(p.get('资源占用（RCS综合得分）', 0)), reverse=True)
        
        data_to_save = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "processes": process_list
        }
        with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
    except (IOError, PermissionError) as e:
        print(f"[ERROR] Failed to save snapshot to {OUTPUT_JSON_PATH}: {e}")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred during file save: {e}")

# --- 后台数据更新线程 (Background Update Thread) ---
def graph_update_thread(system_info):
    """后台定期运行，采集数据，计算RCS，并更新全局图对象G。"""
    global G, latest_timestamp, graph_lock, last_io_stats

    while True:
        current_time = time.time()
        all_connections = get_all_connections()
        connection_counts = collections.Counter()
        for conn in all_connections:
            connection_counts[conn['proc1_pid']] += 1
            connection_counts[conn['proc2_pid']] += 1
        max_conn_count = max(connection_counts.values(), default=1)
        proc_data_map = {}
        current_io_stats = {}
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'io_counters', 'status']):
            try:
                pid = p.info['pid']
                cpu_percent = p.info['cpu_percent']
                s_cpu = cpu_percent / (system_info.cpu_cores * 100.0)
                rss_bytes = p.info['memory_info'].rss
                s_mem = rss_bytes / system_info.total_memory_bytes if system_info.total_memory_bytes > 0 else 0
                io_counters = p.info['io_counters']
                current_io_stats[pid] = (io_counters.read_bytes, io_counters.write_bytes, current_time)
                disk_io_rate = 0
                if pid in last_io_stats:
                    last_read, last_write, last_time = last_io_stats[pid]
                    time_delta = current_time - last_time
                    if time_delta > 0:
                        disk_io_rate = ((io_counters.read_bytes - last_read) + (io_counters.write_bytes - last_write)) / time_delta
                s_disk = disk_io_rate / SYSTEM_BENCHMARKS['MAX_DISK_BPS'] if SYSTEM_BENCHMARKS['MAX_DISK_BPS'] > 0 else 0
                conn_count = connection_counts.get(pid, 0)
                s_net = conn_count / max_conn_count
                rcs = (WEIGHTS['cpu'] * s_cpu) + (WEIGHTS['mem'] * s_mem) + (WEIGHTS['disk'] * s_disk) + (WEIGHTS['net'] * s_net)
                status = 'faulty' if p.info['status'] == psutil.STATUS_ZOMBIE else 'running'
                proc_data_map[pid] = {
                    'pid': pid, 'name': p.info['name'], 'status': status, 'rcs': rcs,
                    'details_scores': {'s_cpu': s_cpu, 's_mem': s_mem, 's_disk': s_disk, 's_net': s_net},
                    'details_raw': {
                        'cpu_percent': cpu_percent, 'mem_rss_mb': rss_bytes / (1024*1024),
                        'disk_io_mbps': disk_io_rate / (1024*1024), 'conn_count': conn_count
                    }
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        last_io_stats = current_io_stats
        sorted_procs = sorted(proc_data_map.values(), key=lambda p: p['rcs'], reverse=True)
        top_pids = {p['pid'] for p in sorted_procs[:TOP_N_PROCESSES]}
        faulty_pids = {p['pid'] for p in proc_data_map.values() if p['status'] == 'faulty'}
        visible_pids = top_pids.union(faulty_pids)
        snapshot_graph = nx.DiGraph()
        if visible_pids:
            for pid in visible_pids:
                if pid in proc_data_map:
                    p_info = proc_data_map[pid]
                    node_id = f"{p_info['name']}-{pid}"
                    node_attrs = {
                        "label": p_info['name'], "pid": pid, "status": p_info['status'],
                        "rcs": f"{p_info['rcs']:.4f}",
                        "details": {
                            "scores": {k: f"{v:.4f}" for k, v in p_info['details_scores'].items()},
                            "raw": {
                                "cpu": f"{p_info['details_raw']['cpu_percent']:.2f}%",
                                "mem": f"{p_info['details_raw']['mem_rss_mb']:.2f} MB",
                                "disk_io": f"{p_info['details_raw']['disk_io_mbps']:.2f} MB/s",
                                "conns": p_info['details_raw']['conn_count']
                            }
                        }
                    }
                    snapshot_graph.add_node(node_id, **node_attrs)
            for conn in all_connections:
                p1_pid, p2_pid = conn['proc1_pid'], conn['proc2_pid']
                if p1_pid in visible_pids and p2_pid in visible_pids:
                    p1_info = proc_data_map.get(p1_pid)
                    p2_info = proc_data_map.get(p2_pid)
                    if p1_info and p2_info:
                        node1_id = f"{p1_info['name']}-{p1_pid}"
                        node2_id = f"{p2_info['name']}-{p2_pid}"
                        snapshot_graph.add_edge(node1_id, node2_id, type=conn['type'], details=conn['details'])

        # #######################################################################
        # ### 新增逻辑: 将RCS得分最高的进程状态强制修改为 'faulty'            ###
        # #######################################################################
        top_rcs_node_id = None
        max_rcs_score = -1.0
        # 1. 遍历所有真实节点，找到RCS最高的那个
        for node_id, attrs in snapshot_graph.nodes(data=True):
            if node_id == VIRTUAL_ROOT_ID or 'rcs' not in attrs:
                continue
            try:
                current_rcs = float(attrs['rcs'])
                if current_rcs > max_rcs_score:
                    max_rcs_score = current_rcs
                    top_rcs_node_id = node_id
            except (ValueError, TypeError):
                continue
        # 2. 如果找到了目标节点，则修改其状态
        if top_rcs_node_id:
            snapshot_graph.nodes[top_rcs_node_id]['status'] = 'faulty'
            top_node_label = snapshot_graph.nodes[top_rcs_node_id].get('label', top_rcs_node_id)
            print(f"[INFO] Status MODIFIED for top RCS process: '{top_node_label}' (RCS: {max_rcs_score:.4f}) set to 'faulty'.")
        # #######################################################################

        if snapshot_graph.number_of_nodes() > 0:
            parent_nodes = [n for n, d in snapshot_graph.in_degree() if d == 0]
            if parent_nodes:
                snapshot_graph.add_node(VIRTUAL_ROOT_ID, label='', isRoot=True, size=20, style={'fill': '#FFFFFF', 'stroke': '#CCCCCC'})
                for parent_id in parent_nodes:
                    snapshot_graph.add_edge(VIRTUAL_ROOT_ID, parent_id, style={'lineDash': [5, 5], 'stroke': '#cccccc', 'endArrow': False})
        
        save_snapshot_to_file(snapshot_graph)
        with graph_lock:
            G.clear()
            G.add_nodes_from(snapshot_graph.nodes(data=True))
            G.add_edges_from(snapshot_graph.edges(data=True))
            latest_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{latest_timestamp}] Graph updated based on RCS. Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
        time.sleep(DATA_REFRESH_INTERVAL)

# --- Flask Web API 模块 ---
app = Flask(__name__)
CORS(app) 

@app.route('/api/topology')
def get_topology():
    """API端点，返回G6可以渲染的JSON格式的图数据。"""
    with graph_lock:
        data = nx.node_link_data(G)
        # 将内部图结构转换为API友好的格式
        g6_data = {
            "nodes": [dict(id=n.pop('id'), **n) for n in data.get('nodes', [])],
            "edges": [dict(source=e.pop('source'), target=e.pop('target'), **e) for e in data.get('links', [])],
            "timestamp": latest_timestamp
        }
    return jsonify(g6_data)

# --- 主程序入口 ---
if __name__ == '__main__':
    if os.geteuid() != 0:
        print("\n[ERROR] This script requires root (sudo) privileges for full process access.")
        exit(1)
    system_info = SystemInfo()
    psutil.cpu_percent(interval=None)
    print("[INFO] Starting background thread for data collection...")
    collector_thread = threading.Thread(target=graph_update_thread, args=(system_info,), daemon=True)
    collector_thread.start()
    print(f"[INFO] Starting API server. Listening on http://{API_HOST}:{API_PORT}")
    print(f"[INFO] Access topology data at http://{API_HOST}:{API_PORT}/api/topology or http://127.0.0.1:{API_PORT}/api/topology")
    if OUTPUT_JSON_PATH:
        print(f"[INFO] Topology snapshots will be saved to {OUTPUT_JSON_PATH}")
    app.run(host=API_HOST, port=API_PORT, debug=False)

### 主要变更
