//故障监控及分析页面开始
    const FaultMonitoringAnalysis = () => {
        // --- 状态管理 ---
        const [healthData, setHealthData] = React.useState(null);
        const [timelineEvents, setTimelineEvents] = React.useState([]);
        const [anomalies, setAnomalies] = React.useState([]);
        const [loading, setLoading] = React.useState(true);
        const [error, setError] = React.useState(null);

        // 控制深度分析侧滑面板的状态
        const [isPanelOpen, setIsPanelOpen] = React.useState(false);
        const [selectedAnomalyId, setSelectedAnomalyId] = React.useState(null);
        
        // 控制列表的过滤条件 ('all', 'active', 'predicted')
        const [filterStatus, setFilterStatus] = React.useState('all');
        
        // --- 数据获取 ---
        const API_BASE_URL = 'http://localhost:5000/api/fault-monitoring'; // 统一的后端地址
        React.useEffect(() => {
            const fetchAllData = async () => {
                setLoading(true);
                setError(null);
                try {

                    // 获取聚合数据
                    const [healthRes, eventsRes, anomaliesRes] = await Promise.all([
                        fetch(`${API_BASE_URL}/global-health`),
                        fetch(`${API_BASE_URL}/timeline-events`),
                        fetch(`${API_BASE_URL}/anomalies`)
                    ]);

                    

                    if (!healthRes.ok || !eventsRes.ok || !anomaliesRes.ok) {
                        throw new Error('一个或多个监控数据文件加载失败，请检查网络或文件路径。');
                    }

                    const health = await healthRes.json();
                    const events = await eventsRes.json();
                    const anomaliesData = await anomaliesRes.json();
                    
                    setHealthData(health);
                    setTimelineEvents(events);
                    setAnomalies(anomaliesData);

                } catch (e) {
                    console.error("获取故障监控数据失败:", e);
                    setError(e.message);
                } finally {
                    setLoading(false);
                }
            };
            fetchAllData();
        }, []);

        // --- 事件处理 ---
        const handleViewDetails = (anomalyId) => {
            setSelectedAnomalyId(anomalyId);
            setIsPanelOpen(true);
        };

        const handleClosePanel = () => {
            setIsPanelOpen(false);
            setTimeout(() => setSelectedAnomalyId(null), 300);
        };
        
        // 在 FaultMonitoringAnalysis 组件内
        const handleFilterChange = (status) => {
            // --- 在这里添加日志 ---
            console.log('Filter status changed to:', status);
            // --------------------
            setFilterStatus(status);
        };

        // --- 渲染逻辑 ---
        if (loading) return <div className="text-center p-10">正在加载AIOps监控数据...</div>;
        if (error) return <div className="p-6 bg-red-50 border border-red-200 rounded-lg text-red-700">{error}</div>;

        return (
            <div className="relative space-y-6 overflow-hidden">
                {/* 区域一: 全局健康度与智能预警区 */}
                <GlobalHealthCards healthData={healthData} onFilterChange={handleFilterChange} />
                
                {/* 区域二: 异常事件关联时间轴 */}
                <EventTimeline events={timelineEvents} />
                
                {/* 区域三: 智能异常聚合列表 */}
                <AnomalyList 
                    allAnomalies={anomalies}
                    filterStatus={filterStatus}
                    onViewDetails={handleViewDetails} 
                    onFilterChange={handleFilterChange}
                />
                
                {/* 区域四: 故障深度分析视图 (侧滑面板) */}
                <DeepDivePanel 
                isOpen={isPanelOpen} 
                onClose={handleClosePanel} 
                anomalyId={selectedAnomalyId}
                apiBaseUrl={API_BASE_URL}  // <-- 新增这一行
            />
            </div>
        );
    };

        const GlobalHealthCards = ({ healthData, onFilterChange }) => {
        if (!healthData) return null;
        
        const HealthScoreCircle = ({ score }) => {
            const getScoreColor = (s) => {
                if (s >= 90) return 'text-green-500';
                if (s >= 70) return 'text-yellow-500';
                return 'text-red-500';
            };
            const radius = 30;
            const circumference = 2 * Math.PI * radius;
            const offset = circumference - (score / 100) * circumference;

            return (
                <div className="relative w-20 h-20">
                    <svg className="w-full h-full" viewBox="0 0 70 70">
                        <circle className="text-gray-200" strokeWidth="8" stroke="currentColor" fill="transparent" r={radius} cx="35" cy="35"/>
                        <circle className={getScoreColor(score)} strokeWidth="8" strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round" stroke="currentColor" fill="transparent" r={radius} cx="35" cy="35" style={{ transform: 'rotate(-90deg)', transformOrigin: '50% 50%' }}/>
                    </svg>
                    <span className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-2xl font-bold ${getScoreColor(score)}`}>{score}</span>
                </div>
            );
        };

        const StatCard = ({ title, value, icon, description, onCardClick }) => (
            <div className={`bg-white p-4 rounded-lg shadow-sm border flex items-center ${onCardClick ? 'cursor-pointer hover:bg-gray-50 transition-colors' : ''}`} onClick={onCardClick}>
                <div className="mr-4">{icon}</div>
                <div>
                    <h4 className="text-sm text-gray-500 font-semibold">{title}</h4>
                    <p className="text-2xl font-bold text-gray-800">{value}</p>
                    {description && <p className="text-xs text-gray-400">{description}</p>}
                </div>
            </div>
        );

        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-white p-4 rounded-lg shadow-sm border flex items-center justify-around">
                    <HealthScoreCircle score={healthData.healthScore} />
                    <div>
                        <h4 className="text-sm text-gray-500 font-semibold">AI健康评分</h4>
                    </div>
                </div>
                <StatCard title="实时异常事件" value={healthData.activeAnomalies} icon={<div className="p-3 bg-red-100 rounded-full"><svg className="w-6 h-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg></div>} onCardClick={() => onFilterChange('active')}/>
                <StatCard title="潜在风险预测" value={healthData.predictedRisks} description="未来6小时内" icon={<div className="p-3 bg-yellow-100 rounded-full"><svg className="w-6 h-6 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg></div>} onCardClick={() => onFilterChange('predicted')}/>
                <StatCard title="平均修复时间 (MTTR)" value={healthData.mttr} icon={<div className="p-3 bg-blue-100 rounded-full"><svg className="w-6 h-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" /></svg></div>}/>
            </div>
        );
    };

        const EventTimeline = ({ events }) => {
        const [hoveredEvent, setHoveredEvent] = React.useState(null);

        const getEventStyle = (type) => {
            const base = "absolute top-1/2 -translate-y-1/2 w-4 h-4 rounded-full border-2 cursor-pointer transition-transform duration-200 hover:scale-150";
            switch(type) {
                case 'anomaly': return `${base} bg-red-500 border-white`;
                case 'log_error': return `${base} bg-yellow-400 border-white`;
                case 'change': return `${base} bg-blue-400 border-white`;
                default: return `${base} bg-gray-400 border-white`;
            }
        };

        return (
            <div className="bg-white p-4 rounded-lg shadow-sm border">
                <h3 className="text-base font-semibold mb-4">异常事件关联时间轴</h3>
                <div className="w-full h-20 bg-gray-50 rounded-md relative flex items-center">
                    <div className="w-full h-0.5 bg-gray-300"></div>
                    {events.map(event => (
                        <div 
                            key={event.id}
                            className="absolute h-full top-0 flex items-center"
                            style={{ left: `${event.position_percent}%` }}
                            onMouseEnter={() => setHoveredEvent(event)}
                            onMouseLeave={() => setHoveredEvent(null)}
                        >
                            <div className={getEventStyle(event.type)}></div>
                            {hoveredEvent && hoveredEvent.id === event.id && (
                                <div className="absolute bottom-full mb-2 w-max max-w-xs bg-gray-800 text-white text-xs rounded-md p-2 shadow-lg z-10 transform -translate-x-1/2 left-1/2">
                                    <p className="font-bold">{event.summary}</p>
                                    <p className="text-gray-300">{event.timestamp}</p>
                                    <div className="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-x-4 border-x-transparent border-t-4 border-t-gray-800"></div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    const AnomalyList = ({ allAnomalies, filterStatus, onViewDetails, onFilterChange }) => {
        const SolutionMatchIcon = ({ status }) => {
            switch(status) {
                case 'high_confidence': 
                    return <span title="高置信度预案匹配" className="inline-block p-1 bg-green-100 rounded-full"><svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path></svg></span>;
                case 'possible_match': 
                    return <span title="可能匹配到预案" className="inline-block p-1 bg-yellow-100 rounded-full"><svg className="w-4 h-4 text-yellow-600" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd"></path></svg></span>;
                case 'no_match': 
                    return <span title="未匹配到预案" className="inline-block p-1 bg-red-100 rounded-full"><svg className="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd"></path></svg></span>;
                default: return null;
            }
        };

        console.log('AnomalyList received props:', { allAnomalies, filterStatus });

        const filteredAnomalies = React.useMemo(() => {
            if (filterStatus === 'all') {
                return allAnomalies;
            }
            return allAnomalies.filter(a => a.status === filterStatus);
        }, [allAnomalies, filterStatus]);

        return (
            <div className="bg-white p-4 rounded-lg shadow-sm border">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-base font-semibold">智能异常聚合列表</h3>
                    {filterStatus !== 'all' && (
                        <div className="flex items-center space-x-2">
                           <span className="text-sm font-semibold px-3 py-1 bg-blue-100 text-blue-700 rounded-full">
                                当前筛选: {filterStatus === 'active' ? '实时异常' : '潜在风险'}
                           </span>
                           <button onClick={() => onFilterChange('all')} className="text-sm text-gray-500 hover:text-gray-800">
                                × 清除筛选
                           </button>
                        </div>
                    )}
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead className="bg-gray-50 text-left">
                            <tr>
                                <th className="p-3 font-semibold text-gray-600">严重性</th>
                                <th className="p-3 font-semibold text-gray-600">AI摘要 / 根因推荐</th>
                                <th className="p-3 font-semibold text-gray-600">影响范围</th>
                                <th className="p-3 font-semibold text-gray-600">持续时间</th>
                                <th className="p-3 font-semibold text-gray-600 text-center">预案匹配</th>
                                <th className="p-3 font-semibold text-gray-600">操作</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {/* --- 核心修复点在这里 --- */}
                            {/* 确保这里使用的是 filteredAnomalies.map 来渲染列表 */}
                            {filteredAnomalies.length === 0 ? (
                                <tr><td colSpan="6" className="text-center p-8 text-gray-500">当前条件下无数据</td></tr>
                            ) : (
                                filteredAnomalies.map(anomaly => (
                                    <tr key={anomaly.id}>
                                        <td className="p-3"><span className={`px-2 py-1 text-xs font-semibold rounded-full ${anomaly.severity === '严重' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>{anomaly.severity}</span></td>
                                        <td className="p-3">
                                            <p className="font-semibold text-gray-800">{anomaly.ai_summary}</p>
                                            <p className="text-xs text-gray-500">根因推荐: {anomaly.root_cause_recommendation}</p>
                                        </td>
                                        <td className="p-3 text-gray-600">{anomaly.scope}</td>
                                        <td className="p-3 text-gray-600">{anomaly.duration}</td>
                                        <td className="p-3 text-center"><SolutionMatchIcon status={anomaly.solution_match_status}/></td>
                                        <td className="p-3 text-blue-600 font-semibold">
                                            <button onClick={() => onViewDetails(anomaly.id)} className="hover:underline">查看详情</button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        );
    };

        const DeepDivePanel = ({ isOpen, onClose, anomalyId, apiBaseUrl }) => { // <-- 关键修改点 1：在这里接收 apiBaseUrl
    const [detail, setDetail] = React.useState(null);
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState(null);
    const [activeTab, setActiveTab] = React.useState('diagnosis');
    const [manualSteps, setManualSteps] = React.useState('');

    React.useEffect(() => {
        // 在 effect 内部，现在可以安全地使用 apiBaseUrl
        if (anomalyId) {
            setLoading(true);
            setError(null);
            setActiveTab('diagnosis');
            setManualSteps('');
            fetch(`${apiBaseUrl}/anomaly-detail/${anomalyId}`) // <-- 现在这里可以正常工作
                .then(res => {
                    if (!res.ok) throw new Error("无法加载异常详情数据。");
                    return res.json();
                })
                .then(data => setDetail(data))
                .catch(err => setError(err.message))
                .finally(() => setLoading(false));
        } else {
            setDetail(null);
        }
    }, [anomalyId, apiBaseUrl]); // <-- 关键修改点 2：这里的依赖项现在是有效的

    const handleExecuteSolution = (solution) => {
        alert(`正在执行预案: ${solution.name}...\n(此为模拟操作)`);
    };
    const handleEnableAutoHealing = (solution) => {
        if (window.confirm(`确定要为 "${solution.name}" 预案开启自动执行吗？\n下次发生同类异常时，系统将自动触发此预案。`)) {
            alert("已成功开启自动执行！(此为模拟操作)");
        }
    };
    const handleCreateSolution = () => {
        if (!manualSteps.trim()) {
            alert("请输入手动操作步骤！");
            return;
        }
        alert(`已将您的手动操作转化为新的预案，请在工作流或预案库中查看和完善。\n\n内容:\n${manualSteps}\n(此为模拟操作)`);
    };

    const renderTabContent = () => {
        if (loading) return <div className="p-6 text-center">加载详情中...</div>;
        if (error) return <div className="p-6 bg-red-50 text-red-700">{error}</div>;
        if (!detail) return <div className="p-6 text-center text-gray-400">请先从列表中选择一个异常事件</div>;

        switch(activeTab) {
            case 'diagnosis': return (
                <div className="p-6 space-y-4">
                    <h4 className="font-bold text-lg">AI诊断与决策</h4>
                    <blockquote className="border-l-4 border-blue-500 bg-blue-50 p-4 text-gray-800">
                        <p className="font-semibold mb-2">LLM诊断摘要:</p>
                        <p className="text-sm">{detail.diagnosis.llm_summary}</p>
                    </blockquote>
                    <div>
                        <p className="font-semibold mb-2">因果关系图:</p>
                        <div className="p-4 border rounded-lg bg-gray-900 text-white text-sm font-mono flex items-center justify-center h-48">
                            <div>{detail.diagnosis.causal_graph} (图表占位符)</div>
                        </div>
                    </div>
                </div>
            );
            case 'metrics': return (
                <div className="p-6 h-full flex flex-col">
                    <h4 className="font-bold text-lg mb-4">关联指标</h4>
                    <div className="border rounded-lg flex-grow">
                        <AssetMonitoringReport srcUrl={detail.correlated_metrics_url} />
                    </div>
                </div>
            );
            case 'logs': return (
                <div className="p-6 space-y-4">
                    <h4 className="font-bold text-lg">关联日志</h4>
                    <pre className="p-4 border rounded-lg bg-gray-900 text-white text-xs font-mono h-96 overflow-auto">{detail.correlated_logs}</pre>
                </div>
            );
            case 'execution': return (
                <div className="p-6 space-y-6">
                    <h4 className="font-bold text-lg">预案执行中心</h4>
                    {detail.solution ? (
                        <div className="space-y-4">
                            <div>
                                <p className="text-sm text-gray-500">已匹配到预案</p>
                                <p className="text-xl font-bold text-blue-600">{detail.solution.name}</p>
                            </div>
                            <div className="bg-gray-100 p-4 rounded-lg border text-sm space-y-1">
                                <p><span className="font-semibold">描述:</span> {detail.solution.description}</p>
                                <p><span className="font-semibold">历史成功率:</span> <span className="text-green-600 font-bold">{detail.solution.success_rate}</span></p>
                            </div>
                            <div>
                                <p className="font-semibold text-sm mb-2">执行预览:</p>
                                <pre className="p-3 border bg-gray-50 rounded-md text-xs font-mono">{detail.solution.steps}</pre>
                            </div>
                            <div className="flex items-center space-x-3 pt-4 border-t">
                                <button onClick={() => handleExecuteSolution(detail.solution)} className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-md">▶️ 一键执行</button>
                                <button onClick={() => handleEnableAutoHealing(detail.solution)} className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-md">⚙️ 设为自动执行</button>
                            </div>
                        </div>
                    ) : (
                        <div>
                            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-800">
                                <p><span className="font-bold">未在知识库中找到可用预案。</span><br/>请根据诊断信息手动处理，并将操作步骤记录在下方，以便将其转化为新的预案。</p>
                            </div>
                            <div className="mt-4">
                                <label className="font-semibold text-sm mb-2 block">手动操作记录:</label>
                                <textarea 
                                    className="w-full border rounded-md p-2 font-mono text-sm h-40 focus:ring-2 focus:ring-blue-400" 
                                    placeholder="例如:
1. ssh admin@10.0.0.5
2. sudo systemctl restart nginx
3. exit"
                                    value={manualSteps}
                                    onChange={(e) => setManualSteps(e.target.value)}
                                ></textarea>
                            </div>
                            <div className="mt-4">
                                <button onClick={handleCreateSolution} className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-md">[+] 转化为新预案</button>
                            </div>
                        </div>
                    )}
                </div>
            );
            default: return null;
        }
    };

    return (
        <div className={`fixed top-16 right-0 h-[calc(100%-4rem)] bg-white shadow-2xl border-l transition-transform duration-300 ease-in-out z-40 ${isOpen ? 'translate-x-0' : 'translate-x-full'}`} style={{ width: '50%' }}>
            <div className="flex flex-col h-full">
                <div className="flex justify-between items-center p-4 border-b flex-shrink-0">
                    <h3 className="text-lg font-semibold text-gray-800">故障深度分析</h3>
                    <button onClick={onClose} className="text-gray-500 hover:text-gray-800 text-3xl font-light">×</button>
                </div>
                <div className="border-b border-gray-200 flex-shrink-0">
                    <nav className="flex space-x-4 px-4">
                        <button onClick={() => setActiveTab('diagnosis')} className={`py-3 px-2 text-sm font-medium border-b-2 ${activeTab === 'diagnosis' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}>AI诊断与决策</button>
                        <button onClick={() => setActiveTab('metrics')} className={`py-3 px-2 text-sm font-medium border-b-2 ${activeTab === 'metrics' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}>关联指标</button>
                        <button onClick={() => setActiveTab('logs')} className={`py-3 px-2 text-sm font-medium border-b-2 ${activeTab === 'logs' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}>关联日志</button>
                        <button onClick={() => setActiveTab('execution')} className={`py-3 px-2 text-sm font-medium border-b-2 ${activeTab === 'execution' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}>预案执行中心</button>
                    </nav>
                </div>
                <div className="flex-grow overflow-y-auto">
                    {renderTabContent()}
                </div>
            </div>
        </div>
    );
};

    //故障监控及分析组件结束