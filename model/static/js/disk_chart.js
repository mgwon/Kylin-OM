// disk_chart.js
function renderCpuChart(containerId, timestamps, clocktime, Totaldisk_size, Useddisk_size, Freedisk_size, Disk_usage, readIO_size, writeIO_size, readdisk_time, writedisk_time) {
    var dom = document.getElementById(containerId);
    var myChart = echarts.init(dom, null, {
      renderer: 'canvas',
      useDirtyRect: false
    });

    var option = {
  polar: {
    radius: [30, '80%']
  },
  angleAxis: {
    max: 4,
    startAngle: 75
  },
  radiusAxis: {
    type: 'category',
    data: ['a', 'b', 'c', 'd']
  },
  tooltip: {},
  series: {
    type: 'bar',
    data: [2, 1.2, 2.4, 3.6],
    coordinateSystem: 'polar',
    label: {
      show: true,
      position: 'middle',
      formatter: '{b}: {c}'
    }
  }
};
    var option = {
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: timestamps
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '瓶颈', // 系列名称改为 "瓶颈"
          data: Disk_usage,
          type: 'line',
          areaStyle: {},
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
      ],
      tooltip: {
        trigger: 'axis',
        formatter: function(params) {
          var point = params[0];
          var index = params[0].dataIndex;
          return '时间戳: ' + point.axisValueLabel + '<br>' +
                 '时间: ' + clocktime[index] + '<br>' +
                 '磁盘利用率: ' + point.value + '%<br>' +
                 '磁盘总空间: ' + Totaldisk_size[index] + ' MB<br>' +
                 '磁盘已使用大小: ' + Useddisk_size[index] + ' MB<br>' +
                 '磁盘空闲大小: ' + Freedisk_size[index] + ' MB<br>' +
                 '磁盘读IO量: ' + readIO_size[index] + ' MB<br>' +
                 '磁盘写IO量: ' + writeIO_size[index] + ' MB<br>' +
                 '磁盘读时间: ' + readdisk_time[index] + ' s<br>' +
                 '磁盘写时间: ' + writedisk_time[index] + 's'
        }
      }
    };

    if (option && typeof option === 'object') {
      myChart.setOption(option);
    }

    window.addEventListener('resize', myChart.resize);
}