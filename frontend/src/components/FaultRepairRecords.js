//故障修复记录组件开始
    const CreateWorkflowModal = ({ isOpen, onClose, commands }) => {
        if (!isOpen) return null;
        const [workflowName, setWorkflowName] = React.useState('新自动化工作流');
        return (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
                <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl">
                    <div className="p-5 border-b"><h3 className="text-lg font-semibold">将手动操作转化为自动化工作流</h3></div>
                    <div className="p-6 space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">工作流名称:</label>
                            <input value={workflowName} onChange={(e) => setWorkflowName(e.target.value)} className="mt-1 block w-full border rounded-md p-2" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">执行步骤 (已自动填充):</label>
                            <textarea readOnly value={commands} rows="8" className="mt-1 block w-full border bg-gray-100 rounded-md p-2 font-mono text-sm"></textarea>
                        </div>
                    </div>
                    <div className="p-4 border-t flex justify-end space-x-2">
                        <button onClick={onClose} className="px-4 py-2 border rounded-md">取消</button>
                        <button onClick={() => { alert('工作流保存成功 (模拟)'); onClose(); }} className="px-4 py-2 bg-blue-600 text-white rounded-md">保存工作流</button>
                    </div>
                </div>
            </div>
        );
    };

    const FaultDetailView = ({ recordId, onBack }) => {
        const [detail, setDetail] = React.useState(null);
        const [loading, setLoading] = React.useState(true);
        const [isWorkflowModalOpen, setWorkflowModalOpen] = React.useState(false);

        const API_BASE_URL = 'http://localhost:5000/api/fault-repairs';

        React.useEffect(() => {
            const fetchDetail = async () => {
                setLoading(true);
                try {
                    const response = await fetch(`${API_BASE_URL}/records/${recordId}`);
                    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                    const data = await response.json();
                    setDetail(data);
                } catch (error) {
                    console.error(`获取故障详情 ${recordId} 失败:`, error);
                    // 不再使用alert，而是让界面渲染错误信息
                    setDetail(null);
                } finally {
                    setLoading(false);
                }
            };
            fetchDetail();
        }, [recordId]);

        if (loading) return <div className="text-center p-10">正在加载故障复盘信息...</div>;
        
        // --- 修复点 1: 增加加载失败时的返回功能 ---
        if (!detail) {
            return (
                <div className="text-center p-10 bg-white rounded-lg shadow-md">
                    <h3 className="text-xl font-bold text-red-600">加载故障详情失败</h3>
                    <p className="text-gray-600 my-4">无法获取到ID为 "{recordId}" 的复盘数据，请确认对应的详情文件是否存在且格式正确。</p>
                    <button onClick={onBack} className="text-blue-600 hover:underline text-sm font-semibold">
                        ← 返回记录列表
                    </button>
                </div>
            );
        }

        const KnowledgeTransformation = () => {
            // ... 此处内部逻辑无变化
            if (detail.type === '手动' && detail.result === '成功') {
                return (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
                        <h4 className="font-semibold text-blue-800">将成功经验转化为能力</h4>
                        <p className="text-sm text-blue-700 my-2">这次成功的手动修复可以被固化为自动化预案，以应对未来类似的故障。</p>
                        <button onClick={() => setWorkflowModalOpen(true)} className="bg-blue-600 text-white font-semibold py-2 px-4 rounded-md hover:bg-blue-700 text-sm">
                            [+] 转化为自动化工作流
                        </button>
                    </div>
                );
            }
            if (detail.type === '自动' && detail.result === '失败') {
                return (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                        <h4 className="font-semibold text-yellow-800">从此“失败”中学习</h4>
                        <p className="text-sm text-yellow-700 my-2">该自动化工作流执行失败。建议分析执行日志，并优化工作流或创建新的修复方案。</p>
                    </div>
                );
            }
            return (
                <div className="text-center text-sm text-gray-500">
                    <p>当前场景无需额外操作。自动化修复成功，工作流表现稳定。</p>
                </div>
            );
        };

        return (
            <div className="space-y-6">
                <CreateWorkflowModal isOpen={isWorkflowModalOpen} onClose={() => setWorkflowModalOpen(false)} commands={detail.executionDetails} />
                {/* Header */}
                <div>
                    <button onClick={onBack} className="text-blue-600 hover:underline text-sm mb-2">← 返回记录列表</button>
                    <h2 className="text-2xl font-bold text-gray-800">{detail.summary}</h2>
                </div>

                {/* Module 1: Event Timeline & LLM Summary */}
                <div className="bg-white p-6 rounded-lg shadow-md">
                    <h3 className="text-lg font-semibold mb-4">事件摘要与时间轴</h3>
                    <blockquote className="border-l-4 border-blue-500 bg-blue-50 p-4 my-4">
                        <p className="text-gray-700 italic">🤖 <span className="font-semibold">AIOps分析:</span> {detail.llmAnalysis}</p>
                    </blockquote>
                    <div className="flex justify-between space-x-2 text-center">
                        {detail.timeline.map((item, index) => (
                            <div key={index} className="flex-1">
                                <div className="font-semibold text-gray-800">{item.status}</div>
                                <div className="text-sm text-gray-500">{item.time}</div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Module 2 & 3 in a Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Fault Context */}
                    <div className="bg-white p-6 rounded-lg shadow-md space-y-4">
                        <h3 className="text-lg font-semibold">故障上下文</h3>
                        <div>
                            <h4 className="font-medium text-gray-600 mb-1">关联告警</h4>
                            <pre className="bg-gray-100 p-3 rounded-md text-sm text-gray-800 whitespace-pre-wrap">{detail.context.alertDetails}</pre>
                        </div>
                        <div>
                            <h4 className="font-medium text-gray-600 mb-1">异常日志</h4>
                            <pre className="bg-gray-100 p-3 rounded-md text-sm text-red-600 whitespace-pre-wrap font-mono">{detail.context.relatedLogs}</pre>
                        </div>
                        <div>
                            <h4 className="font-medium text-gray-600 mb-1">相关性能指标 (故障时段)</h4>
                            <div className="h-48 bg-gray-50 rounded-md flex items-center justify-center">
                                <iframe src={detail.context.performanceChartUrl} title="性能图表" className="w-full h-full border-none rounded-md"></iframe>
                            </div>
                        </div>
                    </div>

                    {/* Repair Execution */}
                    <div className="bg-white p-6 rounded-lg shadow-md space-y-4">
                        <h3 className="text-lg font-semibold">修复过程详解</h3>
                        <div className="bg-gray-800 text-white font-mono text-sm p-4 rounded-lg h-full overflow-y-auto" style={{minHeight: '300px'}}>
                            <pre className="whitespace-pre-wrap">{detail.executionDetails}</pre>
                        </div>
                    </div>
                </div>

                {/* Module 4: Knowledge Transformation */}
                <div className="bg-white p-6 rounded-lg shadow-md">
                    <h3 className="text-lg font-semibold mb-4">智能复盘与优化</h3>
                    <KnowledgeTransformation />
                </div>
            </div>
        );
    };

    const FaultRepairRecords = () => {
        const [view, setView] = React.useState({ page: 'list', param: null });
        const [records, setRecords] = React.useState([]);
        const [loading, setLoading] = React.useState(true);
        // TODO: AIOps 指标应从后端计算获取
        const [metrics] = React.useState({ mttr: '18.2分钟', automationRate: '68%' });

        const API_BASE_URL = 'http://localhost:5000/api/fault-repairs';

        const fetchRecords = React.useCallback(async () => {
            setLoading(true);
            try {
                const response = await fetch(`${API_BASE_URL}/records`);
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const data = await response.json();
                setRecords(data);
            } catch (error) {
                console.error("获取修复记录失败:", error);
                alert("获取修复记录失败，请检查后端服务是否正常以及网络连接。");
                setRecords([]);
            } finally {
                setLoading(false);
            }
        }, []);

        React.useEffect(() => {
            if(view.page === 'list') {
                fetchRecords();
            }
        }, [view.page, fetchRecords]);
        
        const handleNavigateToDetail = (recordId) => setView({ page: 'detail', param: recordId });
        const handleNavigateToList = () => setView({ page: 'list', param: null });

        const getTypeClass = (type) => type === '自动' ? 'bg-blue-100 text-blue-800' : 'bg-yellow-100 text-yellow-800';
        const getResultClass = (result) => result === '成功' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';

        const renderListView = () => (
            <div className="bg-white p-6 rounded-lg shadow-md">
                {/* Top Action & Metrics Bar */}
                <div className="flex justify-between items-start mb-5">
                    <div className="flex items-center space-x-4">
                        {/* AIOps 指标卡片 */}
                        <div className="p-3 bg-gray-50 rounded-lg border">
                            <div className="text-sm text-gray-500">平均修复时长 (MTTR)</div>
                            <div className="text-2xl font-bold text-gray-800">{metrics.mttr}</div>
                        </div>
                        <div className="p-3 bg-gray-50 rounded-lg border">
                            <div className="text-sm text-gray-500">自动化修复率</div>
                            <div className="text-2xl font-bold text-blue-600">{metrics.automationRate}</div>
                        </div>
                    </div>
                    <button onClick={fetchRecords} className="bg-white border border-gray-300 text-gray-700 font-semibold py-2 px-4 rounded-md hover:bg-gray-50 text-sm flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h5M20 20v-5h-5M4 4l5 5M20 20l-5-5"></path></svg>
                        刷新
                    </button>
                </div>
                {/* Table */}
                <div className="overflow-x-auto">
                    <table className="min-w-full text-sm">
                        <thead className="bg-gray-50"><tr>
                            <th className="p-3 text-left font-semibold text-gray-600">关联告警</th>
                            <th className="p-3 text-left font-semibold text-gray-600">故障资产</th>
                            <th className="p-3 text-left font-semibold text-gray-600">修复工作流</th>
                            <th className="p-3 text-left font-semibold text-gray-600">触发类型</th>
                            <th className="p-3 text-left font-semibold text-gray-600">结果</th>
                            <th className="p-3 text-left font-semibold text-gray-600">修复耗时</th>
                            <th className="p-3 text-left font-semibold text-gray-600">修复时间</th>
                            <th className="p-3 text-left font-semibold text-gray-600">操作</th>
                        </tr></thead>
                        <tbody>
                            {loading ? (
                                <tr><td colSpan="8" className="p-10 text-center text-gray-500">加载中...</td></tr>
                            ) : (
                                records.map(r => (
                                    <tr key={r.id} className="border-b hover:bg-gray-50">
                                        <td className="p-3 font-semibold text-gray-800">{r.alertSummary}</td>
                                        <td className="p-3 text-gray-600">{r.asset}</td>
                                        <td className="p-3 text-gray-600">{r.workflow}</td>
                                        <td className="p-3"><span className={`px-2 py-1 text-xs font-semibold rounded-full ${getTypeClass(r.type)}`}>{r.type}</span></td>
                                        <td className="p-3"><span className={`px-2 py-1 text-xs font-semibold rounded-full ${getResultClass(r.result)}`}>{r.result}</span></td>
                                        <td className="p-3 text-gray-600">{r.duration}</td>
                                        <td className="p-3 text-gray-600">{r.timestamp}</td>
                                        <td className="p-3">
                                            <a href="#" onClick={(e) => {e.preventDefault(); handleNavigateToDetail(r.id)}} className="text-blue-600 hover:underline">查看详情</a>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        );
        
        return view.page === 'list' ? renderListView() : <FaultDetailView recordId={view.param} onBack={handleNavigateToList} />;
    };
    //故障修复记录组件结束