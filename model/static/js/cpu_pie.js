// cpu_chart.js
function renderCpuChart(containerId, value_i ,value_ii, value_iii, value_iv, value_v) {
    var dom = document.getElementById(containerId);
    var myChart = echarts.init(dom, null, {
      renderer: 'canvas',
      useDirtyRect: false
    });
    var app = {};

    var option = {
  tooltip: {
    trigger: 'item'
  },
  legend: {
    top: '3%',
    left: 'center',
    textStyle: {
        color: '#66B2FF' // 修改图例文字的颜色
    }
  },
  series: [
    {
      name: 'CPU利用率',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 18,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: [
        { value: value_i, name: '0~20 %' , itemStyle: { color: '#6666FF' } },
        { value: value_ii, name: '20~40 %' , itemStyle: { color: '#66B2FF' } },
        { value: value_iii, name: '40~60 %' , itemStyle: { color: '#66FF66' } },
        { value: value_iv, name: '60~80 %' , itemStyle: { color: '#FFFF66' } },
        { value: value_v, name: '80~100 %' , itemStyle: { color: '#FF4444' } }
      ]
    }
  ]
};

    if (option && typeof option === 'object') {
      myChart.setOption(option);
    }

    window.addEventListener('resize', myChart.resize);
}