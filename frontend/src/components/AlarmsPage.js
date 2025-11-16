//告警页面组件开始
    const AlarmsPage = () => {
        // 数据状态
        const [stats, setStats] = React.useState([]);
        const [originalRecords, setOriginalRecords] = React.useState([]);
        const [displayRecords, setDisplayRecords] = React.useState([]);
        const [loading, setLoading] = React.useState(true); // 全局初始加载状态
        const [error, setError] = React.useState(null);
        // 为告警记录表格创建独立的加载状态
        const [isRecordsLoading, setIsRecordsLoading] = React.useState(false);

        // UI交互状态
        const [recordsCurrentPage, setRecordsCurrentPage] = React.useState(1);
        const [recordsPageSize, setRecordsPageSize] = React.useState(10);
        const [sortOrder, setSortOrder] = React.useState('desc'); // 'asc' 或 'desc'
        
        const [isStatsPanelOpen, setIsStatsPanelOpen] = React.useState(false);
        // 为统计面板的表格添加独立的分页状态
        const [statsCurrentPage, setStatsCurrentPage] = React.useState(1);
        const [statsPageSize, setStatsPageSize] = React.useState(10);

        const [isDetailsPanelOpen, setIsDetailsPanelOpen] = React.useState(false);
        const [selectedAlert, setSelectedAlert] = React.useState(null);
        const [confirmingAlertId, setConfirmingAlertId] = React.useState(null); // 用于控制确认气泡的显示
        
        // 为统计信息标题旁的问号气泡增加状态
        const [isStatsTooltipVisible, setIsStatsTooltipVisible] = React.useState(false);

        // 为标签悬浮提示框增加状态
        const [hoveredTagId, setHoveredTagId] = React.useState(null);

        // 为详情面板中的“异常数据项”表格增加独立分页状态
        const [detailsCurrentPage, setDetailsCurrentPage] = React.useState(1);
        const [detailsPageSize, setDetailsPageSize] = React.useState(10);

        // 从统计数据中计算告警总数
        const totalAlerts = React.useMemo(() => {
            if (!stats || stats.length === 0) return 0;
            return stats.reduce((sum, item) => sum + item.alert_count, 0);
        }, [stats]);
        
        // 主告警记录表格的客户端分页
        const paginatedRecords = React.useMemo(() => {
            const startIndex = (recordsCurrentPage - 1) * recordsPageSize;
            return displayRecords.slice(startIndex, startIndex + recordsPageSize);
        }, [displayRecords, recordsCurrentPage, recordsPageSize]);

        // 统计信息面板表格的客户端分页
        const paginatedStats = React.useMemo(() => {
            const startIndex = (statsCurrentPage - 1) * statsPageSize;
            return stats.slice(startIndex, startIndex + statsPageSize);
        }, [stats, statsCurrentPage, statsPageSize]);

        //为异常详情中的表格添加分页逻辑
        const paginatedDetailsMetrics = React.useMemo(() => {
            if (!selectedAlert) return [];
            const startIndex = (detailsCurrentPage - 1) * detailsPageSize;
            return selectedAlert.details.abnormal_metrics.slice(startIndex, startIndex + detailsPageSize);
        }, [selectedAlert, detailsCurrentPage, detailsPageSize]);

       

        // 数据获取函数
        const fetchData = React.useCallback(async () => {
            // 在函数开始时，不设置 setLoading(true)，由调用者决定
            setError(null);
            try {
                // 并行请求两个API端点
                const [statsResponse, recordsResponse] = await Promise.all([
                    fetch('http://localhost:5000/api/alarms/statistics'),
                    fetch('http://localhost:5000/api/alarms/records')
                ]);

                // 检查两个请求是否都成功
                if (!statsResponse.ok || !recordsResponse.ok) {
                    throw new Error('获取告警数据时网络响应错误');
                }
                
                // 正确地分别解析两个响应
                const statsData = await statsResponse.json();
                const recordsData = await recordsResponse.json();

                // 更新状态
                setStats(statsData.statistics || []);
                const records = recordsData.records || [];
                const sortedRecords = records.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
                setOriginalRecords(sortedRecords);
                setDisplayRecords(sortedRecords);

            } catch (e) {
                console.error("获取告警数据失败:", e);
                setError(`获取告警数据失败: ${e.message}。`);
            }
        }, []); // useCallback 的依赖项为空，表示此函数本身不会改变

        // 页面首次加载时调用
        React.useEffect(() => {
            const initialLoad = async () => {
                setLoading(true);
                await fetchData();
                setLoading(false);
            };
            initialLoad();
        }, [fetchData]); // 依赖于 fetchData 函数


        const handleRefresh = async () => {
            setIsRecordsLoading(true); // 只显示表格的加载状态
            await fetchData(); // 直接调用统一的数据获取函数
            setIsRecordsLoading(false);
        };

        const handleSort = () => {
            const newSortOrder = sortOrder === 'desc' ? 'asc' : 'desc';
            setSortOrder(newSortOrder);
            const sorted = [...displayRecords].sort((a, b) => {
            const dateA = new Date(a.timestamp);
            const dateB = new Date(b.timestamp);
            return newSortOrder === 'desc' ? dateB - dateA : dateA - dateB;
            });
            setDisplayRecords(sorted);
        };

        //确认告警函数 (handleConfirmAlert) 
        const handleConfirmAlert = async (alertIdToConfirm) => {
            try {
                const response = await fetch('http://localhost:5000/api/alarms/confirm', { // 确认URL是正确的
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: alertIdToConfirm }),
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || '确认告警失败');
                }
                
                const result = await response.json();
                alert(result.message); // 显示后端的成功消息

                // 操作成功后，刷新整个页面的数据以保证一致性
                await fetchData();

            } catch (error) {
                console.error("确认告警失败:", error);
                alert(`操作失败: ${error.message}`);
            } finally {
                setConfirmingAlertId(null);
            }
        };
                
        const handleViewDetails = (alert) => {
            setSelectedAlert(alert);
            // 打开详情时重置分页到第一页
            setDetailsCurrentPage(1);
            setIsDetailsPanelOpen(true);
            setIsStatsPanelOpen(false); // 同时确保另一个面板是关闭的
        };
        
        const handleViewStats = () => {
            setIsStatsPanelOpen(true);
            setIsDetailsPanelOpen(false); // 同时确保另一个面板是关闭的
        };

        const handleDownloadReport = (alert) => {
            const reportContent = JSON.stringify(alert, null, 2);
            const blob = new Blob([reportContent], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `alert-report-${alert.id}.json`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        };

        // 如果是首次加载，显示全局加载信息
        if (loading) return <div className="p-4 text-center text-gray-500">正在加载告警数据...</div>;
        if (error) return <div className="p-4 text-center text-red-500 bg-red-50 rounded-md">{error}</div>;

        return (
            <div className="relative">
            {/* 主内容区 */}
            <div className="space-y-4">
                {/* Top Section: Summary & Stats */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* 告警总数 */}
                <div className="bg-blue-600 text-white p-6 rounded-lg flex items-center shadow-lg">
                    <div className="bg-white bg-opacity-20 p-3 rounded-full mr-6">
                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>
                    </div>
                    <div>
                    <h3 className="text-sm font-semibold">告警总数</h3>
                    <p className="text-4xl font-bold">{totalAlerts}</p>
                    </div>
                </div>
                {/* 告警信息统计 */}
                <div className="bg-white p-4 rounded-lg shadow-md relative">
                    <h3 className="font-semibold text-gray-800 mb-3 flex items-center relative">
                    告警信息统计
                    <span 
                        onClick={() => setIsStatsTooltipVisible(prev => !prev)}
                        className="ml-2 w-4 h-4 bg-gray-200 text-gray-600 flex items-center justify-center rounded-full text-xs font-bold cursor-pointer"
                    >
                        ?
                    </span>
                    {isStatsTooltipVisible && (
                        <div className="absolute top-full left-0 mt-2 w-80 bg-white border border-gray-200 rounded-lg shadow-xl z-20 p-4 text-sm font-normal text-gray-700">
                        <p className="font-bold mb-2">此模块用于展示告警信息的统计排名。</p>
                        <p className="mb-2">通过告警数量对主机组进行降序排列，可以帮助您快速定位问题最集中的主机组，从而优先处理。</p>
                        <p>默认仅展示排名第一的主机组，点击右侧“查看更多”可浏览完整排名列表。</p>
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 w-0 h-0 border-l-8 border-l-transparent border-r-8 border-r-transparent border-b-8 border-b-white" style={{marginLeft: '-70px'}}></div>
                        </div>
                    )}
                    </h3>
                    <table className="min-w-full text-sm">
                    <thead className="bg-gray-50">
                        <tr>
                        <th className="p-2 text-left font-semibold text-gray-600 w-1/4">排名</th>
                        <th className="p-2 text-left font-semibold text-gray-600 w-1/2">主机组名称</th>
                        <th className="p-2 text-left font-semibold text-gray-600 w-1/4">告警数</th>
                        </tr>
                    </thead>
                    <tbody>
                    {stats.length > 0 ? (
                        <tr className="border-b">
                            <td className="p-2"><span className="bg-blue-500 text-white rounded-full w-5 h-5 flex items-center justify-center">{stats[0].rank}</span></td>
                            <td className="p-2 text-gray-800">{stats[0].host_group}</td>
                            <td className="p-2 text-red-600 font-semibold">{stats[0].alert_count}</td>
                        </tr>
                        ) : (
                        <tr><td colSpan="3" className="p-4 text-center text-gray-400">暂无统计信息</td></tr>
                        )}
                    </tbody>
                    </table>
                    <button onClick={handleViewStats} className="absolute top-0 right-0 h-full bg-blue-600 hover:bg-blue-700 text-white px-2 rounded-r-lg flex flex-col items-center justify-center font-bold text-xs" style={{ writingMode: 'vertical-rl' }}>
                    查 看 更 多
                    </button>
                </div>
                </div>
                
                {/* Bottom Section: Records Table */}
                <div className="bg-white p-4 rounded-lg shadow-md">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="font-semibold text-gray-800">告警记录</h3>
                    <button onClick={handleRefresh} className="bg-blue-600 text-white py-1 px-4 rounded-md hover:bg-blue-700 transition flex items-center text-sm">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h5M20 20v-5h-5m-1 5a9 9 0 115.66-16.01A9 9 0 019 19z"></path></svg>
                    刷新
                    </button>
                </div>
                <p className="text-sm text-gray-500 mb-3">共获取到 {displayRecords.length} 条记录</p>
                <div className="overflow-x-auto">
                    <table className="min-w-full text-sm text-left">
                    <thead className="bg-gray-50">
                        <tr>
                        <th className="p-3 font-semibold text-gray-600 cursor-pointer" onClick={handleSort}>
                            <div className="flex items-center">
                            时间 {sortOrder === 'desc' ? '↓' : '↑'}
                            </div>
                        </th>
                        <th className="p-3 font-semibold text-gray-600">主机组</th>
                        <th className="p-3 font-semibold text-gray-600">异常主机数</th>
                        <th className="p-3 font-semibold text-gray-600">告警信息</th>
                        <th className="p-3 font-semibold text-gray-600">等级</th>
                        <th className="p-3 font-semibold text-gray-600">操作</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {isRecordsLoading ? (
                        <tr><td colSpan="6" className="p-10 text-center text-gray-500">正在刷新记录...</td></tr>
                        ) : paginatedRecords.length > 0 ? paginatedRecords.map(record => (
                        <tr key={record.id} className="hover:bg-gray-50">
                            <td className="p-3 text-gray-700">{record.timestamp}</td>
                            <td className="p-3 text-gray-700">{record.host_group}</td>
                            <td className="p-3 text-gray-700">{record.abnormal_host_count}</td>
                            <td className="p-3 text-gray-700">{record.message}</td>
                            <td className="p-3 text-gray-700">{record.level}</td>
                            <td className="p-3 space-x-3 text-blue-600 relative">
                            <a href="#" onClick={(e) => { e.preventDefault(); setConfirmingAlertId(record.id); }} className="hover:underline">确认</a>
                            {confirmingAlertId === record.id && (
                                <div className="absolute right-0 top-full mt-2 w-64 bg-white border border-gray-300 rounded-lg shadow-xl z-10 p-4">
                                    <div className="flex items-start">
                                    <svg className="w-6 h-6 text-yellow-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                                    <div>
                                        <p className="font-semibold text-gray-800">确认后,该告警将不再提示</p>
                                        <div className="mt-3 flex justify-end space-x-2">
                                        <button onClick={() => setConfirmingAlertId(null)} className="text-sm bg-gray-200 text-gray-800 px-3 py-1 rounded-md hover:bg-gray-300">取消</button>
                                        <button onClick={() => handleConfirmAlert(record.id)} className="text-sm bg-blue-600 text-white px-3 py-1 rounded-md hover:bg-blue-700">确定</button>
                                        </div>
                                    </div>
                                    </div>
                                </div>
                            )}
                            <a href="#" onClick={(e) => { e.preventDefault(); handleViewDetails(record); }} className="hover:underline">异常详情</a>
                            <a href="#" onClick={(e) => { e.preventDefault(); handleDownloadReport(record); }} className="hover:underline">下载报告</a>
                            </td>
                        </tr>
                        )) : (
                        <tr><td colSpan="6" className="p-10 text-center text-gray-500">暂无告警记录</td></tr>
                        )}
                    </tbody>
                    </table>
                </div>
                {displayRecords.length > 0 && (
                    <div className="pt-4">
                        <Pagination 
                        currentPage={recordsCurrentPage}
                        totalItems={displayRecords.length}
                        pageSize={recordsPageSize}
                        onPageChange={setRecordsCurrentPage}
                        onPageSizeChange={(size) => { setRecordsPageSize(size); setRecordsCurrentPage(1); }}
                        />
                    </div>
                )}
                </div>
            </div>
            
                        {/* 异常详情侧边栏 */}
                        <div className={`fixed top-16 right-0 bottom-0 bg-white shadow-lg transition-transform duration-300 ease-in-out ${isDetailsPanelOpen ? 'translate-x-0' : 'translate-x-full'}`} style={{width: '50%'}}>
                <div className="flex flex-col h-full">
                    <div className="flex justify-between items-center p-4 border-b">
                    <h3 className="text-lg font-semibold text-gray-800">异常信息</h3>
                    <button onClick={() => setIsDetailsPanelOpen(false)} className="text-gray-500 hover:text-gray-800 text-2xl">×</button>
                    </div>
                    {selectedAlert && (
                    <div className="p-4 space-y-4 overflow-y-auto">
                        {/* 异常主机信息 (无改动) */}
                        <div>
                            <table className="min-w-full text-sm text-left">
                                <thead className="bg-gray-50">
                                <tr>
                                    <th className="p-2 w-10 font-semibold text-gray-600">序号</th>
                                    <th className="p-2 font-semibold text-gray-600">主机名</th>
                                    <th className="p-2 font-semibold text-gray-600">IP</th>
                                    <th className="p-2 font-semibold text-gray-600">异常项个数</th>
                                    <th className="p-2 font-semibold text-gray-600">根因节点</th>
                                </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200">
                                {selectedAlert.details.abnormal_hosts.map((host, index) => (
                                    <tr key={host.host_id}>
                                        <td className="p-2 text-gray-700">{index + 1}</td>
                                        <td className="p-2 text-gray-700">{host.host_name}</td>
                                        <td className="p-2 text-gray-700">{host.ip}</td>
                                        <td className="p-2 text-gray-700">{host.abnormal_item_count}</td>
                                        <td className="p-2 text-gray-700">{host.is_root_cause_node}</td>
                                    </tr>
                                ))}
                                </tbody>
                            </table>
                        </div>
                        {/* 异常数据项 */}
                        <div>
                            <table className="min-w-full text-sm text-left table-fixed">
                                <thead className="bg-gray-50">
                                <tr>
                                    <th className="p-2 w-10 font-semibold text-gray-600">序号</th>
                                    <th className="p-2 w-40 font-semibold text-gray-600">时间</th>
                                    <th className="p-2 font-semibold text-gray-600">数据项</th>
                                    <th className="p-2 w-40 font-semibold text-gray-600">标签</th>
                                    {/* 【新增】为“等级”列增加表头，并调整了“标签”列的宽度 */}
                                    <th className="p-2 w-20 font-semibold text-gray-600">等级</th>
                                    <th className="p-2 w-24 font-semibold text-gray-600">根因异常</th>
                                </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200">
                                {paginatedDetailsMetrics.map((metric, index) => (
                                    <tr key={metric.metric_id} className={`relative ${hoveredTagId === metric.metric_id ? 'z-10' : ''}`}>
                                    <td className="p-2 text-gray-700">{(detailsCurrentPage - 1) * detailsPageSize + index + 1}</td>
                                    <td className="p-2 text-gray-700 truncate" title={metric.timestamp}>{metric.timestamp}</td>
                                    <td className="p-2 text-gray-700 truncate" title={metric.data_item}>{metric.data_item}</td>
                                    <td 
                                        className="p-2 text-gray-700 truncate"
                                        onMouseEnter={() => setHoveredTagId(metric.metric_id)}
                                        onMouseLeave={() => setHoveredTagId(null)}
                                    >
                                        {metric.tags}
                                        {hoveredTagId === metric.metric_id && (
                                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-max max-w-sm bg-gray-800 bg-opacity-90 text-white text-xs rounded-md p-3 shadow-lg z-50 pointer-events-none">
                                            <div className="whitespace-pre-wrap break-all">
                                            {metric.tags.split(', ').join('\n')}
                                            </div>
                                            <div className="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-l-8 border-l-transparent border-r-8 border-r-transparent border-t-8 border-t-gray-800 border-opacity-90"></div>
                                        </div>
                                        )}
                                    </td>
                                    {/* 【新增】渲染“等级”列的数据单元格 */}
                                    <td className="p-2 text-gray-700 truncate">{metric.level}</td>
                                    <td className="p-2 text-gray-700 truncate">{metric.is_root_cause}</td>
                                    </tr>
                                ))}
                                </tbody>
                            </table>
                            {/* 【BUG修复】修改此处的条件判断 */}
                            {selectedAlert.details.abnormal_metrics.length > 0 && (
                                <div className="pt-4">
                                    <Pagination
                                        currentPage={detailsCurrentPage}
                                        totalItems={selectedAlert.details.abnormal_metrics.length}
                                        pageSize={detailsPageSize}
                                        onPageChange={setDetailsCurrentPage}
                                        onPageSizeChange={(size) => { setDetailsPageSize(size); setDetailsCurrentPage(1); }}
                                    />
                                </div>
                            )}
                        </div>
                    </div>
                    )}
                </div>
            </div>

            {/* 统计信息侧边面板 */}
            <div className={`fixed top-16 right-0 bottom-0 bg-white shadow-lg transition-transform duration-300 ease-in-out ${isStatsPanelOpen ? 'translate-x-0' : 'translate-x-full'}`} style={{width: '50%'}}>
                <div className="flex flex-col h-full">
                <div className="flex justify-between items-center p-4 border-b">
                    <h3 className="text-lg font-semibold text-gray-800">告警信息统计</h3>
                    <button onClick={() => setIsStatsPanelOpen(false)} className="text-gray-500 hover:text-gray-800 text-2xl">×</button>
                </div>
                <div className="flex-1 flex flex-col p-4 overflow-hidden">
                    <div className="flex-1 overflow-y-auto">
                    <table className="min-w-full text-sm">
                        <thead className="bg-gray-50 sticky top-0">
                            <tr>
                            <th className="p-2 text-left font-semibold text-gray-600 w-1/4">排名</th>
                            <th className="p-2 text-left font-semibold text-gray-600 w-1/2">主机组名称</th>
                            <th className="p-2 text-left font-semibold text-gray-600 w-1/4">告警数</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {paginatedStats.map(item => (
                            <tr key={item.rank}>
                                <td className="p-2"><span className={`${item.rank <= 3 ? 'bg-blue-500' : 'bg-gray-400'} text-white rounded-full w-5 h-5 flex items-center justify-center`}>{item.rank}</span></td>
                                <td className="p-2 text-gray-800">{item.host_group}</td>
                                <td className="p-2 text-red-600 font-semibold">{item.alert_count}</td>
                            </tr>
                            ))}
                        </tbody>
                    </table>
                    </div>
                    {stats.length > 0 && (
                        <div className="pt-4 flex-shrink-0">
                        <Pagination 
                            currentPage={statsCurrentPage}
                            totalItems={stats.length}
                            pageSize={statsPageSize}
                            onPageChange={setStatsCurrentPage}
                            onPageSizeChange={(size) => { setStatsPageSize(size); setStatsCurrentPage(1); }}
                        />
                        </div>
                    )}
                </div>
                </div>
            </div>
            </div>
        );
        };
    //告警页面结束