//资产日志组件 
    const AssetLogs = ({ onOpenExplanationModal }) => {
        // --- 1. 状态管理 ---
        const [logs, setLogs] = React.useState([]);
        const [totalLogs, setTotalLogs] = React.useState(0);
        
        // 新增状态：用于管理日志文件列表和当前选中的文件
        const [logFiles, setLogFiles] = React.useState([]);
        const [selectedLogFile, setSelectedLogFile] = React.useState('');
        
        // 修改状态：将 loading 分为两种，一种是全局加载（首次），一种是表格刷新
        const [isInitialLoading, setIsInitialLoading] = React.useState(true);
        const [isTableLoading, setIsTableLoading] = React.useState(false);

        // 分页状态
        const [currentPage, setCurrentPage] = React.useState(1);
        const [pageSize, setPageSize] = React.useState(10);
        
        // --- 2. 数据获取 ---
        const API_BASE_URL = 'http://localhost:5000';

        // useCallback 优化，当 selectedLogFile 或 pageSize 变化时，重新创建函数
        const fetchLogs = React.useCallback(async (filename, page, limit) => {
            if (!filename) return;
            setIsTableLoading(true); // 开始加载表格数据
            try {
                // 使用新的后端服务地址和动态文件名
                const response = await fetch(`${API_BASE_URL}/api/logs/content/${filename}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const allLogs = await response.json();
                
                setTotalLogs(allLogs.length);
                const paginatedData = allLogs.slice((page - 1) * limit, page * limit);
                setLogs(paginatedData);

            } catch (error) {
                console.error(`获取日志文件 "${filename}" 失败:`, error);
                alert(`获取日志文件 "${filename}" 失败: ${error.message}`);
                setLogs([]);
                setTotalLogs(0);
            } finally {
                setIsTableLoading(false); // 结束加载表格数据
            }
        }, []);

        // Effect 1: 仅在组件首次加载时获取日志文件列表
        React.useEffect(() => {
            const fetchLogFiles = async () => {
                try {
                    const response = await fetch(`${API_BASE_URL}/api/logs/files`);
                    const files = await response.json();
                    if (files && files.length > 0) {
                        setLogFiles(files);
                        setSelectedLogFile(files[0]); // 默认选中第一个文件
                    } else {
                        setLogFiles([]);
                    }
                } catch (error) {
                    console.error("获取日志文件列表失败:", error);
                } finally {
                    setIsInitialLoading(false); // 结束初始加载
                }
            };
            fetchLogFiles();
        }, []);

        // Effect 2: 当选中的文件或分页变化时，获取该文件的日志内容
        React.useEffect(() => {
            fetchLogs(selectedLogFile, currentPage, pageSize);
        }, [selectedLogFile, currentPage, pageSize, fetchLogs]);

        // --- 3. 事件处理 ---
        const handleFileChange = (e) => {
            setCurrentPage(1); // 切换文件时，重置到第一页
            setSelectedLogFile(e.target.value);
        };
        const handlePageChange = (newPage) => setCurrentPage(newPage);
        const handlePageSizeChange = (newSize) => { setPageSize(newSize); setCurrentPage(1); };
        const handleRefresh = () => fetchLogs(selectedLogFile, currentPage, pageSize);
        const handleGetExplanation = (logId) => {
            // 从当前页的日志列表中找到完整的日志对象
            const logToExplain = logs.find(log => log.id === logId);
            if (logToExplain) {
                // 调用从父组件传入的函数，并把日志对象作为参数传递过去
                onOpenExplanationModal(logToExplain);
            } else {
                console.error("未找到ID为", logId, "的日志");
                alert("无法获取该日志的详细信息。");
            }
        };

        // --- 4. 渲染 ---
        if (isInitialLoading) {
            return <div className="text-center p-10">正在加载日志文件列表...</div>;
        }

        return (
            <div className="bg-white p-6 rounded-lg shadow-md">
                <div className="flex justify-between items-center mb-5">
                    {/* 新增: 日志文件选择下拉框 */}
                    <div className="flex items-center space-x-4">
                        <select 
                            value={selectedLogFile} 
                            onChange={handleFileChange}
                            className="border border-gray-300 rounded-md py-2 px-3 text-sm focus:ring-2 focus:ring-blue-400"
                        >
                            {logFiles.length === 0 ? (
                                <option>未找到日志文件</option>
                            ) : (
                                logFiles.map(file => <option key={file} value={file}>{file}</option>)
                            )}
                        </select>
                        <span className="text-sm text-gray-600">共获取到 {totalLogs} 条日志信息</span>
                    </div>

                    <button onClick={handleRefresh} className="bg-white border border-gray-300 text-gray-700 font-semibold py-2 px-4 rounded-md hover:bg-gray-50 transition text-sm flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h5M20 20v-5h-5M4 4l5 5M20 20l-5-5"></path></svg>
                        刷新
                    </button>
                </div>
                <div className="overflow-x-auto">
                    <table className="min-w-full text-sm">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="p-3 text-left font-semibold text-gray-600 w-[18%]">时间</th>
                                <th className="p-3 text-left font-semibold text-gray-600 w-[15%]">主机名</th>
                                <th className="p-3 text-left font-semibold text-gray-600 w-[15%]">日志名</th>
                                <th className="p-3 text-left font-semibold text-gray-600 w-[32%]">日志内容</th>
                                <th className="p-3 text-left font-semibold text-gray-600 w-[20%]">日志解释</th>
                            </tr>
                        </thead>
                        <tbody>
                            {isTableLoading ? (
                                <tr><td colSpan="5" className="p-10 text-center text-gray-500">加载中...</td></tr>
                            ) : logs.length === 0 ? (
                                <tr><td colSpan="5" className="p-10 text-center text-gray-500">未找到日志记录。</td></tr>
                            ) : (
                                logs.map(log => (
                                    <tr key={log.id} className="border-b hover:bg-gray-50">
                                        <td className="p-3 text-gray-800 align-top whitespace-nowrap">{log.timestamp}</td>
                                        <td className="p-3 text-gray-800 align-top whitespace-nowrap">{log.hostname}</td>
                                        <td className="p-3 text-gray-800 font-mono align-top whitespace-nowrap">{log.name}</td>
                                        <td className="p-3 text-gray-800 break-words align-top">{log.content}</td>
                                        <td className="p-3 align-top">
                                            <button 
                                                onClick={() => handleGetExplanation(log.id)}
                                                className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200 transition-colors" 
                                                title="调用大模型解释当前日志"
                                            >
                                                🤖 获取解释
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
                <div className="pt-4">
                    <Pagination
                        currentPage={currentPage}
                        totalItems={totalLogs}
                        pageSize={pageSize}
                        onPageChange={handlePageChange}
                        onPageSizeChange={handlePageSizeChange}
                        options={[10, 20, 50]}
                    />
                </div>
            </div>
        );
    };
    // 资产日志组件 结束
