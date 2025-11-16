function renderCpuChart(containerId, timestamps, clocktime, Totaldisk_size, Useddisk_size, Freedisk_size, Disk_usage, readIO_size, writeIO_size, readdisk_time, writedisk_time) {
    var dom = document.getElementById(containerId);
    var myChart = echarts.init(dom, null, {
      renderer: 'canvas',
      useDirtyRect: false
    });
    var app = {};

    var option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow' // 这行代码确保提示框出现在柱状图上
            },
            formatter: function(params) {
                var point = params[0];
                var index = point.dataIndex;
                return '时间戳: ' + point.axisValueLabel + '<br>' +
                    '时间: ' + clocktime[index] + '<br>' +
                    '磁盘利用率: ' + point.value + '%<br>' +
                    '磁盘总空间: ' + Totaldisk_size[index] + ' MB<br>' +
                    '磁盘已使用大小: ' + Useddisk_size[index] + ' MB<br>' +
                    '磁盘空闲大小: ' + Freedisk_size[index] + ' MB<br>' +
                    '磁盘读IO量: ' + readIO_size[index] + ' MB<br>' +
                    '磁盘写IO量: ' + writeIO_size[index] + ' MB<br>' +
                    '磁盘读时间: ' + readdisk_time[index] + ' s<br>' +
                    '磁盘写时间: ' + writedisk_time[index] + ' s';
            }
        },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: [
    {
      type: 'category',
      data: timestamps,
      axisTick: {
        alignWithLabel: true
      }
    }
  ],
  yAxis: [
    {
      type: 'value'
    }
  ],
  series: [
    {
      name: 'Direct',
      type: 'bar',
      barWidth: '60%',
      data: Disk_usage,
      markPoint: {
            data: [
              { type: 'max', name: '瓶颈' } // 标记点名称改为 "瓶颈"
            ],
            label: {
              show: true,
              formatter: function(params) {
                return '瓶颈: ' + params.value + ' %';
              }
            }
          }
    }
  ]
};

    if (option && typeof option === 'object') {
      myChart.setOption(option);
    }

    window.addEventListener('resize', myChart.resize);
}