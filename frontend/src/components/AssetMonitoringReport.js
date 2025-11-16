//资产监控组件开始
    const AssetMonitoringReport = () => {
      return (
        // 使用 h-full 让 iframe 容器占满父元素的高度
        <div className="bg-transparent rounded-lg w-full h-full">
          <iframe
            src="./monitoring_report.html"
            title="资产性能监控报告"
            className="w-full h-full border-none rounded-lg"
          ></iframe>
        </div>
      );
    };
    //资产监控组件结束