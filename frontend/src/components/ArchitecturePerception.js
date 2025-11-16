const ArchitecturePerception = () => {
      return (
        // 使用 h-full 让 iframe 容器占满父元素的高度
        <div className="bg-transparent rounded-lg w-full h-full">
          <iframe
            src="/frontend/public/TopologyGraph.html"
            title="架构感知 (动态拓扑图)"
            className="w-full h-full border-none rounded-lg"
          ></iframe>
        </div>
      );
    };