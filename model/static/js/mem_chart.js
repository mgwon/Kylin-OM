// mem_chart.js
function renderCpuChart(containerId, timestamps, clocktime, Totalmemory_size, Usedmemory_size, Freememory_size, Memory_usage, Swapmemory_size, UsedSwapmemory_size, FreeSwapmemory_size, Swapmemory_usage) {
    var dom = document.getElementById(containerId);
    var myChart = echarts.init(dom, null, {
      renderer: 'canvas',
      useDirtyRect: false
    });

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
          data: Memory_usage,
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
                 '内存利用率: ' + point.value + '%<br>' +
                 '总内存: ' + Totalmemory_size[index] + ' MB<br>' +
                 '已用内存: ' + Usedmemory_size[index] + ' MB<br>' +
                 '空闲内存: ' + Freememory_size[index] + ' MB<br>' +
                 '交换内存大小: ' + Swapmemory_size[index] + ' Byte<br>' +
                 '交换内存已用大小: ' + UsedSwapmemory_size[index] + ' Byte<br>' +
                 '交换内存空闲大小: ' + FreeSwapmemory_size[index] + ' Byte<br>' +
                 '交换内存使用占比: ' + Swapmemory_usage[index]+ '%'
        }
      }
    };

    if (option && typeof option === 'object') {
      myChart.setOption(option);
    }

    window.addEventListener('resize', myChart.resize);
}