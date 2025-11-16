// cpu_chart.js
function renderCpuChart(containerId, timestamps, clocktime, cpuFreqs, cpuLogicsNum, cpuPhysicalsNum, usermodeRuntime, corestateRuntime, IOwaitTime, averloadIn1min, averloadIn5min, averloadIn15min, interruptionsNum, softinterruptionsNum, systemcallsNum, timestamps, cpu_usages, value_i ,value_ii, value_iii, value_iv, value_v) {
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
          data: cpu_usages,
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
      tooltip: { /* 提示框配置 */
        trigger: 'axis', /* 触发类型 */
        formatter: function (params) { /* 格式化函数 */
          var point = params[0]; /* 第一个数据点 */
          var index = params[0].dataIndex;
          /* 显示时间戳和CPU使用率 */
          return '时间戳: ' + point.axisValueLabel + '<br>' +
                 '时间: ' + clocktime[index] + '<br>' +
                 'CPU 利用率: ' + point.value + '%<br>' +
                 'CPU 频率: ' + cpuFreqs[index] + ' MHz<br>' +
                 'CPU 逻辑核心数量: ' + cpuLogicsNum[index] + '<br>' +
                 'CPU 物理核心数量: ' + cpuPhysicalsNum[index] + '<br>' +
                 '用户态运行时间: ' + usermodeRuntime[index] + ' s<br>' +
                 '核心态运行时间: ' + corestateRuntime[index] + ' s<br>' +
                 'IO 等待时间: ' + IOwaitTime[index] + ' s<br>' +
                 '1min内平均负载: ' + averloadIn1min[index] + '<br>' +
                 '5min内平均负载: ' + averloadIn5min[index] + '<br>' +
                 '15min内平均负载: ' + averloadIn15min[index] + '<br>' +
                 '中断次数: ' + interruptionsNum[index] + '<br>' +
                 '软中断次数: ' + softinterruptionsNum[index] + '<br>' +
                 '系统调用次数: ' + systemcallsNum[index];
        }
      }
    };

    if (option && typeof option === 'object') {
      myChart.setOption(option);
    }

    window.addEventListener('resize', myChart.resize);

}