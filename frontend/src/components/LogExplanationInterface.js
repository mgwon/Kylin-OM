// LogExplanationInterface.js (新文件)

const LogExplanationInterface = ({ log, onClose }) => {
    // --- 1. 状态管理 ---
    const ws = React.useRef(null);
    const [explanation, setExplanation] = React.useState('');
    const [isLoading, setIsLoading] = React.useState(true);
    const [error, setError] = React.useState('');

    // --- 2. WebSocket 核心逻辑 ---
    React.useEffect(() => {
        // 如果没有传入log对象，则不执行任何操作
        if (!log) {
            setError('没有提供有效的日志信息。');
            setIsLoading(false);
            return;
        }

        // 构建一个清晰的、用于请求解释的提示
        const prompt = `请作为一名资深的运维开发(DevOps)专家，用中文对以下这条日志进行详细分析，并遵循以下格式：
1.  **日志解读**: 简单明了地解释这条日志的核心内容。
2.  **重要性评估**: 评估此日志的级别（例如：信息、警告、错误、严重），并说明判断依据。
3.  **可能原因**: 列出可能触发这条日志的1-3个主要原因。
4.  **建议操作**: 给出具体的排查步骤或解决方案。

**日志原文如下:**
主机名: ${log.hostname}
时间戳: ${log.timestamp}
内容: ${log.content}
`;
        
        // WebSocket 连接地址 (与 LLMInterface 保持一致)
        const wsUrl = `ws://localhost:8003/ws/chat`;
        const socket = new WebSocket(wsUrl);
        ws.current = socket;

        socket.onopen = () => {
            // 连接成功后，自动发送包含日志信息的请求
            const messagePayload = {
                content: prompt,
                role: 'user',
                source: 'user'
            };
            socket.send(JSON.stringify(messagePayload));
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (isLoading) setIsLoading(false); // 收到第一条消息时，停止加载状态

            // 仿照 LLMInterface 处理流式响应
            switch(data.type) {
                case 'streaming_update':
                case 'streaming_end':
                    setExplanation(data.content);
                    break;
                case 'task_completed':
                    // 如果任务完成有最终消息，也更新一下
                    // 任务完成后可以断开连接，因为此界面只做一次性请求
                    ws.current.close();
                    break;
                case 'error':
                    setError(`获取解释时出错: ${data.content}`);
                    setIsLoading(false);
                    break;
                default:
                    break;
            }
        };

        socket.onerror = () => {
            setError('无法连接到智能助理服务，请检查后端是否运行在8003端口。');
            setIsLoading(false);
        };
        
        socket.onclose = () => {
            // console.log("WebSocket connection closed.");
        };

        // 组件卸载时，确保关闭WebSocket连接
        return () => {
            if (ws.current) {
                ws.current.close();
            }
        };

    }, [log]); // 依赖项是 log，当 log 对象变化时会重新执行

    // --- 3. 渲染 ---
    return (
        // 这是一个模态框（Modal）的典型结构
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-2xl w-full max-w-3xl h-[80vh] flex flex-col">
                {/* 头部 */}
                <div className="flex justify-between items-center p-4 border-b">
                    <h3 className="text-lg font-semibold text-gray-800">🤖 日志智能分析</h3>
                    <button onClick={onClose} className="p-2 text-gray-500 hover:text-gray-800 hover:bg-gray-100 rounded-full">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* 内容区 */}
                <div className="flex-1 p-6 overflow-y-auto space-y-4">
                    {/* 原始日志信息 */}
                    <div className="bg-gray-50 p-3 rounded-md border border-gray-200">
                        <h4 className="font-bold text-sm mb-2 text-gray-600">原始日志</h4>
                        <p className="text-xs text-gray-500"><strong>时间:</strong> {log.timestamp}</p>
                        <p className="text-xs text-gray-500"><strong>主机:</strong> {log.hostname}</p>
                        <p className="text-sm text-gray-800 mt-1 font-mono break-all">{log.content}</p>
                    </div>

                    {/* 大模型解释 */}
                    <div className="border-t pt-4">
                        <h4 className="font-bold text-sm mb-2 text-gray-600">大模型分析结果</h4>
                        {isLoading && <p className="text-gray-500 animate-pulse">正在获取解释，请稍候...</p>}
                        {error && <p className="text-red-600 bg-red-50 p-3 rounded-md">{error}</p>}
                        {/* 使用 prose 来优化 markdown 渲染效果，white-space: pre-wrap 保留换行和空格 */}
                        <div className="text-sm text-gray-800 prose max-w-none" style={{whiteSpace: 'pre-wrap'}}>
                            {explanation}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
