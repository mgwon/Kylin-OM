//CVEs组件
    const CVEsManagement = ({ onAddRepairRecord }) => {
    
        const api = {
            fetchCveList: async () => {
                const response = await fetch('http://localhost:5000/api/vulnerability/cves');
                if (!response.ok) throw new Error(`网络响应错误: ${response.statusText}`);
                return response.json(); 
            },
            fetchCveDetail: async (cveId) => {
                const response = await fetch(`http://localhost:5000/api/vulnerability/cves/${cveId}`);
                if (!response.ok) throw new Error(`无法找到 ${cveId} 的详情`);
                return response.json();
            },
            // 创建任务的逻辑可以复用 VulnerabilityHostList.js 中的 handleSubmitTask
            // 或者统一抽离成一个公共函数
            createTask: async (taskData) => {
                const response = await fetch('http://localhost:5000/api/vulnerability/tasks', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(taskData),
                });
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `创建任务失败: ${response.statusText}`);
                }
                return response.json(); // 返回后端创建的记录
            },
        };

        const [view, setView] = React.useState({ page: 'list', param: null }); 
        const [cveList, setCveList] = React.useState([]);
        const [isLoading, setIsLoading] = React.useState(true);
        const [isRefreshing, setIsRefreshing] = React.useState(false);

        React.useEffect(() => {
            const loadInitialData = async () => {
                setIsLoading(true);
                try {
                    const data = await api.fetchCveList();
                    setCveList(data);
                } catch (error) {
                    console.error("获取CVE初始列表失败:", error);
                    alert(`获取CVE列表失败: ${error.message}`);
                } finally {
                    setIsLoading(false);
                }
            };
            loadInitialData();
        }, []);
        
        const handleNavigateToDetail = (cveId) => {
            setView({ page: 'detail', param: cveId });
        };
        
        const handleNavigateToList = () => {
            setView({ page: 'list', param: null });
        };

        const handleCreateTask = async (taskInfo) => { // 1. 改为 async 函数
            const { taskName, taskDescription, cvesToRepair } = taskInfo;
            const hostCount = cvesToRepair.reduce((acc, cve) => acc + (cve.affected_hosts?.length || 0), 0);
            
            // 2. 准备要发送到后端的数据
            const taskPayload = {
            name: taskName,
            description: taskDescription,
            hostCount: hostCount, // 后端会根据 host_ids 重新计算，这里可以不传
            type: 'cve修复',
            creationTime: new Date().toLocaleString('zh-CN', { hour12: false }),
            cve_ids: cvesToRepair.map(c => c.id),
            // 假设 cvesToRepair 里的数据结构符合后端 affected_hosts 的需要
            affected_hosts: cvesToRepair.map(cve => ({ 
                cve_id: cve.id, 
                hosts: cve.affected_hosts?.map(h => ({ name: h.hostname })) || []
            })),
            };

            try {
                // 3. 调用 API 将任务数据发送到后端
                const newRecord = await api.createTask(taskPayload);

                // 4. 使用后端返回的数据更新修复记录列表的UI
                if (onAddRepairRecord) {
                    onAddRepairRecord(newRecord);
                }
                alert(`任务 "${taskName}" 已成功创建并记录到后端！`);
                handleNavigateToList(); // 返回列表页
            } catch (error) {
                console.error("创建修复任务失败:", error);
                alert(`创建失败: ${error.message}`);
            }
        };

        const handleExecuteRepair = async (taskInfo) => { // 1. 改为 async 函数
            const { taskName, taskDescription, cvesToRepair } = taskInfo;
            const idsToRepair = cvesToRepair.map(cve => cve.id);
            
            // 2. 准备数据，与 handleCreateTask 类似
            const taskPayload = {
                name: taskName,
                description: taskDescription,
                type: 'cve修复',
                creationTime: new Date().toLocaleString('zh-CN', { hour12: false }),
                cve_ids: idsToRepair,
                affected_hosts: cvesToRepair.map(cve => ({ 
                    cve_id: cve.id, 
                    hosts: cve.affected_hosts?.map(h => ({ name: h.hostname })) || []
                })),
            };

            try {
                // 3. 调用 API 将任务数据发送到后端
                const newRecord = await api.createTask(taskPayload);

                // 4. 后端记录成功后，执行前端的模拟操作
                if (onAddRepairRecord) {
                    onAddRepairRecord(newRecord);
                }

                // 5. 更新当前CVE列表的UI状态为“已修复”
                setCveList(currentCves =>
                    currentCves.map(cve =>
                        idsToRepair.includes(cve.id) ? { ...cve, status: '已修复' } : cve
                    )
                );
                alert(`任务 "${taskName}" 已成功记录到后端，并已在界面上标记为“已修复”。`);

            } catch (error) {
                console.error("执行并创建修复任务失败:", error);
                alert(`操作失败: ${error.message}`);
            }
        };
        const handleExecuteRemoval = (taskInfo) => {
            const { taskName, taskDescription, cvesToRemove } = taskInfo;
            const hostCount = cvesToRemove.reduce((acc, cve) => acc + (cve.affected_hosts?.length || 0), 0);
            
            const newRecord = {
            id: `task-${Date.now()}`,
            name: taskName,
            description: taskDescription,
            hostCount: hostCount,
            type: '热补丁移除', // 新的任务类型
            status: { success: 0, fail: 0, running: 0, unknown: hostCount },
            creationTime: new Date().toLocaleString('zh-CN', { hour12: false }),
            cve_ids: cvesToRemove.map(c => c.id),
            };

            if (onAddRepairRecord) {
            onAddRepairRecord(newRecord);
            }
            
            const idsToRemove = cvesToRemove.map(cve => cve.id)
            
            setCveList(currentCves =>
            currentCves.map(cve =>
                idsToRemove.includes(cve.id) ? { ...cve, status: '未修复' } : cve // 状态改回“未修复”
            )
            );
            alert(`已为 ${idsToRemove.join(', ')} 创建热补丁移除任务，漏洞状态已标记为“未修复”（模拟）。`);
            handleNavigateToList();
        };

        const handleRefresh = async () => {
            setIsRefreshing(true);
            try {
                const newCveData = await api.fetchCveList();
                setCveList(newCveData);
                alert("CVE列表刷新成功！");
            } catch (error) {
                console.error("刷新CVE列表失败:", error);
                alert(`刷新失败: ${error.message}`);
            } finally {
                setIsRefreshing(false);
            }
        };

        const RepairTaskModal = ({ onClose, cvesToRepair, onCreateTask, onExecuteTask, _taskType, _taskName, _taskDescription, _executeButtonText }) => {
            const cveCount = cvesToRepair.length; 
            const cveIds = cvesToRepair.map(cve => cve.id).join('、 ');
            
            const [taskName, setTaskName] = React.useState(_taskName || `修复${cveCount}个CVE`);
            const [taskDescription, setTaskDescription] = React.useState(_taskDescription || `修复以下CVE: ${cveIds.length > 50 ? cveIds.substring(0,50)+'...' : cveIds}`);
            
            const isFormValid = taskName.trim() !== '' && taskDescription.trim() !== '';

            const handleSubmit = (isExecution) => {
                if (!isFormValid) return;
                const taskInfo = { taskName, taskDescription, cvesToRepair: cvesToRepair, cvesToRemove: cvesToRepair };
                if (isExecution) {
                    onExecuteTask(taskInfo);
                } else {
                    onCreateTask(taskInfo);
                }
                onClose();
            };

            return ( 
                <div className="fixed inset-0 bg-black bg-opacity-25 flex justify-end z-40" onClick={onClose}> 
                <div className="bg-white shadow-xl h-full w-full max-w-2xl flex flex-col" onClick={e => e.stopPropagation()}> 
                    <div className="flex justify-between items-center p-4 border-b">
                    <h2 className="text-lg font-semibold text-gray-900">{_taskType ? "生成" + _taskType + "任务" : "生成修复任务"}</h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-700 text-3xl font-light">×</button>
                    </div> 
                    {/* --- 这是之前缺失的内容 --- */}
                    <div className="p-6 flex-grow overflow-y-auto space-y-6 bg-gray-50">
                    <div className="grid grid-cols-3 items-center">
                        <label className="text-sm text-gray-600 col-span-1">任务类型：</label>
                        <p className="text-sm text-gray-800 col-span-2">{_taskType || 'cve修复'}</p>
                    </div>
                    <div className="grid grid-cols-3 items-start">
                        <label className="text-sm text-gray-600 pt-2 col-span-1"><span className="text-red-500 mr-1">*</span>任务名称：</label>
                        <input type="text" value={taskName} onChange={e => setTaskName(e.target.value)} className="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm col-span-2" />
                    </div>
                    <div className="grid grid-cols-3 items-start">
                        <label className="text-sm text-gray-600 pt-2 col-span-1"><span className="text-red-500 mr-1">*</span>任务描述：</label>
                        <textarea rows="3" value={taskDescription} onChange={e => setTaskDescription(e.target.value)} className="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm col-span-2"></textarea>
                    </div>
                    <div className="border rounded-md bg-white flex flex-col" style={{minHeight: '200px'}}>
                        <div className="flex-shrink-0 border-b">
                            <table className="w-full text-sm">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="p-2 w-16 font-medium text-gray-600 text-left"></th>
                                        <th className="p-2 font-medium text-gray-600 text-left">CVE_ID</th>
                                        <th className="p-2 font-medium text-gray-600 text-left">主机数</th>
                                    </tr>
                                </thead>
                            </table>
                        </div>
                        <div className="overflow-y-auto">
                            <table className="w-full text-sm text-left">
                                <tbody className="text-gray-700">
                                    {(cvesToRepair || []).map(cve => (
                                        <tr key={cve.id} className="border-t">
                                            <td className="p-2 w-16 text-center text-gray-500 font-mono">[+]</td>
                                            <td className="p-2">{cve.id}</td>
                                            <td className="p-2">{cve.affected_hosts?.length || cve.hosts || 0}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    </div>
                    {/* --- 缺失内容结束 --- */}
                    <div className="flex justify-end items-center p-4 border-t bg-white space-x-3">
                    <button onClick={onClose} className="px-4 py-1.5 border rounded-md text-sm hover:bg-gray-100 font-semibold text-gray-800">取消</button>
                    {_taskType !== '热补丁移除' && (
                        <button onClick={() => handleSubmit(false)} disabled={!isFormValid} className={`px-4 py-1.5 rounded-md text-sm font-semibold text-white transition-colors ${isFormValid ? 'bg-blue-500 hover:bg-blue-600' : 'bg-gray-300 cursor-not-allowed'}`}>创建</button>
                    )}
                    <button onClick={() => handleSubmit(true)} disabled={!isFormValid} className={`px-4 py-1.5 rounded-md text-sm font-semibold text-white transition-colors ${isFormValid ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-300 cursor-not-allowed'}`}>{_executeButtonText || '立即执行'}</button>
                    </div>
                </div>
                </div>
            );
        };
            const RemovalTaskModal = ({ onClose, cvesToRemove, onExecuteTask }) => {
            const cveCount = cvesToRemove.length;
            const cveIds = cvesToRemove.map(cve => cve.id).join('、');
            const [taskName, setTaskName] = React.useState('热补丁移除任务');
            const [taskDescription, setTaskDescription] = React.useState(`移除以下 ${cveCount} 个 CVE: ${cveIds}`);

            const isFormValid = taskName.trim() !== '' && taskDescription.trim() !== '';

            const handleSubmit = (isExecution) => {
                if (!isFormValid) return;
                const taskInfo = { taskName, taskDescription, cvesToRemove };
                if (isExecution) {
                    onExecuteTask(taskInfo);
                } else {
                    alert('“创建”功能模拟：任务已创建，请在修复记录中查看。');
                    onExecuteTask(taskInfo); // Simplified: create also executes for this demo
                }
                onClose();
            };

            return (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
                <div className="bg-white rounded-lg shadow-xl w-full max-w-3xl">
                    <div className="flex justify-between items-center p-4 border-b">
                        <h2 className="text-lg font-semibold text-gray-900">热补丁移除任务</h2>
                        <button onClick={onClose} className="text-gray-400 hover:text-gray-700 text-3xl font-light">×</button>
                    </div>
                    <div className="p-6 space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-4 items-center">
                            <label className="text-sm font-medium text-gray-700 md:text-right md:pr-4">任务类型:</label>
                            <p className="col-span-3 text-sm p-2 bg-gray-100 rounded mt-1 md:mt-0">热补丁移除</p>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-4 items-start">
                            <label htmlFor="rem-task-name" className="text-sm font-medium text-gray-700 md:text-right md:pr-4 pt-2"><span className="text-red-500 mr-1">*</span>任务名称:</label>
                            <input id="rem-task-name" type="text" value={taskName} onChange={e => setTaskName(e.target.value)} className="col-span-3 w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm mt-1 md:mt-0" />
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-4 items-start">
                            <label htmlFor="rem-task-desc" className="text-sm font-medium text-gray-700 md:text-right md:pr-4 pt-2"><span className="text-red-500 mr-1">*</span>任务描述:</label>
                            <textarea id="rem-task-desc" rows="3" value={taskDescription} onChange={e => setTaskDescription(e.target.value)} className="col-span-3 w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm mt-1 md:mt-0"></textarea>
                        </div>
                        <div className="border rounded-md bg-white">
                            <table className="w-full text-sm">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="p-2 font-medium text-gray-600 text-left">CVE_ID</th>
                                        <th className="p-2 font-medium text-gray-600 text-left">主机</th>
                                        <th className="p-2 font-medium text-gray-600 text-left">热补丁修复</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {(cvesToRemove || []).map(cve => (
                                        <tr key={cve.id} className="border-t">
                                            <td className="p-2">{cve.id}</td>
                                            <td className="p-2">{cve.hosts || 'N/A'}</td>
                                            <td className="p-2 text-green-600">是</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div className="flex justify-end items-center p-4 border-t bg-white space-x-3">
                        <button onClick={onClose} className="px-4 py-1.5 border rounded-md text-sm hover:bg-gray-100 font-semibold text-gray-800">取消</button>
                        <button onClick={() => handleSubmit(false)} disabled={!isFormValid} className={`px-4 py-1.5 rounded-md text-sm font-semibold text-white transition-colors ${isFormValid ? 'bg-blue-500 hover:bg-blue-600' : 'bg-gray-300 cursor-not-allowed'}`}>创建</button>
                        <button onClick={() => handleSubmit(true)} disabled={!isFormValid} className={`px-4 py-1.5 rounded-md text-sm font-semibold text-white transition-colors ${isFormValid ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-300 cursor-not-allowed'}`}>立即执行</button>
                    </div>
                </div>
            </div>
        );
    };
        const CveListPage = ({ onCveClick, allCves, onRefresh, isRefreshing, onCreateTask, onExecuteTask, onExecuteRemovalTask}) => { 
            const [selectedIds, setSelectedIds] = React.useState(new Set());
            const [searchQuery, setSearchQuery] = React.useState(''); 
            const [isRepairModalOpen, setIsRepairModalOpen] = React.useState(false);
            const [isRemovalModalOpen, setIsRemovalModalOpen] = React.useState(false);
            const [statusFilter, setStatusFilter] = React.useState('未修复');
            const filteredData = React.useMemo(() => (allCves || []).filter(cve => cve.status === statusFilter && (cve.id.toLowerCase().includes(searchQuery.toLowerCase().trim()) || cve.package.toLowerCase().includes(searchQuery.toLowerCase().trim()))), [searchQuery, allCves, statusFilter]);
            const getSeverityClass = (s) => ({'低风险':'bg-blue-100 text-blue-800','中风险':'bg-yellow-100 text-yellow-800','高风险':'bg-red-100 text-red-800'}[s] || 'bg-gray-100');
            const cvesForModal = React.useMemo(() => {
            const cvesToProcess = selectedIds.size > 0 ? (allCves || []).filter(cve => selectedIds.has(cve.id)) : filteredData;
                return cvesToProcess.map(cve => ({ id: cve.id, affected_hosts: [{hostname: `host-${cve.hosts}`}], hosts: cve.hosts }));
            }, [selectedIds, filteredData, allCves]);
            const handleTaskButtonClick = () => {
                if (statusFilter === '未修复') {
                    setIsRepairModalOpen(true);
                } else {
                    setIsRemovalModalOpen(true);
                }
            };

            return ( <div className="bg-white border border-gray-200 rounded-md shadow-sm flex flex-col h-full">
            <div className="px-6 py-4 border-b">
                <div className="flex justify-between items-center mb-4">
                <div className="flex items-center"> 
                    <button onClick={() => setStatusFilter('未修复')} className={`px-3 py-1.5 rounded-md text-sm ${statusFilter === '未修复' ? 'bg-blue-500 text-white' : 'border hover:bg-gray-50'}`}>未修复
                    </button> <button onClick={() => setStatusFilter('已修复')} 
                        className={`ml-2 px-3 py-1.5 rounded-md text-sm ${statusFilter === '已修复' ? 'bg-blue-500 text-white' : 'border hover:bg-gray-50'}`}>已修复</button>
                        <div className="relative ml-4"> <input type="text" placeholder="按cve_id或package搜索" className="border rounded-md py-2 pl-8 pr-4 text-sm w-60" value={searchQuery} onChange={e => setSearchQuery(e.target.value)} />
                        <svg className="w-4 h-4 text-gray-400 absolute left-2.5 top-1/2 -translate-y-1/2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                            </div> 
                            </div>
                            <div className="flex items-center space-x-2"> 
                                <button onClick={handleTaskButtonClick} className="px-3 py-1.5 bg-blue-500 text-white rounded-md text-sm hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed" disabled={filteredData.length === 0}>
                                {statusFilter === '未修复' ? '生成修复任务' : '热补丁移除任务'}
                                </button> 
                                <button onClick={onRefresh} disabled={isRefreshing} className="px-3 py-1.5 border rounded-md text-sm hover:bg-gray-50 disabled:bg-gray-200 disabled:cursor-not-allowed"> 
                                    {isRefreshing ? '刷新中...' : '刷新'}
                                    </button>
                                    </div> 
                                    </div>
                                    <div className="flex items-center space-x-2"> <span className="inline-flex items-center bg-blue-100 text-blue-800 text-sm font-medium px-2.5 py-1 rounded"> 已选择 {selectedIds.size} 项 </span> <button onClick={() => { setSearchQuery(''); setSelectedIds(new Set()); }} className="px-3 py-1.5 border rounded-md text-sm hover:bg-gray-50">重置条件
                                        </button> 
                                        </div> 
                                        </div> 
                                        <div className="overflow-y-auto flex-grow"> <table className="w-full text-sm text-left text-gray-600"> <thead className="text-xs text-gray-700 bg-gray-50 sticky top-0 shadow-sm"> <tr> <th className="p-4 w-12"><input type="checkbox" onChange={(e) => setSelectedIds(e.target.checked ? new Set(filteredData.map(c => c.id)) : new Set())} checked={filteredData.length > 0 && selectedIds.size === filteredData.length} className="rounded border-gray-300"/></th> <th className="px-4 py-3">CVE_ID</th> <th className="px-4 py-3">发布时间</th> <th className="px-4 py-3">软件包</th> <th className="px-4 py-3">严重性</th> <th className="px-4 py-3">CVSS 分数</th> <th className="px-4 py-3">主机</th> </tr> </thead> <tbody> {filteredData.length === 0 ? ( <tr><td colSpan="7" className="text-center p-8 text-gray-500">没有数据</td></tr> ) : (filteredData.map(cve => ( <tr key={cve.id} className="bg-white border-b hover:bg-gray-50"> <td className="p-4"><input type="checkbox" onChange={() => { const newIds = new Set(selectedIds); newIds.has(cve.id) ? newIds.delete(cve.id) : newIds.add(cve.id); setSelectedIds(newIds); }} checked={selectedIds.has(cve.id)} className="rounded"/></td> <td className="px-4 py-4 text-blue-600 cursor-pointer hover:underline" onClick={() => onCveClick(cve.id)}>{cve.id}</td> <td className="px-4 py-4">{cve.date}</td> <td className="px-4 py-4">{cve.package}</td> <td className="px-4 py-4"><span className={`px-2 py-1 text-xs font-semibold rounded-full ${getSeverityClass(cve.severity)}`}>{cve.severity}</span></td> <td className="px-4 py-4">{cve.cvss}</td> <td className="px-4 py-4">{cve.hosts}</td> </tr> )))} </tbody> </table> </div> {isRepairModalOpen && <RepairTaskModal onClose={() => setIsRepairModalOpen(false)} cvesToRepair={cvesForModal} onCreateTask={onCreateTask} onExecuteTask={onExecuteTask} />}
                                        {isRemovalModalOpen && <RemovalTaskModal onClose={() => setIsRemovalModalOpen(false)}
                                        cvesToRemove={cvesForModal} onExecuteTask={onExecuteRemovalTask} />}
                                        </div> ); 
        };
        
        const CveDetailPage = ({ cveId, onBack, onCreateTask, onExecuteTask }) => {
            const [cveDetail, setCveDetail] = React.useState(null);
            const [isLoading, setIsLoading] = React.useState(true);
            const [isRepairModalOpen, setIsRepairModalOpen] = React.useState(false);
            const [hostStatusFilter, setHostStatusFilter] = React.useState('未修复');

            React.useEffect(() => {
                const loadDetail = async () => {
                    setIsLoading(true);
                    try {
                        const data = await api.fetchCveDetail(cveId);
                        setCveDetail(data);
                    } catch (error) {
                        console.error(`获取CVE ${cveId} 详情失败:`, error);
                        alert(`加载CVE详情失败: ${error.message}`);
                    } finally {
                        setIsLoading(false);
                    }
                };
                if (cveId) {
                loadDetail();
                }
            }, [cveId]);

            const filteredHosts = React.useMemo(() => {
                if (!cveDetail || !Array.isArray(cveDetail.affectedHosts)) {
                    return [];
                }
                return cveDetail.affectedHosts;
            }, [cveDetail, hostStatusFilter]);

            const getSeverityClass = (severity, type = 'full') => {
            const colors = {
                '高风险': { full: 'bg-red-100 text-red-800', border: 'border-red-500 text-red-600' },
                '中风险': { full: 'bg-yellow-100 text-yellow-800', border: 'border-yellow-500 text-yellow-600' },
                '低风险': { full: 'bg-blue-100 text-blue-800', border: 'border-blue-500 text-blue-600' },
            };
            return colors[severity]?.[type] || 'bg-gray-100 text-gray-800';
            };
            
            if (isLoading) return <div className="text-center p-10">正在加载 CVE 详情...</div>;
            if (!cveDetail) return <div className="text-center p-10">无法加载 CVE 详情。 <button onClick={onBack} className="text-blue-600 hover:underline">返回列表</button></div>;
            
            const cvesForModal = [cveDetail];

            return (
                <div className="bg-white p-6 rounded-lg shadow-md space-y-6">
                    <div className="flex justify-between items-center">
                        <h2 className="text-2xl font-bold">{cveDetail.id}</h2>
                        <button onClick={onBack} className="px-4 py-2 border rounded-md text-sm hover:bg-gray-100">返回</button>
                    </div>

                    <div className="border rounded-md p-4 space-y-3">
                        <div className="flex justify-between items-center">
                            <div>
                                <span className="text-sm font-semibold">发布时间：</span><span className="text-sm">{cveDetail.releaseDate}</span>
                            </div>
                            <div>
                                <span className={`text-sm font-bold p-2 rounded ${getSeverityClass(cveDetail.severity, 'border')}`}>严重性：{cveDetail.severity}</span>
                            </div>
                        </div>
                        <div>
                            <span className="text-sm font-semibold">CVSS 3.0 评分：</span><span className="text-sm font-bold text-red-600">{cveDetail.cvss}</span>
                        </div>
                        <div>
                            <span className="text-sm font-semibold">关联CVE：</span><span className="text-sm text-blue-600">{cveDetail.relatedCveCount} ↑</span>
                        </div>
                        <div>
                            <p className="text-sm font-semibold">cve描述：</p>
                            <p className="text-sm text-gray-700 mt-1">{cveDetail.description}</p>
                        </div>
                    </div>

                    <div>
                        <h3 className="text-md font-bold mb-2">影响产品：</h3>
                        <table className="min-w-full text-sm border">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="p-2 text-left font-semibold text-gray-600">产品</th>
                                    <th className="p-2 text-left font-semibold text-gray-600">软件包</th>
                                </tr>
                            </thead>
                            <tbody>
                                {(cveDetail.affectedProducts || []).map((p, i) => (
                                    <tr key={i} className="border-t">
                                        <td className="p-2">{p.product}</td>
                                        <td className="p-2">{p.package}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <div>
                        <div className="flex justify-between items-center mb-2">
                            <h3 className="text-md font-bold">受影响主机</h3>
                            <div className="flex items-center space-x-2">
                                <button 
                                    onClick={() => setHostStatusFilter('未修复')}
                                    className={`px-3 py-1.5 rounded-md text-sm ${hostStatusFilter === '未修复' ? 'bg-blue-500 text-white' : 'border bg-white hover:bg-gray-100'}`}
                                >
                                    未修复
                                </button>
                                <button 
                                    onClick={() => setHostStatusFilter('已修复')}
                                    className={`px-3 py-1.5 rounded-md text-sm ${hostStatusFilter === '已修复' ? 'bg-blue-500 text-white' : 'border bg-white hover:bg-gray-100'}`}
                                >
                                    已修复
                                </button>
                                <div className="relative">
                                    <input type="text" placeholder="按主机名搜索" className="border rounded-md py-1.5 pl-8 pr-4 text-sm w-48" />
                                    <svg className="w-4 h-4 text-gray-400 absolute left-2.5 top-1/2 -translate-y-1/2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                                </div>
                                <button onClick={() => setIsRepairModalOpen(true)} className="px-3 py-1.5 bg-blue-500 text-white rounded-md text-sm hover:bg-blue-600">生成修复任务</button>
                            </div>
                        </div>
                        <table className="min-w-full text-sm border">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="p-2 w-10"><input type="checkbox" /></th>
                                    <th className="p-2 text-left font-semibold text-gray-600">主机名</th>
                                    <th className="p-2 text-left font-semibold text-gray-600">ip地址</th>
                                    <th className="p-2 text-left font-semibold text-gray-600">主机组</th>
                                    <th className="p-2 text-left font-semibold text-gray-600">CVE REPO</th>
                                    <th className="p-2 text-left font-semibold text-gray-600">上次扫描</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredHosts.map((host, i) => (
                                    <tr key={host.hostname || i} className="border-t">
                                        <td className="p-2"><input type="checkbox" /></td>
                                        <td className="p-2 text-blue-600">{host.name}</td>
                                        <td className="p-2">{host.ip}</td>
                                        <td className="p-2">{host.group}</td>
                                        <td className="p-2">{host.repo}</td>
                                        <td className="p-2">{host.lastScan}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                    {isRepairModalOpen && <RepairTaskModal onClose={() => setIsRepairModalOpen(false)} cvesToRepair={cvesForModal} onCreateTask={onCreateTask} onExecuteTask={onExecuteTask} />}
                </div>
            );
        };

        const renderContent = () => {
            if(isLoading) return <div className="text-center p-10">正在加载CVE列表...</div>;
            
            switch (view.page) {
                case 'list':
                    return <CveListPage onCveClick={handleNavigateToDetail} allCves={cveList} onRefresh={handleRefresh} isRefreshing={isRefreshing} onCreateTask={handleCreateTask} onExecuteTask={handleExecuteRepair} onExecuteRemovalTask={handleExecuteRemoval} />;
                                case 'detail':
                    return <CveDetailPage cveId={view.param} onBack={handleNavigateToList} onCreateTask={handleCreateTask} onExecuteTask={handleExecuteRepair} onExecuteRemovalTask={handleExecuteRemoval} />;
                            default:
                            return <div>页面加载错误</div>;

            }
        };

        return <div className="h-full">{renderContent()}</div>;
        };
    //CVEs组件结束