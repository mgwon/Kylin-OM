import json
import plotly.graph_objects as go
from datetime import datetime
import os
import re

# --- Utility Functions ---

def sanitize_filename(name):
    """Sanitizes a string to be a valid filename."""
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip(' _')
    return name[:100]

def format_bytes(byte_value, target_unit='GB'):
    """Converts a byte value to a more readable unit (KB, MB, GB, TB)."""
    if byte_value is None:
        return 0
    power = {'KB': 1, 'MB': 2, 'GB': 3, 'TB': 4}
    factor = 1024 ** power.get(target_unit, 3)
    return byte_value / factor

# ==============================================================================
# --- Specialized Charting Functions ---
# ==============================================================================

def create_cpu_chart(data, output_dir):
    """Creates a stacked area chart for CPU usage."""
    panel_title = data.get("panel_title", "CPU Usage")
    panel_id = data.get("panel_id", "no-id")
    traces = []
    color_map = {
        'user': '#56a3f2', 'system': '#81c784', 'iowait': '#ffd54f',
        'irq': '#ff8a65', 'softirq': '#f06292', 'steal': '#e0e0e0', 'nice': '#9575cd'
    }
    order = ['user', 'system', 'iowait', 'irq', 'softirq', 'steal', 'nice']
    all_series = {}
    for target in data.get("targets", []):
        legend = target.get("legendFormat", "").lower()
        mode = next((key for key in order if key in legend), None)
        result_data = target.get("result", {}).get("data", {})
        if mode and result_data.get("resultType") == "matrix" and result_data.get("result"):
            series = result_data["result"][0]
            if 'values' in series and series['values']:
                all_series[mode] = series['values']

    for mode in order:
        if mode in all_series:
            values = all_series[mode]
            timestamps = [datetime.fromtimestamp(v[0]) for v in values]
            numeric_values = [float(v[1]) * 100 for v in values]
            traces.append(go.Scatter(
                x=timestamps, y=numeric_values, mode='lines', name=mode.capitalize(),
                stackgroup='one', line=dict(width=0.5), fillcolor=color_map.get(mode),
                hovertemplate=f'<b>{mode.capitalize()}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.2f}}%<extra></extra>'
            ))

    if not traces: return None, None
    fig = go.Figure(data=traces)
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="CPU 使用率 (%)",
        yaxis_ticksuffix='%', hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_system_load_chart(data, output_dir):
    """Creates a line chart for system load averages."""
    panel_title = data.get("panel_title", "System Load")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix" and result_data.get("result"):
            series = result_data.get("result")[0]
            if 'values' in series and series['values']:
                has_data = True
                legend = target.get("legendFormat", "")
                timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                numeric_values = [float(v[1]) for v in series['values']]
                fig.add_trace(go.Scatter(
                    x=timestamps, y=numeric_values, mode='lines', name=legend,
                    line=dict(dash='dash' if 'CPU Core' in legend else 'solid'),
                    hovertemplate=f'<b>{legend}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.2f}}<extra></extra>'
                ))

    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="负载值",
        hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_memory_chart(data, output_dir):
    """Creates a stacked area chart for memory usage."""
    panel_title = data.get("panel_title", "Memory Usage")
    panel_id = data.get("panel_id", "no-id")
    traces = []
    color_map = {
        'Apps': '#56a3f2', 'Buffers': '#66bb6a', 'Cached': '#81c784', 'Slab': '#a5d6a7',
        'Swap': '#ffd54f', 'Unused': '#e0e0e0', 'PageTables': '#ff8a65', 'SwapCache': '#ffab91'
    }
    order = ['Apps', 'Buffers', 'Cached', 'Slab', 'Swap', 'PageTables', 'SwapCache', 'Unused']
    all_series = {}
    for target in data.get("targets", []):
        legend = target.get("legendFormat", "")
        mode = next((key for key in order if key in legend), None)
        result_data = target.get("result", {}).get("data", {})
        if mode and result_data.get("resultType") == "matrix" and result_data.get("result"):
            series = result_data["result"][0]
            if 'values' in series and series['values']:
                all_series[mode] = series['values']

    for mode in order:
        if mode in all_series:
            values = all_series[mode]
            timestamps = [datetime.fromtimestamp(v[0]) for v in values]
            numeric_values_gb = [format_bytes(float(v[1]), 'GB') for v in values]
            traces.append(go.Scatter(
                x=timestamps, y=numeric_values_gb, mode='lines', name=mode,
                stackgroup='one', line=dict(width=0.5), fillcolor=color_map.get(mode),
                hovertemplate=f'<b>{mode}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.3f}} GB<extra></extra>'
            ))
            
    if not traces: return None, None
    fig = go.Figure(data=traces)
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="内存使用 (GB)",
        yaxis_ticksuffix=' GB', hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_disk_iops_chart(data, output_dir):
    """Creates a line chart for disk IOps."""
    panel_title = data.get("panel_title", "Disk IOps")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#8c564b', '#e377c2']
    device_colors = {}
    color_idx = 0
    for target in data.get("targets", []):
        op_type = "Read" if "reads_completed" in target.get('query', '') else "Write"
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix":
            for series in result_data.get("result", []):
                device = series.get("metric", {}).get("device", "unknown")
                if device == 'sr0': continue
                if 'values' in series and series['values']:
                    has_data = True
                    if device not in device_colors:
                        device_colors[device] = colors[color_idx % len(colors)]
                        color_idx += 1
                    timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                    numeric_values = [float(v[1]) for v in series['values']]
                    fig.add_trace(go.Scatter(
                        x=timestamps, y=numeric_values, mode='lines', name=f"{device} - {op_type}",
                        line=dict(color=device_colors[device], dash='dash' if op_type == 'Write' else 'solid'),
                        hovertemplate=f'<b>{device} - {op_type}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.1f}} IOps<extra></extra>'
                    ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="IOps (次/秒)",
        hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_context_switches_chart(data, output_dir):
    """Creates a line chart for context switches and interrupts."""
    panel_title = data.get("panel_title", "Context Switches")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix" and result_data.get("result"):
            series = result_data.get("result")[0]
            if 'values' in series and series['values']:
                has_data = True
                legend = target.get("legendFormat", "Trace")
                timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                numeric_values = [float(v[1]) for v in series['values']]
                fig.add_trace(go.Scatter(
                    x=timestamps, y=numeric_values, mode='lines', name=legend,
                    hovertemplate=f'<b>{legend}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:,.0f}} /s<extra></extra>'
                ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="速率 (次/秒)",
        hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_swap_pages_chart(data, output_dir):
    """Creates a line chart for memory page swapping."""
    panel_title = data.get("panel_title", "Memory Pages Swap")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix" and result_data.get("result"):
            series = result_data.get("result")[0]
            if 'values' in series and series['values']:
                has_data = True
                legend = target.get("legendFormat", "Trace")
                timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                numeric_values = [float(v[1]) for v in series['values']]
                fig.add_trace(go.Scatter(
                    x=timestamps, y=numeric_values, mode='lines', name=legend,
                    hovertemplate=f'<b>{legend}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.2f}} pages/s<extra></extra>'
                ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="速率 (页/秒)",
        hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_disk_throughput_chart(data, output_dir):
    """Creates a line chart for disk throughput in MB/s."""
    panel_title = data.get("panel_title", "Disk Throughput")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#8c564b', '#e377c2']
    device_colors = {}
    color_idx = 0
    for target in data.get("targets", []):
        op_type = "Read" if "read_bytes" in target.get('query', '') else "Write"
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix":
            for series in result_data.get("result", []):
                device = series.get("metric", {}).get("device", "unknown")
                if device == 'sr0': continue
                if 'values' in series and series['values']:
                    has_data = True
                    if device not in device_colors:
                        device_colors[device] = colors[color_idx % len(colors)]
                        color_idx += 1
                    timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                    numeric_values_mbs = [format_bytes(float(v[1]), 'MB') for v in series['values']]
                    fig.add_trace(go.Scatter(
                        x=timestamps, y=numeric_values_mbs, mode='lines', name=f"{device} - {op_type}",
                        line=dict(color=device_colors[device], dash='dash' if op_type == 'Write' else 'solid'),
                        hovertemplate=f'<b>{device} - {op_type}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.2f}} MB/s<extra></extra>'
                    ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="吞吐量 (MB/s)",
        yaxis_ticksuffix=' MB/s', hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_file_descriptor_chart(data, output_dir):
    """Creates a line chart for file descriptor usage."""
    panel_title = data.get("panel_title", "File Descriptors")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        if "allocated" in target.get("query", ""):
            result_data = target.get("result", {}).get("data", {})
            if result_data.get("resultType") == "matrix" and result_data.get("result"):
                series = result_data["result"][0]
                if 'values' in series and series['values']:
                    has_data = True
                    timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                    numeric_values = [float(v[1]) for v in series['values']]
                    fig.add_trace(go.Scatter(
                        x=timestamps, y=numeric_values, mode='lines', name="已分配",
                        hovertemplate='<b>已分配</b><br>%{x|%Y-%m-%d %H:%M:%S}<br>%{y:,.0f}<extra></extra>'
                    ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="数量",
        hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_disk_queue_chart(data, output_dir):
    """Creates a line chart for instantaneous disk queue size."""
    panel_title = data.get("panel_title", "Disk Queue Size")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix":
            for series in result_data.get("result", []):
                device = series.get("metric", {}).get("device", "unknown")
                if device == 'sr0': continue
                if 'values' in series and series['values']:
                    has_data = True
                    timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                    numeric_values = [float(v[1]) for v in series['values']]
                    fig.add_trace(go.Scatter(
                        x=timestamps, y=numeric_values, mode='lines', name=device,
                        hovertemplate=f'<b>{device}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.0f}} 个请求<extra></extra>'
                    ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="队列中的请求数",
        hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_disk_utilization_chart(data, output_dir):
    """Creates a line chart for disk utilization percentage."""
    panel_title = data.get("panel_title", "Disk Utilization")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix":
            for series in result_data.get("result", []):
                device = series.get("metric", {}).get("device", "unknown")
                if device == 'sr0': continue
                if 'values' in series and series['values']:
                    has_data = True
                    timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                    numeric_values_pct = [float(v[1]) * 100 for v in series['values']]
                    fig.add_trace(go.Scatter(
                        x=timestamps, y=numeric_values_pct, mode='lines', name=device,
                        hovertemplate=f'<b>{device}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.2f}}%<extra></extra>'
                    ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="磁盘繁忙率 (%)",
        yaxis_ticksuffix='%', hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_disk_latency_chart(data, output_dir):
    """Creates a line chart for disk average wait time in ms."""
    panel_title = data.get("panel_title", "Disk Latency")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        op_type = "Read" if "read_time" in target.get('query', '') else "Write"
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix":
            for series in result_data.get("result", []):
                device = series.get("metric", {}).get("device", "unknown")
                if device == 'sr0': continue
                if 'values' in series and series['values']:
                    has_data = True
                    timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                    numeric_values_ms = [float(v[1]) * 1000 if v[1] != "NaN" else None for v in series['values']]
                    fig.add_trace(go.Scatter(
                        x=timestamps, y=numeric_values_ms, mode='lines', name=f"{device} - {op_type}",
                        hovertemplate=f'<b>{device} - {op_type}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.2f}} ms<extra></extra>'
                    ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="平均延迟 (ms)",
        yaxis_ticksuffix=' ms', hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title
    
def create_scrape_duration_chart(data, output_dir):
    """Creates a line chart for node exporter collector durations."""
    panel_title = data.get("panel_title", "Scrape Duration")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix":
            for series in result_data.get("result", []):
                collector = series.get("metric", {}).get("collector", "unknown")
                if 'values' in series and series['values']:
                    has_data = True
                    timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                    numeric_values_ms = [float(v[1]) * 1000 for v in series['values']]
                    fig.add_trace(go.Scatter(
                        x=timestamps, y=numeric_values_ms, mode='lines', name=collector,
                        hovertemplate=f'<b>{collector}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.3f}} ms<extra></extra>'
                    ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="采集耗时 (ms)",
        yaxis_ticksuffix=' ms', hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_inode_usage_chart(data, output_dir):
    """Creates a line chart for free inodes on filesystems."""
    panel_title = data.get("panel_title", "Free Inodes")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix":
            for series in result_data.get("result", []):
                mountpoint = series.get("metric", {}).get("mountpoint", "unknown")
                # Filter out filesystems that don't use traditional inodes
                if 'fuse' in series.get("metric", {}).get("fstype", "") or 'vfat' in series.get("metric", {}).get("fstype", ""):
                    continue
                if 'values' in series and series['values']:
                    has_data = True
                    timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                    numeric_values = [float(v[1]) for v in series['values']]
                    fig.add_trace(go.Scatter(
                        x=timestamps, y=numeric_values, mode='lines', name=mountpoint,
                        hovertemplate=f'<b>{mountpoint}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:,.0f}} free<extra></extra>'
                    ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="可用 Inode 数量",
        hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_filesystem_space_chart(data, output_dir):
    """Creates a line chart for available filesystem space in GB."""
    panel_title = data.get("panel_title", "Filesystem Space")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix":
            for series in result_data.get("result", []):
                mountpoint = series.get("metric", {}).get("mountpoint", "unknown")
                if 'values' in series and series['values']:
                    # Filter out consistently zero-sized filesystems
                    if all(float(v[1]) == 0 for v in series['values']):
                        continue
                    has_data = True
                    timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                    numeric_values_gb = [format_bytes(float(v[1]), 'GB') for v in series['values']]
                    fig.add_trace(go.Scatter(
                        x=timestamps, y=numeric_values_gb, mode='lines', name=mountpoint,
                        hovertemplate=f'<b>{mountpoint}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.2f}} GB<extra></extra>'
                    ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="可用空间 (GB)",
        yaxis_ticksuffix=' GB', hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_filesystem_state_chart(data, output_dir):
    """Creates a chart for filesystem read-only or error states."""
    panel_title = data.get("panel_title", "Filesystem State")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix":
            for series in result_data.get("result", []):
                if 'values' in series and series['values']:
                    has_data = True
                    legend = target.get("legendFormat", "State")
                    timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                    numeric_values = [float(v[1]) for v in series['values']]
                    fig.add_trace(go.Scatter(
                        x=timestamps, y=numeric_values, mode='lines', name=legend,
                        hovertemplate=f'<b>{legend}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>State: %{{y}}<extra></extra>'
                    ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="状态 (1 = True)",
        yaxis=dict(range=[-0.1, 1.1]), # Fix range for binary data
        hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title
    
def generate_generic_chart(data, output_dir):
    """Fallback function for any panel without a specialized chart function."""
    panel_title = data.get("panel_title", "Generic Chart")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix":
            for series in result_data.get("result", []):
                if 'values' in series and series['values']:
                    has_data = True
                    label = series.get("metric", {}).get("device", panel_title)
                    timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                    numeric_values = [float(v[1]) for v in series['values']]
                    fig.add_trace(go.Scatter(x=timestamps, y=numeric_values, mode='lines', name=label))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="值",
        hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

# ==============================================================================
# --- (在此处粘贴新函数) ---
# ==============================================================================

def create_network_packets_chart(data, output_dir):
    """为网络包流量创建专属图表 (收/发)。"""
    panel_title = data.get("panel_title", "Network Packets")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    
    for target in data.get("targets", []):
        op_type = "Rx in" if "receive_packets" in target.get('query', '') else "Tx out"
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix":
            for series in result_data.get("result", []):
                device = series.get("metric", {}).get("device", "unknown")
                if 'values' in series and series['values']:
                    has_data = True
                    timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                    numeric_values = [float(v[1]) for v in series['values']]
                    
                    fig.add_trace(go.Scatter(
                        x=timestamps, y=numeric_values, mode='lines',
                        name=f"{device} - {op_type}",
                        hovertemplate=f'<b>{device} - {op_type}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.2f}} packets/s<extra></extra>'
                    ))

    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="速率 (包/秒)",
        hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_udp_traffic_chart(data, output_dir):
    """为 UDP 数据报流量创建专属图表。"""
    panel_title = data.get("panel_title", "UDP Traffic")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        legend = target.get("legendFormat", "Trace")
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix" and result_data.get("result"):
            series = result_data["result"][0]
            if 'values' in series and series['values']:
                has_data = True
                timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                numeric_values = [float(v[1]) for v in series['values']]
                fig.add_trace(go.Scatter(
                    x=timestamps, y=numeric_values, mode='lines', name=legend,
                    hovertemplate=f'<b>{legend}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.2f}} datagrams/s<extra></extra>'
                ))
                
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="速率 (数据报/秒)",
        hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_conntrack_chart(data, output_dir):
    """为 Netfilter 连接跟踪创建专属图表。"""
    panel_title = data.get("panel_title", "NF Conntrack")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix" and result_data.get("result"):
            series = result_data["result"][0]
            if 'values' in series and series['values']:
                has_data = True
                legend = target.get("legendFormat", "Trace")
                timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                numeric_values = [float(v[1]) for v in series['values']]
                fig.add_trace(go.Scatter(
                    x=timestamps, y=numeric_values, mode='lines', name=legend,
                    line=dict(dash='dash' if 'limit' in legend else 'solid'),
                    hovertemplate=f'<b>{legend}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:,.0f}}<extra></extra>'
                ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="连接数",
        hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_process_status_chart(data, output_dir):
    """为进程状态创建专属图表。"""
    panel_title = data.get("panel_title", "Process Status")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix" and result_data.get("result"):
            series = result_data["result"][0]
            if 'values' in series and series['values']:
                has_data = True
                legend = target.get("legendFormat", "Trace")
                timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                numeric_values = [float(v[1]) for v in series['values']]
                fig.add_trace(go.Scatter(
                    x=timestamps, y=numeric_values, mode='lines', name=legend,
                    hovertemplate=f'<b>{legend}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.0f}} 个进程<extra></extra>'
                ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="进程数",
        hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_sockstat_tcp_chart(data, output_dir):
    """为 TCP Socket 状态创建专属图表。"""
    panel_title = data.get("panel_title", "TCP Sockets")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix" and result_data.get("result"):
            series = result_data["result"][0]
            if 'values' in series and series['values']:
                has_data = True
                legend = target.get("legendFormat", "Trace")
                timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                numeric_values = [float(v[1]) for v in series['values']]
                fig.add_trace(go.Scatter(
                    x=timestamps, y=numeric_values, mode='lines', name=legend,
                    hovertemplate=f'<b>{legend}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.0f}} 个 Sockets<extra></extra>'
                ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="Sockets 数量",
        hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

# ==============================================================================
# --- (在此处粘贴新函数) ---
# ==============================================================================

def create_tcp_connections_chart(data, output_dir):
    """为TCP连接数创建专属图表。"""
    panel_title = data.get("panel_title", "TCP Connections")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix" and result_data.get("result"):
            series = result_data["result"][0]
            if 'values' in series and series['values']:
                has_data = True
                legend = target.get("legendFormat", "Trace")
                timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                numeric_values = [float(v[1]) for v in series['values']]
                fig.add_trace(go.Scatter(
                    x=timestamps, y=numeric_values, mode='lines', name=legend,
                    hovertemplate=f'<b>{legend}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.0f}} 连接<extra></extra>'
                ))

    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="连接数量",
        hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_memory_vmalloc_chart(data, output_dir):
    """为内核Vmalloc内存使用创建专属图表。"""
    panel_title = data.get("panel_title", "Memory Vmalloc")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    
    # 由于Total的值过大，我们只关注Used和Chunk
    for target in data.get("targets", []):
        legend = target.get("legendFormat", "")
        if "Total" in legend:
            continue # 忽略Total值以获得更好的可视化效果

        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix" and result_data.get("result"):
            series = result_data["result"][0]
            if 'values' in series and series['values']:
                has_data = True
                # 从legend中提取更简洁的名称
                simple_legend = legend.split('–')[0].strip()
                timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                # 转换为 MB
                numeric_values_mb = [format_bytes(float(v[1]), 'MB') for v in series['values']]
                fig.add_trace(go.Scatter(
                    x=timestamps, y=numeric_values_mb, mode='lines', name=simple_legend,
                    hovertemplate=f'<b>{simple_legend}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.2f}} MB<extra></extra>'
                ))

    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="大小 (MB)",
        yaxis_ticksuffix=' MB', hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_network_traffic_basic_chart(data, output_dir):
    """为基础网络流量创建专属图表，单位自动适配 (bits/s)。"""
    panel_title = data.get("panel_title", "Network Traffic")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix":
            for series in result_data.get("result", []):
                device = series.get("metric", {}).get("device", "unknown")
                op_type = "Rx in" if "Rx" in target.get("legendFormat", "") else "Tx out"
                
                if 'values' in series and series['values']:
                    has_data = True
                    timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                    numeric_values = [float(v[1]) for v in series['values']]
                    
                    fig.add_trace(go.Scatter(
                        x=timestamps, y=numeric_values, mode='lines',
                        name=f"{device} - {op_type}",
                        hovertemplate=f'<b>{device} - {op_type}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.2f}}b/s<extra></extra>'
                    ))

    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="流量 (bits/秒)",
        hovermode='x unified', template='plotly_white',
        yaxis_title_text='流量 (bits/秒)',
        yaxis_type='log',  # 使用对数坐标轴以更好地显示差异巨大的流量
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

# ==============================================================================
# --- (在此处粘贴新函数) ---
# ==============================================================================

def create_icmp_errors_chart(data, output_dir):
    """为 ICMP 错误创建专属图表。"""
    panel_title = data.get("panel_title", "ICMP Errors")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix" and result_data.get("result"):
            series = result_data["result"][0]
            if 'values' in series and series['values']:
                has_data = True
                legend = target.get("legendFormat", "Trace")
                timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                numeric_values = [float(v[1]) for v in series['values']]
                fig.add_trace(go.Scatter(
                    x=timestamps, y=numeric_values, mode='lines', name=legend,
                    hovertemplate=f'<b>{legend}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.2f}} errors/s<extra></extra>'
                ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="速率 (错误数/秒)",
        hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_tcp_errors_chart(data, output_dir):
    """为 TCP 错误和重传创建专属图表。"""
    panel_title = data.get("panel_title", "TCP Errors")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix" and result_data.get("result"):
            # This panel might have empty results for some metrics
            if not result_data["result"]:
                continue
            series = result_data["result"][0]
            if 'values' in series and series['values']:
                has_data = True
                legend = target.get("legendFormat", "Trace")
                timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                numeric_values = [float(v[1]) for v in series['values']]
                fig.add_trace(go.Scatter(
                    x=timestamps, y=numeric_values, mode='lines', name=legend,
                    hovertemplate=f'<b>{legend}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.2f}} events/s<extra></extra>'
                ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="速率 (事件/秒)",
        hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_memory_directmap_chart(data, output_dir):
    """为内核 DirectMap 内存使用创建专属图表。"""
    panel_title = data.get("panel_title", "Memory DirectMap")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix" and result_data.get("result"):
            series = result_data["result"][0]
            if 'values' in series and series['values']:
                has_data = True
                legend = target.get("legendFormat", "Trace").split('–')[0].strip()
                timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                numeric_values_gb = [format_bytes(float(v[1]), 'GB') for v in series['values']]
                fig.add_trace(go.Scatter(
                    x=timestamps, y=numeric_values_gb, mode='lines', name=legend,
                    hovertemplate=f'<b>{legend}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.2f}} GB<extra></extra>'
                ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="大小 (GB)",
        yaxis_ticksuffix=' GB', hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_memory_anonymous_chart(data, output_dir):
    """为匿名内存页面使用创建专属图表。"""
    panel_title = data.get("panel_title", "Anonymous Memory")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix" and result_data.get("result"):
            series = result_data["result"][0]
            if 'values' in series and series['values']:
                has_data = True
                legend = target.get("legendFormat", "Trace").split('–')[0].strip()
                timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                numeric_values_mb = [format_bytes(float(v[1]), 'MB') for v in series['values']]
                fig.add_trace(go.Scatter(
                    x=timestamps, y=numeric_values_mb, mode='lines', name=legend,
                    hovertemplate=f'<b>{legend}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.2f}} MB<extra></extra>'
                ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="大小 (MB)",
        yaxis_ticksuffix=' MB', hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

# ==============================================================================
# --- (在此处粘贴新函数) ---
# ==============================================================================

def create_memory_slab_chart(data, output_dir):
    """为内核 Slab 内存使用创建专属图表。"""
    panel_title = data.get("panel_title", "Memory Slab")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix" and result_data.get("result"):
            series = result_data["result"][0]
            if 'values' in series and series['values']:
                has_data = True
                legend = target.get("legendFormat", "Trace").split('–')[0].strip()
                timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                numeric_values_mb = [format_bytes(float(v[1]), 'MB') for v in series['values']]
                fig.add_trace(go.Scatter(
                    x=timestamps, y=numeric_values_mb, mode='lines', name=legend,
                    hovertemplate=f'<b>{legend}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.2f}} MB<extra></extra>'
                ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="内存 (MB)",
        yaxis_ticksuffix=' MB', hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_memory_writeback_chart(data, output_dir):
    """为脏页和回写内存创建专属图表。"""
    panel_title = data.get("panel_title", "Memory Writeback and Dirty")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix" and result_data.get("result"):
            series = result_data["result"][0]
            if 'values' in series and series['values']:
                has_data = True
                legend = target.get("legendFormat", "Trace").split('–')[0].strip()
                timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                # 使用 KB 作为单位，因为这些值通常较小
                numeric_values_kb = [format_bytes(float(v[1]), 'KB') for v in series['values']]
                fig.add_trace(go.Scatter(
                    x=timestamps, y=numeric_values_kb, mode='lines', name=legend,
                    hovertemplate=f'<b>{legend}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:,.0f}} KB<extra></extra>'
                ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="内存 (KB)",
        yaxis_ticksuffix=' KB', hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_memory_committed_chart(data, output_dir):
    """为已提交内存创建专属图表。"""
    panel_title = data.get("panel_title", "Memory Committed")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix" and result_data.get("result"):
            series = result_data["result"][0]
            if 'values' in series and series['values']:
                has_data = True
                legend = target.get("legendFormat", "Trace").split('–')[0].strip()
                timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                numeric_values_gb = [format_bytes(float(v[1]), 'GB') for v in series['values']]
                fig.add_trace(go.Scatter(
                    x=timestamps, y=numeric_values_gb, mode='lines', name=legend,
                    line=dict(dash='dash' if 'Limit' in legend else 'solid'),
                    hovertemplate=f'<b>{legend}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.2f}} GB<extra></extra>'
                ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="内存 (GB)",
        yaxis_ticksuffix=' GB', hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

# ==============================================================================
# --- (在此处粘贴新函数) ---
# ==============================================================================

def create_network_errors_chart(data, output_dir):
    """为网络错误、丢包、FIFO错误创建专属图表。"""
    panel_title = data.get("panel_title", "Network Errors")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix":
            for series in result_data.get("result", []):
                if 'values' in series and series['values']:
                    # 仅当数据不全为0时才认为有数据，避免空图表
                    if not all(float(v[1]) == 0 for v in series['values']):
                        has_data = True
                    
                    legend = target.get("legendFormat", "Trace").replace("{{device}}", series.get("metric", {}).get("device", ""))
                    timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                    numeric_values = [float(v[1]) for v in series['values']]
                    
                    fig.add_trace(go.Scatter(
                        x=timestamps, y=numeric_values, mode='lines', name=legend,
                        hovertemplate=f'<b>{legend}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.2f}} packets/s<extra></extra>'
                    ))

    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="速率 (包/秒)",
        hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_process_forks_chart(data, output_dir):
    """为进程创建速率 (forks) 创建专属图表。"""
    panel_title = data.get("panel_title", "Process Forks")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix" and result_data.get("result"):
            series = result_data["result"][0]
            if 'values' in series and series['values']:
                has_data = True
                legend = target.get("legendFormat", "Trace")
                timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                numeric_values = [float(v[1]) for v in series['values']]
                fig.add_trace(go.Scatter(
                    x=timestamps, y=numeric_values, mode='lines', name=legend,
                    hovertemplate=f'<b>{legend}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.2f}} forks/s<extra></extra>'
                ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="速率 (forks/秒)",
        hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

def create_exporter_memory_chart(data, output_dir):
    """为 Exporter 进程的内存使用创建专属图表。"""
    panel_title = data.get("panel_title", "Exporter Memory")
    panel_id = data.get("panel_id", "no-id")
    fig = go.Figure()
    has_data = False
    for target in data.get("targets", []):
        legend = target.get("legendFormat", "")
        # 忽略巨大的、无意义的虚拟内存限制
        if "Limit" in legend:
            continue
            
        result_data = target.get("result", {}).get("data", {})
        if result_data.get("resultType") == "matrix" and result_data.get("result"):
            series = result_data["result"][0]
            if 'values' in series and series['values']:
                has_data = True
                timestamps = [datetime.fromtimestamp(v[0]) for v in series['values']]
                numeric_values_mb = [format_bytes(float(v[1]), 'MB') for v in series['values']]
                fig.add_trace(go.Scatter(
                    x=timestamps, y=numeric_values_mb, mode='lines', name=legend,
                    hovertemplate=f'<b>{legend}</b><br>%{{x|%Y-%m-%d %H:%M:%S}}<br>%{{y:.2f}} MB<extra></extra>'
                ))
    if not has_data: return None, None
    fig.update_layout(
        title=dict(text='', x=0.5), xaxis_title="时间", yaxis_title="内存 (MB)",
        yaxis_ticksuffix=' MB', hovermode='x unified', template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=40, b=20)
    )
    safe_title = sanitize_filename(panel_title.lower())
    chart_filename = f"chart_{panel_id}_{safe_title}.html"
    fig.write_html(os.path.join(output_dir, chart_filename), full_html=False, include_plotlyjs='../js/plotly.min.js')
    return chart_filename, panel_title

# ==============================================================================
# --- Main Report Generation ---
# ==============================================================================

import os
import json
import re
from datetime import datetime

# 假设所有 create_..._chart 和 generate_generic_chart 函数已在此处或导入的文件中定义
# 例如: from chart_generators import create_cpu_chart, ...

# 确保在文件顶部有这些导入
import os
import json
import re
from datetime import datetime

# ... (这里是所有 create_..._chart 函数) ...

def create_performance_report(data_dir: str, charts_dir: str, report_filename: str) -> dict:
    """
    根据指定的数据目录生成包含 pyecharts 图表的 HTML 性能报告。
    HTML模板已硬编码在此函数内部。

    Args:
        data_dir (str): 存放 JSON 数据文件的目录路径。
        charts_dir (str): 用于存放生成的图表 HTML 文件的目录路径。
        report_filename (str): 最终生成的 HTML 报告的完整文件路径。

    Returns:
        dict: 一个包含操作状态和消息的字典。
    """
    try:
        # --- 核心改动 1: 验证输入路径 (移除 template_path 的验证) ---
        if not os.path.isdir(data_dir):
            return {"status": "error", "message": f"数据目录不存在: '{data_dir}'"}

        os.makedirs(charts_dir, exist_ok=True)

        # --- 函数映射和报告结构 (保持不变) ---
        function_mapper = {
            3: create_cpu_chart, 7: create_system_load_chart, 8: create_context_switches_chart,
            9: create_disk_iops_chart, 22: create_swap_pages_chart, 24: create_memory_chart,
            28: create_file_descriptor_chart, 33: create_disk_throughput_chart, 34: create_disk_queue_chart,
            36: create_disk_utilization_chart, 37: create_disk_latency_chart, 40: create_scrape_duration_chart,
            41: create_inode_usage_chart, 42: create_disk_throughput_chart, 43: create_filesystem_space_chart,
            44: create_filesystem_state_chart, 50: create_icmp_errors_chart, 55: create_udp_traffic_chart,
            60: create_network_packets_chart, 61: create_conntrack_chart, 62: create_process_status_chart,
            63: create_sockstat_tcp_chart, 64: create_file_descriptor_chart, 70: create_memory_vmalloc_chart,
            74: create_network_traffic_basic_chart, 77: create_cpu_chart, 78: create_memory_chart,
            82: generate_generic_chart, 85: create_tcp_connections_chart, 91: create_tcp_errors_chart,
            104: create_tcp_errors_chart, 109: create_udp_traffic_chart, 115: create_udp_traffic_chart,
            124: create_sockstat_tcp_chart, 125: create_sockstat_tcp_chart, 126: generate_generic_chart,
            127: create_disk_utilization_chart, 128: create_memory_directmap_chart, 129: create_memory_anonymous_chart,
            130: create_memory_writeback_chart, 131: create_memory_slab_chart, 133: create_disk_iops_chart,
            135: create_memory_committed_chart, 136: create_cpu_chart, 137: create_memory_writeback_chart,
            138: create_memory_slab_chart, 140: create_memory_vmalloc_chart, 141: create_network_errors_chart,
            142: create_network_errors_chart, 143: create_network_errors_chart, 144: create_network_errors_chart,
            145: create_network_errors_chart, 146: create_network_packets_chart, 148: create_process_forks_chart,
            149: create_exporter_memory_chart,
        }
        report_structure = [
            {"group_title": "系统概览", "charts": [
                {"panel_id": 77, "title": "CPU 使用率"},
                {"panel_id": 7, "title": "系统平均负载"}, {"panel_id": 62, "title": "进程状态"},
                {"panel_id": 148, "title": "进程创建速率 (Forks)"}]},
            {"group_title": "内存", "charts": [
                {"panel_id": 24, "title": "内存使用情况 (详细)"}, {"panel_id": 22, "title": "内存页面交换"}, {"panel_id": 135, "title": "已提交内存 (Committed Memory)"},
                {"panel_id": 136, "title": "内存LRU活动状态 (%)"}, {"panel_id": 129, "title": "匿名内存页面 (Anonymous Pages)"},
                {"panel_id": 138, "title": "共享与映射内存"}, {"panel_id": 130, "title": "脏页与回写内存"},
                {"panel_id": 131, "title": "内核Slab内存"}, {"panel_id": 70, "title": "内核 Vmalloc 内存"},
                {"panel_id": 128, "title": "内核 DirectMap 内存"}, {"panel_id": 140, "title": "大页内存 (HugePages)"}]},
            {"group_title": "网络", "charts": [
                {"panel_id": 74, "title": "网络数据流量"}, {"panel_id": 60, "title": "网络包流量"},
                {"panel_id": 146, "title": "网络多播流量"}, {"panel_id": 142, "title": "网络流量错误"},
                {"panel_id": 143, "title": "网络流量丢包"}, {"panel_id": 144, "title": "网络FIFO缓冲区错误"},
                {"panel_id": 141, "title": "网络压缩包流量"}, {"panel_id": 85, "title": "TCP 连接数"},
                {"panel_id": 82, "title": "TCP 连接建立速率"}, {"panel_id": 104, "title": "TCP 错误"},
                {"panel_id": 91, "title": "TCP SYN Cookies"}, {"panel_id": 63, "title": "TCP Sockets 状态"},
                {"panel_id": 55, "title": "UDP 数据报流量"}, {"panel_id": 109, "title": "UDP 错误"},
                {"panel_id": 115, "title": "ICMP 流量"}, {"panel_id": 50, "title": "ICMP 接收错误"},
                {"panel_id": 61, "title": "网络连接跟踪 (NF Conntrack)"}, {"panel_id": 124, "title": "UDP / UDPLite Sockets"},
                {"panel_id": 125, "title": "RAW / FRAG Sockets"}, {"panel_id": 126, "title": "Sockets 总数"}]},
            {"group_title": "磁盘与文件系统", "charts": [
                {"panel_id": 43, "title": "文件系统可用空间"}, {"panel_id": 41, "title": "文件系统可用 Inodes"},
                {"panel_id": 9, "title": "磁盘读写 IOps"}, {"panel_id": 133, "title": "磁盘合并读写数"},
                {"panel_id": 42, "title": "磁盘吞吐量"}, {"panel_id": 37, "title": "磁盘平均等待时间 (延迟)"},
                {"panel_id": 36, "title": "磁盘繁忙率 (按IO时间)"}, 
                {"panel_id": 34, "title": "磁盘瞬时队列大小"}, {"panel_id": 44, "title": "文件系统只读或错误状态"}]},
            {"group_title": "Node Exporter 自身监控", "charts": [
                {"panel_id": 28, "title": "系统文件描述符使用情况"}, {"panel_id": 64, "title": "Exporter 进程文件描述符使用"},
                {"panel_id": 149, "title": "Exporter 进程内存使用"}, {"panel_id": 40, "title": "Node Exporter 采集器耗时"}]},
        ]

        json_files = {}
        for f in os.listdir(data_dir):
            if f.endswith(".json"):
                match = re.search(r'panel_(\d+)_', f)
                if match:
                    json_files[int(match.group(1))] = os.path.join(data_dir, f)

        panels_html_content = ""
        charts_dir_basename = os.path.basename(charts_dir)

        for group in report_structure:
            # ... (这部分循环逻辑保持不变)
            group_html_content = ""
            has_charts_in_group = False

            for chart_def in group["charts"]:
                panel_id_to_find = chart_def["panel_id"]
                
                if panel_id_to_find in json_files:
                    json_path = json_files[panel_id_to_find]
                    with open(json_path, 'r', encoding='utf-8') as f:
                        panel_data = json.load(f)
                    if "error" in panel_data.get("result", {}):
                        continue

                    chart_function = function_mapper.get(panel_id_to_find, generate_generic_chart)
                    chart_file, _ = chart_function(panel_data, charts_dir)

                    if chart_file:
                        has_charts_in_group = True
                        display_title = chart_def["title"]
                        description = panel_data.get("description", "无详细描述。")
                        iframe_src = f"{charts_dir_basename}/{chart_file}"
                        
                        group_html_content += f"""
                <div class="panel">
                    <h3>{display_title}</h3>
                    <p class="description">{description}</p>
                    <div class="panel-content">
                        <iframe src="{iframe_src}"></iframe>
                    </div>
                </div>"""

            if has_charts_in_group:
                panels_html_content += f"""
            <div class="group-container">
                <h2 class="group-title collapsible">{group['group_title']}</h2>
                <div class="panel-container">
                    {group_html_content}
                </div>
            </div>"""

        # --- 核心改动 2: 在此处硬编码HTML模板 ---
        template_content = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>系统性能监控报告</title>
    <style>
        body {
            background-color: #f7faff; color: #2c3e50;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            margin: 0; padding: 25px;
        }
        .container { max-width: 1600px; margin: 0 auto; }
        .header { text-align: center; padding-bottom: 20px; border-bottom: 1px solid #e0e6ed; margin-bottom: 30px; }
        .header h1 { font-size: 2.2em; font-weight: 600; margin: 0; color: #0056b3; }
        .header p { color: #6c757d; margin-top: 5px; font-size: 1.1em; }
        .group-container {
            background-color: #ffffff; border-radius: 12px; border: 1px solid #e0e6ed;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05); margin-bottom: 30px;
        }
        .group-title {
            font-size: 1.7em; color: #0056b3; padding: 20px 25px; margin: 0;
            border-bottom: 1px solid #e0e6ed;
        }
        
        /* --- 折叠功能 CSS --- */
        .collapsible {
            cursor: pointer;
            user-select: none;
            position: relative;
        }
        .collapsible::after {
            content: '▼'; /* 折叠状态的图标 */
            font-size: 0.7em;
            position: absolute;
            right: 25px;
            top: 50%;
            transform: translateY(-50%);
            transition: transform 0.3s ease;
        }
        .collapsible.active::after {
            transform: translateY(-50%) rotate(180deg); /* 展开状态的图标 */
        }
        .panel-container {
            padding: 25px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 25px;
            /* --- 折叠核心样式 --- */
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.5s ease-in-out, padding 0.5s ease-in-out;
            padding-top: 0;
            padding-bottom: 0;
        }
        /* --- 展开时的样式 --- */
        .panel-container.active {
             padding-top: 25px;
             padding-bottom: 25px;
        }
        
        .panel {
            border: 1px solid #e9ecef; border-radius: 8px; overflow: hidden;
            display: flex; flex-direction: column; background-color: #fff;
        }
        .panel h3 {
            margin: 0; font-size: 1.2em; font-weight: 600; color: #343a40;
            background-color: #f8f9fa; padding: 15px; border-bottom: 1px solid #e9ecef;
        }
        .panel .description {
            font-size: 0.9em; padding: 15px 15px 0 15px; color: #555; margin-bottom: 10px;
        }
        .panel-content { flex-grow: 1; }
        iframe { width: 100%; height: 400px; border: none; }
        footer {
            text-align: center; margin-top: 30px; padding-top: 20px;
            border-top: 1px solid #e0e6ed; font-size: 0.9em; color: #888;
        }
    </style>
</head>
<body>
    <div class="container">
        <div id="report-content">
            {{PANELS_CONTENT}}
        </div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function () {
            const collapsibles = document.querySelectorAll('.collapsible');

            collapsibles.forEach(item => {
                const content = item.nextElementSibling;
                if (content) {
                    item.classList.add('active'); 
                    content.classList.add('active'); 
                    content.style.maxHeight = '50000px'; 
                }

                item.addEventListener('click', function () {
                    this.classList.toggle('active');
                    const content = this.nextElementSibling;
                    
                    if (content.style.maxHeight) {
                        content.style.maxHeight = null;
                        content.classList.remove('active');
                    } else {
                        content.style.maxHeight = content.scrollHeight + "px";
                        content.classList.add('active');
                    }
                });
            });
        });
    </script>
</body>
</html>
        """

        # --- 核心改动 3: 移除从文件加载模板的逻辑 ---
        # with open(template_path, 'r', encoding='utf-8') as f:
        #     template_content = f.read()

        final_report_html = template_content.replace("{{PANELS_CONTENT}}", panels_html_content)
        final_report_html = final_report_html.replace("{{GENERATION_TIME}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        with open(report_filename, "w", encoding='utf-8') as f:
            f.write(final_report_html)

        report_abs_path = os.path.abspath(report_filename)
        return {
            "status": "success",
            "message": "报告已成功生成!",
            "report_path": report_abs_path
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"生成报告时发生未知错误: {str(e)}"
        }

if __name__ == '__main__':
    # 定义脚本所在的目录作为基础路径
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 基于脚本目录构建路径
    data_dir_path = os.path.join(script_dir, 'panel_data')
    charts_dir_path = os.path.join(script_dir, 'charts')
    report_file_path = os.path.join(script_dir, 'performance_report.html')

    print("开始生成性能报告...")
    print(f"数据源: {data_dir_path}")
    print(f"图表输出至: {charts_dir_path}")

    # 使用更新后的参数调用函数
    result = create_performance_report(
        data_dir='D:\kylin(1)\kylin\data\prometheus\panel_data',
        charts_dir='D:\kylin(1)\kylin\\frontend\public\charts',
        report_filename='D:\kylin(1)\kylin\\frontend\public\monitoring_report.html'
    )

    # 打印函数返回的结果
    if result.get("status") == "success":
        print("\n报告生成成功!")
        print(f"报告路径: {result.get('report_path')}")
    else:
        print("\n报告生成失败。")
        print(f"错误信息: {result.get('message')}")