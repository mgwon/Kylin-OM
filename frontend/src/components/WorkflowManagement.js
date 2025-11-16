 //工作流页面组件 
    const WorkflowManagement = () => {

        // -----------------------------------------------------------------
        // 状态管理 (State Management)
        // -----------------------------------------------------------------
        const [view, setView] = React.useState({ page: 'list', param: null });
        const [workflows, setWorkflows] = React.useState([]);
        const [applications, setApplications] = React.useState([]);
        const [workflowLoading, setWorkflowLoading] = React.useState(true);
        const [appLoading, setAppLoading] = React.useState(true);
        const [workflowCurrentPage, setWorkflowCurrentPage] = React.useState(1);
        const [workflowPageSize, setWorkflowPageSize] = React.useState(10);
        const [appCurrentPage, setAppCurrentPage] = React.useState(1);
        const [appPageSize, setAppPageSize] = React.useState(8);
        const [isAddAppModalOpen, setIsAddAppModalOpen] = React.useState(false);

        // -----------------------------------------------------------------
        // 导航处理 (Navigation Handlers)
        // -----------------------------------------------------------------
        const handleNavigateToDetail = (workflowId) => setView({ page: 'detail', param: workflowId });
        const handleNavigateToList = () => setView({ page: 'list', param: null });
        const handleNavigateToAppDetail = (appId) => setView({ page: 'app_detail', param: appId });
        
        // -----------------------------------------------------------------
        // 数据获取 (Data Fetching)
        // -----------------------------------------------------------------
        const fetchWorkflows = React.useCallback(async () => {
            setWorkflowLoading(true);
            try {
                const response = await fetch('http://localhost:5000/api/workflows');
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const data = await response.json();
                setWorkflows(data);
            } catch (error) {
                console.error("获取工作流数据失败:", error);
                alert(`获取工作流数据失败: ${error.message}.`);
                setWorkflows([]);
            } finally {
                setWorkflowLoading(false);
            }
        }, []);

        const fetchApplications = React.useCallback(async () => {
            setAppLoading(true);
            try {
                const response = await fetch('http://localhost:5000/api/applications');
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const data = await response.json();
                setApplications(data);
            } catch (error) {
                console.error("获取应用数据失败:", error);
                alert(`获取应用数据失败: ${error.message}.`);
                setApplications([]);
            } finally {
                setAppLoading(false);
            }
        }, []);
        
        React.useEffect(() => {
            fetchWorkflows();
            fetchApplications();
        }, [fetchWorkflows, fetchApplications]);

        
        const handleUpdateWorkflowStatus = async (workflowId, newStatus) => {
            try {
                const response = await fetch('http://localhost:5000/api/workflows/update_status', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ id: workflowId, status: newStatus }),
                });

                if (!response.ok) {
                    // 如果后端返回错误，尝试读取错误信息并抛出
                    const errorData = await response.json();
                    throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
                }

                // API调用成功后，才更新前端的UI状态
                setWorkflows(currentWorkflows => 
                    currentWorkflows.map(wf => 
                        wf.id === workflowId ? { ...wf, status: newStatus } : wf
                    )
                );
                // 可以在这里给一个更明确的成功提示
                alert(`工作流状态已成功更新为 "${newStatus}"`);

            } catch (error) {
                console.error("更新工作流状态失败:", error);
                alert(`操作失败: ${error.message}`);
            }
        };
        
       
        const handleDeleteWorkflow = async (workflowIdToDelete) => {
            // 先弹窗确认，用户取消则直接返回
            if (!window.confirm(`您确定要删除此工作流吗？此操作无法撤销。`)) {
                return;
            }

            try {
                const response = await fetch('http://localhost:5000/api/workflows/delete', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ id: workflowIdToDelete }),
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
                }
                
                // API调用成功后，才更新前端UI并给出提示
                alert('工作流已成功删除！');
                
                // 从前端列表中移除
                setWorkflows(currentWorkflows => 
                    currentWorkflows.filter(wf => wf.id !== workflowIdToDelete)
                );

                // 如果当前在详情页，则返回列表页
                if (view.page === 'detail' && view.param === workflowIdToDelete) {
                    handleNavigateToList();
                }

            } catch (error) {
                console.error("删除工作流失败:", error);
                alert(`删除失败: ${error.message}`);
            }
        };



        const handleToggleRecommend = async (workflowId) => {
            try {
                const response = await fetch('http://localhost:5000/api/workflows/toggle_recommend', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: workflowId }),
                });

                if (!response.ok) {
                    throw new Error('Failed to update recommend status');
                }

                const updatedWorkflow = await response.json();

                // 使用后端返回的最新数据更新前端状态
                setWorkflows(currentWorkflows =>
                    currentWorkflows.map(wf =>
                        wf.id === workflowId 
                            ? { ...wf, isRecommended: updatedWorkflow.workflow.isRecommended } 
                            : wf
                    )
                );
                alert(`工作流 "${updatedWorkflow.workflow.name}" 的推荐状态已更新。`);

            } catch (error) {
                console.error("切换推荐状态失败:", error);
                alert(`操作失败: ${error.message}`);
            }
        };
        
        const handleAddNewWorkflow = async (formData) => {
            try {
                const response = await fetch('http://localhost:5000/api/workflows/add', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData), // formData 包含了所有需要的信息
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || '创建工作流失败');
                }

                const result = await response.json();
                alert(result.message); // 显示来自后端的成功消息

                // 使用后端返回的、带有真实ID的新工作流对象来更新前端状态
                setWorkflows(prev => [result.workflow, ...prev]);
                handleNavigateToList();

            } catch (error) {
                console.error("创建工作流失败:", error);
                alert(`创建失败: ${error.message}`);
            }
        };
        
        const handleOpenAddAppModal = () => setIsAddAppModalOpen(true);
        const handleCloseAddAppModal = () => setIsAddAppModalOpen(false);
        const handleSaveNewApp = async (appData) => {
            try {
                const response = await fetch('http://localhost:5000/api/applications/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(appData),
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || '保存应用失败');
                }

                const result = await response.json();
                alert(result.message);

                // 直接调用 fetchApplications 刷新列表，而不是手动添加
                fetchApplications();
                handleCloseAddAppModal(); // 关闭弹窗

            } catch (error) {
                console.error("保存新应用失败:", error);
                alert(`保存失败: ${error.message}`);
            }
        };
        const handleWorkflowPageChange = (newPage) => setWorkflowCurrentPage(newPage);
        const handleWorkflowPageSizeChange = (newSize) => { setWorkflowPageSize(newSize); setWorkflowCurrentPage(1); };
        const handleAppPageChange = (newPage) => setAppCurrentPage(newPage);
        const handleAppPageSizeChange = (newSize) => { setAppPageSize(newSize); setAppCurrentPage(1); };

        const paginatedWorkflows = React.useMemo(() => workflows.slice((workflowCurrentPage - 1) * workflowPageSize, workflowCurrentPage * workflowPageSize), [workflows, workflowCurrentPage, workflowPageSize]);
        const paginatedApps = React.useMemo(() => applications.slice((appCurrentPage - 1) * appPageSize, appCurrentPage * appPageSize), [applications, appCurrentPage, appPageSize]);

        
        
        const ModifyModelModal = ({ isOpen, onClose, onApply, currentIndicator }) => {
            
            if (!isOpen) return null;
            const [allModels, setAllModels] = React.useState([]);
            const [isLoading, setIsLoading] = React.useState(true);
            const [error, setError] = React.useState(null);
            const [selectedModelId, setSelectedModelId] = React.useState(currentIndicator?.modelId || null);
            const [searchQuery, setSearchQuery] = React.useState('');
            const [currentPage, setCurrentPage] = React.useState(1);
            const [pageSize, setPageSize] = React.useState(5);
            const fetchModels = React.useCallback(async () => {
                setIsLoading(true);
                setError(null);
                try {
                    const response = await fetch('http://localhost:5000/api/models');
                    if (!response.ok) {
                        throw new Error(`网络错误 (状态: ${response.status})`);
                    }
                    const data = await response.json();
                    setAllModels(data);
                } catch (err) {
                    console.error("加载模型列表失败:", err);
                    setError("无法加载模型列表。");
                } finally {
                    setIsLoading(false);
                }
            }, []);
            React.useEffect(() => {
                fetchModels();
            }, [fetchModels]);
            const filteredModels = React.useMemo(() => {
                const lowercasedQuery = searchQuery.toLowerCase().trim();
                if (!lowercasedQuery) {
                    return allModels;
                }
                return allModels.filter(model => 
                    model.name.toLowerCase().includes(lowercasedQuery) ||
                    model.algorithm.toLowerCase().includes(lowercasedQuery)
                );
            }, [allModels, searchQuery]);
            React.useEffect(() => {
                setCurrentPage(1);
            }, [searchQuery]);
            const handleApply = () => {
                const selectedModel = allModels.find(m => m.id === selectedModelId);
                if (selectedModel) {
                    onApply(selectedModel);
                }
            };
            const selectedModel = allModels.find(m => m.id === selectedModelId);
            const paginatedModels = filteredModels.slice((currentPage - 1) * pageSize, currentPage * pageSize);
            return (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50" onClick={onClose}>
                <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl" onClick={e => e.stopPropagation()}>
                    <div className="p-4 border-b flex justify-between items-center"><h2 className="text-lg font-semibold">修改模型</h2><button onClick={onClose} className="text-gray-400 hover:text-gray-800 text-3xl font-light leading-none">×</button></div>
                    <div className="p-6 space-y-4">
                        <div className="flex items-center text-sm space-x-4"><span>已取得模型总条数：{allModels.length}</span><span className="text-blue-600">{selectedModel ? `已选择 ${selectedModel.name} 模型` : '请选择一个模型'}</span></div>
                        <div className="flex items-center space-x-2">
                            <div className="relative w-40">
                                <select className="w-full border border-gray-300 rounded-md p-2 text-sm appearance-none bg-white"><option>模型名称</option></select>
                                <svg className="w-4 h-4 text-gray-400 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd"></path></svg>
                            </div>
                            <div className="relative flex-grow">
                                <input type="text" placeholder="按关键字进行搜索" className="w-full border border-gray-300 rounded-md p-2 pl-8 text-sm" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
                                <svg className="w-4 h-4 text-gray-400 absolute left-2.5 top-1/2 -translate-y-1/2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                            </div>
                        </div>
                        <div className="overflow-x-auto border rounded-md">
                            <table className="min-w-full text-sm">
                                <thead className="bg-gray-50">
                                    <tr><th className="p-3 w-10"></th>{['模型', '算法', '精确度', '标签', '创建时间'].map(header => (<th key={header} className="p-3 text-left font-semibold text-gray-600">{header}</th>))}</tr>
                                </thead>
                                <tbody>
                                    {isLoading ? ( <tr><td colSpan="6" className="p-10 text-center text-gray-500">加载中...</td></tr> ) : 
                                    error ? ( <tr><td colSpan="6" className="p-10 text-center text-red-500">{error}</td></tr> ) :
                                    paginatedModels.length === 0 ? ( <tr><td colSpan="6" className="p-10 text-center text-gray-500">未找到匹配的模型。</td></tr> ) :
                                    paginatedModels.map(model => (
                                        <tr key={model.id} className={`border-b hover:bg-gray-50 ${selectedModelId === model.id ? 'bg-blue-50' : ''}`}>
                                            <td className="p-3 text-center"><input type="radio" name="model-selection" checked={selectedModelId === model.id} onChange={() => setSelectedModelId(model.id)} /></td>
                                            <td className="p-3">{model.name}</td><td className="p-3">{model.algorithm}</td><td className="p-3">{model.precision}</td><td className="p-3">{model.tags.join(', ')}</td><td className="p-3">{model.createdAt}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        <Pagination currentPage={currentPage} totalItems={filteredModels.length} pageSize={pageSize} onPageChange={setCurrentPage} onPageSizeChange={setPageSize} options={[5]} />
                    </div>
                    <div className="flex justify-end items-center p-4 border-t bg-gray-50 space-x-2">
                        <button onClick={onClose} className="bg-white border border-gray-300 text-gray-700 font-semibold py-1.5 px-6 rounded-md hover:bg-gray-100 text-sm">取消</button>
                        <button onClick={handleApply} disabled={!selectedModelId} className="bg-blue-500 text-white font-semibold py-1.5 px-6 rounded-md hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-sm">应用</button>
                    </div>
                </div>
            </div>
            );
        };

        const AddApplicationModal = ({ isOpen, onClose, onSave }) => {
            if (!isOpen) return null;
            
            // 1. 新增一个 state 来管理流程步骤数组
            const [name, setName] = React.useState('');
            const [version, setVersion] = React.useState(''); 
            const [description, setDescription] = React.useState('');
            const [flowSteps, setFlowSteps] = React.useState([{ tempId: Date.now(), name: '' }]); // 初始有一个空步骤

            // 2. 新增三个函数来处理步骤的增、删、改
            const handleAddStep = () => {
                setFlowSteps(prev => [...prev, { tempId: Date.now(), name: '' }]);
            };

            const handleRemoveStep = (indexToRemove) => {
                setFlowSteps(prev => prev.filter((_, index) => index !== indexToRemove));
            };

            const handleStepNameChange = (indexToChange, newName) => {
                setFlowSteps(prev => 
                    prev.map((step, index) => 
                        index === indexToChange ? { ...step, name: newName } : step
                    )
                );
            };

            // 3. 修改保存函数，使其包含 flowSteps
            const handleSaveClick = () => {
                if (!name.trim() || !version.trim()) {
                    alert('应用名称和版本号不能为空！');
                    return;
                }
                // 过滤掉空的步骤并只保留name字段
                const finalFlow = flowSteps
                    .map(step => ({ name: step.name.trim() }))
                    .filter(step => step.name !== '');

                onSave({ name, version, description, flow: finalFlow });
            };

            return (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
                    <div className="bg-white rounded-lg shadow-xl w-full max-w-lg">
                        <div className="p-4 border-b"><h3 className="text-lg font-semibold">新增应用</h3></div>
                        <div className="p-6 space-y-4 max-h-[70vh] overflow-y-auto">
                            {/* 基本信息输入框 */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700">应用名称</label>
                                <input value={name} onChange={e => setName(e.target.value)} className="w-full border rounded-md p-2 mt-1" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">版本</label>
                                <input value={version} onChange={e => setVersion(e.target.value)} placeholder="例如: 1.0" className="w-full border rounded-md p-2 mt-1" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">应用描述</label>
                                <textarea value={description} onChange={e => setDescription(e.target.value)} className="w-full border rounded-md p-2 mt-1" rows="3"></textarea>
                            </div>
                            
                            {/* 4. 新增的动态流程区域 */}
                            <div className="border-t pt-4">
                                <label className="block text-sm font-medium text-gray-700 mb-2">应用流程</label>
                                <div className="space-y-2">
                                    {flowSteps.map((step, index) => (
                                        <div key={step.tempId} className="flex items-center space-x-2">
                                            <input 
                                                value={step.name} 
                                                onChange={(e) => handleStepNameChange(index, e.target.value)}
                                                placeholder={`步骤 ${index + 1}`}
                                                className="flex-grow border rounded-md p-2" 
                                            />
                                            <button 
                                                onClick={() => handleRemoveStep(index)} 
                                                className="bg-red-500 text-white rounded-md h-9 w-9 flex-shrink-0 hover:bg-red-600"
                                                disabled={flowSteps.length <= 1} // 如果只剩一个则禁止删除
                                            >
                                                -
                                            </button>
                                        </div>
                                    ))}
                                </div>
                                <button onClick={handleAddStep} className="mt-2 text-blue-600 hover:underline text-sm">+ 添加步骤</button>
                            </div>
                        </div>
                        <div className="p-4 bg-gray-50 border-t flex justify-end space-x-2">
                            <button onClick={onClose} className="px-4 py-2 border rounded-md bg-white text-gray-700 hover:bg-gray-50">取消</button>
                            <button onClick={handleSaveClick} className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">保存</button>
                        </div>
                    </div>
                </div>
            );
        };

        const WorkflowDetailPage = ({ workflowId, onBack, onDelete, sharedStatus, onUpdateStatus }) => {
            
            const [workflowDetails, setWorkflowDetails] = React.useState(null);
            const [isLoading, setIsLoading] = React.useState(true);
            const [error, setError] = React.useState(null);
            const [activeTab, setActiveTab] = React.useState('single-metric');
            const [expandedHostId, setExpandedHostId] = React.useState(null);
            const [isModifyModalOpen, setIsModifyModalOpen] = React.useState(false);
            const [editingIndicator, setEditingIndicator] = React.useState(null);
            const [expandedRuleId, setExpandedRuleId] = React.useState(null);

            // --- 新增: 状态管理 ---
            const [isRuleModalOpen, setIsRuleModalOpen] = React.useState(false);
            const [editingRule, setEditingRule] = React.useState(null); // null表示新增, object表示编辑
            
            const fetchWorkflowDetail = React.useCallback(async (id) => {
                const response = await fetch(`http://localhost:5000/api/workflows/${id}`);
                if (!response.ok) {
                    throw new Error(`网络响应错误，无法加载 ${id}.txt (状态: ${response.status})`);
                }
                const data = await response.json();
                if (data.affectedHosts) {
                    data.hosts = data.affectedHosts;
                    delete data.affectedHosts;
                }
                return data;
            }, []);

            React.useEffect(() => {
                const loadData = async () => {
                    setIsLoading(true);
                    setError(null);
                    try {
                        const data = await fetchWorkflowDetail(workflowId);
                        setWorkflowDetails(data);
                        if (data && data.hosts && data.hosts.length > 0) {
                            setExpandedHostId(data.hosts[0].id);
                        }
                    } catch (err) {
                        console.error("获取工作流详情失败:", err);
                        setError(err.message);
                    } finally {
                        setIsLoading(false);
                    }
                };
                loadData();
            }, [workflowId, fetchWorkflowDetail]);
            
            const workflow = workflowDetails ? { ...workflowDetails, status: sharedStatus } : null;
            const host = workflow?.hosts?.find(h => h.id === expandedHostId);
            
            const handleOpenModifyModal = (indicator) => { setEditingIndicator(indicator); setIsModifyModalOpen(true); };
            const handleCloseModifyModal = () => { setIsModifyModalOpen(false); setEditingIndicator(null); };
            
            const handleApplyModifyModel = async (newModel) => {
                if (!editingIndicator || !host || !workflow) return;

                try {
                    const response = await fetch('http://localhost:5000/api/workflows/update_indicator', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            workflowId: workflow.id,
                            hostId: host.id,
                            indicatorId: editingIndicator.id,
                            newModel: {
                                name: newModel.name,
                                algorithm: newModel.algorithm,
                            },
                        }),
                    });

                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.error || '更新指标失败');
                    }

                    // API调用成功后，再更新前端UI以立即反馈
                    setWorkflowDetails(prevDetails => {
                        const newDetails = JSON.parse(JSON.stringify(prevDetails));
                        const hostToUpdate = newDetails.hosts.find(h => h.id === host.id);
                        const indicatorToUpdate = hostToUpdate.indicators.find(ind => ind.id === editingIndicator.id);
                        if (indicatorToUpdate) {
                            indicatorToUpdate.model = newModel.name;
                            indicatorToUpdate.algorithm = newModel.algorithm;
                        }
                        return newDetails;
                    });
                    alert('模型修改已成功保存！');

                } catch (error) {
                    console.error("更新指标失败:", error);
                    alert(`操作失败: ${error.message}`);
                } finally {
                    handleCloseModifyModal();
                }
            };

            const handleExecute = () => { onUpdateStatus(workflow.id, '运行中'); /*alert(`工作流 "${workflow.name}" 已开始执行。`);*/ };
            const handlePause = () => { onUpdateStatus(workflow.id, '已暂停'); /*alert(`工作流 "${workflow.name}" 已暂停（模拟）。`); */};
            const handleDelete = () => { if (window.confirm(`您确定要删除工作流 "${workflow.name}" 吗？此操作无法撤销。`)) { onDelete(workflow.id); } };
            
            // --- 新增: 多指标规则的增删改 Handlers ---
            const handleOpenAddRuleModal = () => {
                setEditingRule(null);
                setIsRuleModalOpen(true);
            };
            const handleOpenEditRuleModal = (ruleToEdit) => {
                setEditingRule(ruleToEdit);
                setIsRuleModalOpen(true);
            };
            const handleCloseRuleModal = () => {
                setIsRuleModalOpen(false);
                setEditingRule(null);
            };
            const handleSaveRule = async (ruleData) => {
                try {
                    const response = await fetch('http://localhost:5000/api/workflows/save_rule', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            workflowId: workflow.id,
                            hostId: expandedHostId,
                            ruleData: { ...ruleData, id: editingRule ? editingRule.id : null }
                        }),
                    });

                    if (!response.ok) {
                        const err = await response.json();
                        throw new Error(err.error || '保存规则失败');
                    }
                    
                    const result = await response.json();
                    alert(result.message);

                    // API成功后，使用后端返回的最新数据刷新前端（特别是为了获取新规则的ID）
                    setWorkflowDetails(prevDetails => {
                        const newDetails = JSON.parse(JSON.stringify(prevDetails));
                        const hostToUpdate = newDetails.hosts.find(h => h.id === expandedHostId);
                        if (!hostToUpdate.multiMetricRules) hostToUpdate.multiMetricRules = [];
                        
                        if (editingRule) { // 编辑模式
                            const ruleIndex = hostToUpdate.multiMetricRules.findIndex(r => r.id === editingRule.id);
                            if (ruleIndex > -1) {
                                // 使用后端返回的数据进行更新
                                hostToUpdate.multiMetricRules[ruleIndex] = { ...hostToUpdate.multiMetricRules[ruleIndex], ...result.rule };
                            }
                        } else { // 新增模式
                            hostToUpdate.multiMetricRules.push(result.rule); // 添加后端返回的带有ID的新规则
                        }
                        return newDetails;
                    });

                } catch (error) {
                    console.error("保存规则失败:", error);
                    alert(`操作失败: ${error.message}`);
                } finally {
                    handleCloseRuleModal();
                }
            };

            const handleDeleteRule = async (ruleId, ruleName) => {
                if (window.confirm(`确定要删除规则 "${ruleName}" 吗？`)) {
                    try {
                        const response = await fetch('http://localhost:5000/api/workflows/delete_rule', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                workflowId: workflow.id,
                                hostId: expandedHostId,
                                ruleId: ruleId
                            }),
                        });

                        if (!response.ok) {
                            const err = await response.json();
                            throw new Error(err.error || '删除规则失败');
                        }

                        const result = await response.json();
                        alert(result.message);

                        // API成功后，更新前端UI
                        setWorkflowDetails(prevDetails => {
                            const newDetails = JSON.parse(JSON.stringify(prevDetails));
                            const hostToUpdate = newDetails.hosts.find(h => h.id === expandedHostId);
                            if (hostToUpdate && hostToUpdate.multiMetricRules) {
                                hostToUpdate.multiMetricRules = hostToUpdate.multiMetricRules.filter(r => r.id !== ruleId);
                            }
                            return newDetails;
                        });

                    } catch (error) {
                        console.error("删除规则失败:", error);
                        alert(`操作失败: ${error.message}`);
                    }
                }
            };
            
            const [currentPage, setCurrentPage] = React.useState(1);
            const [pageSize, setPageSize] = React.useState(10);
            const indicators = host ? host.indicators : [];
            const paginatedIndicators = indicators.slice((currentPage - 1) * pageSize, currentPage * pageSize);

            if (isLoading) return <div className="p-8 text-center text-gray-500">正在加载工作流详情...</div>;
            if (error) return <div className="p-8 text-center text-red-500">加载失败: {error}</div>;
            if (!workflow) return <div className="p-8 text-center text-gray-500">未找到工作流。</div>;
            
            const getStatusPill = (status) => {
                switch(status) {
                    case '运行中': return <span className="text-green-600 font-semibold">{status}</span>;
                    case '已暂停': return <span className="text-yellow-600 font-semibold">{status}</span>;
                    case '失败': return <span className="text-red-600 font-semibold">{status}</span>;
                    default: return <span className="text-gray-600 font-semibold">{status}</span>;
                }
            };
            
            return (
                <React.Fragment>
                <div className="space-y-6">
                    {/* ... (头部和单指标检测部分 JSX 保持不变) ... */}
                    <div className="text-sm text-gray-500"><a href="#" onClick={(e) => { e.preventDefault(); onBack(); }} className="text-blue-600 hover:underline">工作流</a><span className="mx-2">/</span><span className="text-gray-800">工作流详情</span></div>
                    <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
                        <div className="flex justify-between items-start">
                            <div>
                                <h2 className="text-xl font-bold text-gray-800 mb-4">{workflow.name}</h2>
                                <div className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm text-gray-600"><span>主机组：{workflow.hostGroup}</span><span>应用：{workflow.application}</span><span>主机数：{workflow.hostCount}</span><span>状态：{getStatusPill(workflow.status)}</span></div>
                                <p className="mt-4 text-sm text-gray-600">描述：{workflow.description}</p>
                            </div>
                            <div className="flex space-x-2">
                                <button onClick={handleExecute} disabled={workflow.status === '运行中'} className="bg-blue-500 text-white px-4 py-1.5 rounded-md text-sm hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed">执行</button>
                                <button onClick={handlePause} disabled={workflow.status !== '运行中'} className="bg-white border border-gray-300 text-gray-700 px-4 py-1.5 rounded-md text-sm hover:bg-gray-50 disabled:bg-gray-300 disabled:cursor-not-allowed">暂停</button>
                                <button onClick={handleDelete} className="bg-white border border-red-500 text-red-500 px-4 py-1.5 rounded-md text-sm hover:bg-red-50">删除</button>
                            </div>
                        </div>
                        <div className="mt-6 border-t pt-4">
                             <div className="flex space-x-1">
                                <button onClick={() => setActiveTab('single-metric')} className={`px-4 py-2 text-sm rounded-t-md ${activeTab === 'single-metric' ? 'border-b-2 border-blue-500 text-blue-600 font-semibold' : 'text-gray-500 hover:bg-gray-100'}`}>单指标检测</button>
                                <button onClick={() => setActiveTab('multi-metric')} className={`px-4 py-2 text-sm rounded-t-md ${activeTab === 'multi-metric' ? 'border-b-2 border-blue-500 text-blue-600 font-semibold' : 'text-gray-500 hover:bg-gray-100'}`}>多指标检测</button>
                                <button onClick={() => setActiveTab('cluster-diag')} className={`px-4 py-2 text-sm rounded-t-md ${activeTab === 'cluster-diag' ? 'border-b-2 border-blue-500 text-blue-600 font-semibold' : 'text-gray-500 hover:bg-gray-100'}`}>集群故障诊断</button>
                            </div>
                        </div>
                    </div>
                     {activeTab === 'single-metric' && (
                        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
                            <table className="w-full text-sm text-left">
                                <thead className="text-gray-600 bg-gray-50">
                                    <tr><th className="p-3 w-12 text-center"><input type="checkbox" className="rounded border-gray-300" /></th><th className="p-3">主机名</th><th className="p-3">IP</th><th className="p-3">指标数</th></tr>
                                </thead>
                                <tbody>
                                    {workflow.hosts && workflow.hosts.map(hostItem => (
                                        <React.Fragment key={hostItem.id}>
                                            <tr className="border-b hover:bg-gray-50">
                                                <td className="p-3 text-center"><button onClick={() => setExpandedHostId(id => id === hostItem.id ? null : hostItem.id)} className="text-blue-500 font-mono text-lg w-6 h-6 flex items-center justify-center rounded hover:bg-gray-200">{expandedHostId === hostItem.id ? '−' : '+'}</button></td>
                                                <td className="p-3">{hostItem.name}</td><td className="p-3">{hostItem.ip}</td><td className="p-3">{hostItem.indicatorCount}</td>
                                            </tr>
                                            {expandedHostId === hostItem.id && (
                                                <tr className="bg-gray-50/50"><td colSpan="4" className="p-4">
                                                    <div className="bg-white border rounded-md p-4">
                                                        <table className="w-full text-sm">
                                                            <thead><tr className="border-b"><th className="p-2 text-left font-medium text-gray-600">单指标</th><th className="p-2 text-left font-medium text-gray-600">算法</th><th className="p-2 text-left font-medium text-gray-600">模型</th><th className="p-2 text-left font-medium text-gray-600">操作</th></tr></thead>
                                                            <tbody>
                                                                {paginatedIndicators.map(indicator => (
                                                                    <tr key={indicator.id} className="border-b last:border-b-0 hover:bg-gray-50"><td className="p-2">{indicator.name}</td><td className="p-2">{indicator.algorithm}</td><td className="p-2">{indicator.model}</td><td className="p-2"><button onClick={() => handleOpenModifyModal(indicator)} className="text-blue-600 hover:underline">修改</button></td></tr>
                                                                ))}
                                                            </tbody>
                                                        </table>
                                                        {indicators.length > pageSize && (<div className="pt-4"><Pagination currentPage={currentPage} totalItems={indicators.length} pageSize={pageSize} onPageChange={setCurrentPage} onPageSizeChange={setPageSize} /></div>)}
                                                    </div>
                                                </td></tr>
                                            )}
                                        </React.Fragment>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                    {activeTab === 'multi-metric' && (
                        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
                            <table className="w-full text-sm text-left">
                                <thead className="text-gray-600 bg-gray-50">
                                    <tr>
                                        <th className="p-3 w-12 text-center"><input type="checkbox" className="rounded border-gray-300" /></th>
                                        <th className="p-3">主机名</th><th className="p-3">IP</th><th className="p-3">规则数</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {workflow.hosts && workflow.hosts.map(hostItem => {
                                        const multiMetricRules = hostItem.multiMetricRules || [];
                                        return (
                                            <React.Fragment key={hostItem.id}>
                                                <tr className="border-b hover:bg-gray-50">
                                                    <td className="p-3 text-center"><button onClick={() => setExpandedHostId(id => id === hostItem.id ? null : hostItem.id)} className="text-blue-500 font-mono text-lg w-6 h-6 flex items-center justify-center rounded hover:bg-gray-200">{expandedHostId === hostItem.id ? '−' : '+'}</button></td>
                                                    <td className="p-3">{hostItem.name}</td><td className="p-3">{hostItem.ip}</td><td className="p-3">{multiMetricRules.length}</td>
                                                </tr>
                                                {expandedHostId === hostItem.id && (
                                                    <tr className="bg-gray-50/50"><td colSpan="4" className="p-4">
                                                        <div className="bg-white border rounded-md p-4">
                                                            <div className="flex justify-between items-center mb-2">
                                                                <h4 className="font-semibold text-gray-700">多指标检测规则</h4>
                                                                <button onClick={handleOpenAddRuleModal} className="bg-blue-500 text-white text-xs px-3 py-1 rounded hover:bg-blue-600">+ 新增规则</button>
                                                            </div>
                                                            {multiMetricRules.length === 0 ? (<div className="text-center py-4 text-gray-500">此主机没有配置多指标检测规则。</div>) : (
                                                                <table className="w-full text-sm">
                                                                    <thead className="border-b"><tr className="text-left text-gray-600 font-medium"><th className="p-2 w-10"></th><th className="p-2">规则名称</th><th className="p-2">当前值 / 阈值</th><th className="p-2">状态</th><th className="p-2">操作</th></tr></thead>
                                                                    <tbody>
                                                                        {multiMetricRules.map(rule => (
                                                                            <React.Fragment key={rule.id}>
                                                                                <tr className="border-b hover:bg-gray-50">
                                                                                    <td className="p-2 text-center"><button onClick={() => setExpandedRuleId(id => id === rule.id ? null : rule.id)} className="text-gray-500 font-mono w-5 h-5 flex items-center justify-center rounded text-sm hover:bg-gray-200">{expandedRuleId === rule.id ? '▾' : '▸'}</button></td>
                                                                                    <td className="p-2 font-semibold text-gray-800">{rule.name}</td>
                                                                                    <td className="p-2"><span className={`${rule.currentValue > rule.threshold ? 'text-red-600' : 'text-green-600'}`}>{rule.currentValue.toFixed(2)}</span><span className="text-gray-400 mx-1">/</span><span>{rule.threshold}</span></td>
                                                                                    <td className="p-2"><span className={`px-2 py-0.5 text-xs rounded-full ${rule.status === '告警' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>{rule.status}</span></td>
                                                                                    <td className="p-2 text-blue-600 space-x-2"><a href="#" onClick={(e) => { e.preventDefault(); handleOpenEditRuleModal(rule); }} className="hover:underline">编辑</a><a href="#" onClick={(e) => { e.preventDefault(); handleDeleteRule(rule.id, rule.name); }} className="hover:underline">删除</a></td>
                                                                                </tr>
                                                                                {expandedRuleId === rule.id && (
                                                                                    <tr className="bg-white"><td colSpan="5" className="px-2 py-1">
                                                                                        <div className="bg-gray-100 rounded-md p-3 ml-8">
                                                                                            <h5 className="font-semibold text-xs text-gray-600 mb-2">指标构成</h5>
                                                                                            <table className="w-full text-xs">
                                                                                                <thead className="text-gray-500"><tr className="border-b"><th className="py-1 px-2 text-left">指标</th><th className="py-1 px-2 text-left">当前值</th><th className="py-1 px-2 text-left">权重</th><th className="py-1 px-2 text-right">加权值</th></tr></thead>
                                                                                                <tbody>
                                                                                                    {rule.metrics.map(metric => (<tr key={metric.id}><td className="py-1 px-2">{metric.name}</td><td className="py-1 px-2">{metric.currentValue}</td><td className="py-1 px-2">{metric.weight}</td><td className="py-1 px-2 text-right font-mono">{(metric.currentValue * metric.weight).toFixed(2)}</td></tr>))}
                                                                                                    <tr className="border-t font-bold"><td colSpan="3" className="py-1 px-2 text-right">加权和:</td><td className="py-1 px-2 text-right font-mono">{rule.currentValue.toFixed(2)}</td></tr>
                                                                                                </tbody>
                                                                                            </table>
                                                                                        </div>
                                                                                    </td></tr>
                                                                                )}
                                                                            </React.Fragment>
                                                                        ))}
                                                                    </tbody>
                                                                </table>
                                                            )}
                                                        </div>
                                                    </td></tr>
                                                )}
                                            </React.Fragment>
                                        )
                                    })}
                                </tbody>
                            </table>
                        </div>
                    )}
                    {/* 集群故障诊断 TAB */}
                    {activeTab === 'cluster-diag' && (
                        <ClusterDiagnosisTab workflowId={workflow.id} />
                    )}
                </div>
                <ModifyModelModal isOpen={isModifyModalOpen} onClose={handleCloseModifyModal} onApply={handleApplyModifyModel} currentIndicator={editingIndicator} />
                <AddEditRuleModal isOpen={isRuleModalOpen} onClose={handleCloseRuleModal} onSave={handleSaveRule} rule={editingRule} hostName={host?.name} />
                </React.Fragment>
            );
        };

        const ClusterDiagnosisTab = ({ workflowId }) => {
            const [data, setData] = React.useState(null);
            const [loading, setLoading] = React.useState(true);
            const [error, setError] = React.useState(null);
            const [activeLogTab, setActiveLogTab] = React.useState(0);

            React.useEffect(() => {
                const fetchData = async () => {
                    setLoading(true);
                    setError(null);
                    try {
                        const response = await fetch(`http://localhost:5000/api/workflows/cluster-diag/${workflowId}`);
                        if (!response.ok) throw new Error(`无法加载诊断报告 (ID: ${workflowId})`);
                        const result = await response.json();
                        setData(result);
                        if(result.logs && result.logs.length > 0) {
                            setActiveLogTab(result.logs[0].serviceName);
                        }
                    } catch (err) {
                        setError(err.message);
                    } finally {
                        setLoading(false);
                    }
                };
                fetchData();
            }, [workflowId]);

            const getStatusColor = (status) => {
                switch(status) {
                    case 'healthy': return { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-500'};
                    case 'degraded': return { bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-500'};
                    case 'error': return { bg: 'bg-orange-100', text: 'text-orange-800', border: 'border-orange-500'};
                    case 'critical': return { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-500'};
                    default: return { bg: 'bg-gray-100', text: 'text-gray-800', border: 'border-gray-500'};
                }
            };

            if (loading) return <div className="text-center p-10">正在加载诊断报告...</div>;
            if (error) return <div className="text-center p-10 text-red-600 bg-red-50 rounded-md">错误: {error}</div>;
            if (!data) return <div className="text-center p-10">没有可用的诊断数据。</div>;

            return (
                <div className="space-y-6">
                    {/* AI Summary */}
                    <div className="bg-white p-6 rounded-lg shadow-md border">
                        <h3 className="text-lg font-semibold mb-4">智能诊断摘要</h3>
                        <blockquote className="border-l-4 border-blue-500 bg-blue-50 p-4">
                            <p className="text-gray-700 italic">🤖 {data.aiSummary}</p>
                        </blockquote>
                    </div>
                    
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Topology */}
                        <div className="bg-white p-6 rounded-lg shadow-md border">
                             <h3 className="text-lg font-semibold mb-4">故障拓扑与影响面</h3>
                             <div className="p-4 bg-gray-50 rounded-md flex justify-center items-center space-x-8 min-h-[150px]">
                                {data.topology.nodes.map(node => {
                                    const colors = getStatusColor(node.status);
                                    return (
                                        <div key={node.id} className={`relative p-4 border-2 rounded-lg shadow-sm text-center ${colors.bg} ${colors.border}`}>
                                            <div className={`font-bold ${colors.text}`}>{node.label}</div>
                                            <div className={`text-xs capitalize ${colors.text}`}>{node.status}</div>
                                            {node.isRootCause && <div className="absolute -top-2 -right-2 px-1.5 py-0.5 bg-red-600 text-white text-xs font-bold rounded-full animate-pulse">根因</div>}
                                        </div>
                                    );
                                })}
                             </div>
                        </div>
                        {/* Event Timeline */}
                        <div className="bg-white p-6 rounded-lg shadow-md border">
                            <h3 className="text-lg font-semibold mb-4">关键事件时间轴</h3>
                            <ul className="space-y-3">
                                {data.eventTimeline.map(event => (
                                    <li key={event.id} className="flex items-start text-sm">
                                        <span className="font-mono text-gray-500 mr-4">{event.time}</span>
                                        <span className={`font-semibold mr-2 ${getStatusColor(event.level).text}`}>{event.service}:</span>
                                        <span className="text-gray-700">{event.message}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    {/* Logs & Recommendations */}
                    <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
                        <div className="lg:col-span-3 bg-white p-6 rounded-lg shadow-md border">
                            <h3 className="text-lg font-semibold mb-4">关联日志摘要</h3>
                            <div className="border-b mb-2">
                                <nav className="flex space-x-4">
                                    {data.logs.map(log => (
                                        <button key={log.serviceName} onClick={() => setActiveLogTab(log.serviceName)}
                                            className={`pb-2 border-b-2 text-sm ${activeLogTab === log.serviceName ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500'}`}>
                                            {log.serviceName}
                                        </button>
                                    ))}
                                </nav>
                            </div>
                            <pre className="bg-gray-800 text-white p-4 rounded-md font-mono text-xs h-48 overflow-auto">
                               {data.logs.find(log => log.serviceName === activeLogTab)?.logContent || '无日志'}
                            </pre>
                        </div>
                        <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow-md border">
                            <h3 className="text-lg font-semibold mb-4">优化建议</h3>
                             <ul className="space-y-2 text-sm text-gray-700 list-inside">
                                {data.recommendations.map((rec, index) => <li key={index} dangerouslySetInnerHTML={{ __html: rec.replace(/\*\*(.*?)\*\*/g, '<strong class=\"font-bold text-gray-900\">$1</strong>') }} />)}
                            </ul>
                        </div>
                    </div>
                </div>
            );
        };


        const AddEditRuleModal = ({ isOpen, onClose, onSave, rule, hostName }) => {
            if (!isOpen) return null;

            const isEditMode = Boolean(rule);
            const [name, setName] = React.useState(rule?.name || '新规则');
            const [threshold, setThreshold] = React.useState(rule?.threshold || 80);
            const [metrics, setMetrics] = React.useState(rule?.metrics || [{ id: `m-${Date.now()}`, name: 'cpu_usage', currentValue: 50, weight: 0.5 }]);
            const [currentValue, setCurrentValue] = React.useState(rule?.currentValue || 0);

            React.useEffect(() => {
                const total = metrics.reduce((sum, metric) => sum + (metric.currentValue * metric.weight), 0);
                setCurrentValue(total);
            }, [metrics]);

            const handleMetricChange = (index, field, value) => {
                const newMetrics = [...metrics];
                // 允许修改 name, currentValue, 和 weight
                if (field === 'name') {
                    newMetrics[index][field] = value;
                } else {
                    newMetrics[index][field] = parseFloat(value) || 0;
                }
                setMetrics(newMetrics);
            };

            const handleAddMetric = () => {
                setMetrics([...metrics, { id: `m-${Date.now() + metrics.length}`, name: 'memory_usage', currentValue: 30, weight: 0.3 }]);
            };

            const handleRemoveMetric = (indexToRemove) => {
                setMetrics(metrics.filter((_, index) => index !== indexToRemove));
            };
            
            const handleSave = () => {
                if (!name.trim()) {
                    alert('规则名称不能为空！');
                    return;
                }
                onSave({ name, threshold, metrics, currentValue });
            };

            return (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50" onClick={onClose}>
                    <div className="bg-white rounded-lg shadow-xl w-full max-w-3xl" onClick={e => e.stopPropagation()}>
                        <div className="p-4 border-b flex justify-between items-center">
                            <h2 className="text-lg font-semibold">{isEditMode ? '编辑规则' : '新增规则'} (主机: {hostName})</h2>
                            <button onClick={onClose} className="text-gray-400 hover:text-gray-800 text-3xl font-light leading-none">×</button>
                        </div>
                        <div className="p-6 space-y-4 max-h-[60vh] overflow-y-auto">
                            <div className="grid grid-cols-3 gap-4 items-center">
                                <label className="text-sm font-medium text-gray-700">规则名称:</label>
                                <input type="text" value={name} onChange={e => setName(e.target.value)} className="col-span-2 w-full border rounded px-3 py-1.5 text-sm" />
                            </div>
                             <div className="grid grid-cols-3 gap-4 items-center">
                                <label className="text-sm font-medium text-gray-700">告警阈值:</label>
                                <input type="number" value={threshold} onChange={e => setThreshold(parseFloat(e.target.value) || 0)} className="col-span-2 w-full border rounded px-3 py-1.5 text-sm" />
                            </div>
                            <div className="border rounded-md">
                                <div className="p-2 border-b bg-gray-50 flex justify-between items-center">
                                    <h4 className="text-sm font-semibold">指标构成 (当前加权和: <span className={`font-bold ${currentValue > threshold ? 'text-red-500' : 'text-green-500'}`}>{currentValue.toFixed(2)}</span>)</h4>
                                    <button onClick={handleAddMetric} className="text-xs bg-gray-200 px-2 py-1 rounded hover:bg-gray-300">+ 添加指标</button>
                                </div>
                                <table className="w-full text-sm">
                                    <thead><tr className="text-left text-gray-600"><th className="p-2">指标名称</th><th className="p-2">当前值</th><th className="p-2">权重</th><th className="p-2">操作</th></tr></thead>
                                    <tbody>
                                        {metrics.map((metric, index) => (
                                            <tr key={metric.id} className="border-t">
                                                <td className="p-2"><input type="text" value={metric.name} onChange={e => handleMetricChange(index, 'name', e.target.value)} className="w-full border rounded px-2 py-1 text-sm"/></td>
                                                <td className="p-2"><input type="number" value={metric.currentValue} onChange={e => handleMetricChange(index, 'currentValue', e.target.value)} className="w-full border rounded px-2 py-1 text-sm"/></td>
                                                <td className="p-2"><input type="number" step="0.1" value={metric.weight} onChange={e => handleMetricChange(index, 'weight', e.target.value)} className="w-full border rounded px-2 py-1 text-sm"/></td>
                                                <td className="p-2"><button onClick={() => handleRemoveMetric(index)} className="text-red-500 hover:underline">移除</button></td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div className="flex justify-end items-center p-4 border-t bg-gray-50 space-x-2">
                            <button onClick={onClose} className="bg-white border text-gray-700 font-semibold py-1.5 px-6 rounded-md hover:bg-gray-100 text-sm">取消</button>
                            <button onClick={handleSave} className="bg-blue-500 text-white font-semibold py-1.5 px-6 rounded-md hover:bg-blue-600 text-sm">保存</button>
                        </div>
                    </div>
                </div>
            );
        };


        const CreateWorkflowModal = ({ app, isOpen, onClose, onCreate }) => {
            // ... (此组件代码无变化, 保持原样)
             if (!isOpen) return null;
            const [workflowName, setWorkflowName] = React.useState('');
            const [description, setDescription] = React.useState('');
            const [isRecommended, setIsRecommended] = React.useState(false);
            const [selectedGroupId, setSelectedGroupId] = React.useState('');
            const [allHosts, setAllHosts] = React.useState([]);
            const [hostGroups, setHostGroups] = React.useState([]);
            const [loading, setLoading] = React.useState(true);
            const [availableHosts, setAvailableHosts] = React.useState([]);
            const [selectedHosts, setSelectedHosts] = React.useState([]);
            const [checkedAvailable, setCheckedAvailable] = React.useState(new Set());
            const [checkedSelected, setCheckedSelected] = React.useState(new Set());
            React.useEffect(() => {
                const fetchData = async () => {
                    setLoading(true);
                    try {
                        const hostPromise = fetch('http://localhost:5000/api/hosts').then(res => res.json());
                        const groupPromise = fetch('http://localhost:5000/api/host-groups').then(res => res.json());
                        const [hostData, groupData] = await Promise.all([hostPromise, groupPromise]);
                        setAllHosts(hostData);
                        setHostGroups(groupData);
                        if (groupData.length > 0) {
                            setSelectedGroupId(groupData[0].name);
                        }
                    } catch (error) {
                        console.error("弹窗加载数据失败:", error);
                    } finally {
                        setLoading(false);
                    }
                };
                fetchData();
            }, []);
            React.useEffect(() => {
                if (!selectedGroupId) { setAvailableHosts([]); return; }
                const selectedHostIds = new Set(selectedHosts.map(h => h.id));
                const filtered = allHosts.filter(host => host.group === selectedGroupId && !selectedHostIds.has(host.id));
                setAvailableHosts(filtered);
            }, [selectedGroupId, allHosts, selectedHosts]);
            const handleToggleCheck = (host, listType) => {
                const [checked, setChecked] = listType === 'available' ? [checkedAvailable, setCheckedAvailable] : [checkedSelected, setCheckedSelected];
                const newChecked = new Set(checked);
                if (newChecked.has(host.id)) { newChecked.delete(host.id); } else { newChecked.add(host.id); }
                setChecked(newChecked);
            };
            const handleToggleCheckAll = (listType) => {
                const [hosts, checked, setChecked] = listType === 'available' ? [availableHosts, checkedAvailable, setCheckedAvailable] : [selectedHosts, checkedSelected, setCheckedSelected];
                const allIds = new Set(hosts.map(h => h.id));
                const isAllChecked = hosts.length > 0 && checked.size === hosts.length;
                if (isAllChecked) { setChecked(new Set()); } else { setChecked(allIds); }
            };
            const moveCheckedRight = () => {
                const hostsToMove = availableHosts.filter(h => checkedAvailable.has(h.id));
                setSelectedHosts(prev => [...prev, ...hostsToMove]);
                setCheckedAvailable(new Set());
            };
            const moveCheckedLeft = () => {
                const hostsToKeep = selectedHosts.filter(h => !checkedSelected.has(h.id));
                setSelectedHosts(hostsToKeep);
                setCheckedSelected(new Set());
            };
            const handleCreateClick = () => {
                if (!workflowName.trim()) { alert('请输入工作流名称。'); return; }
                const newWorkflowData = { appName: app.name, workflowName, description, isRecommended, hostGroupId: selectedGroupId, hostIds: selectedHosts.map(h => h.id) };
                console.log("正在创建工作流，数据如下:", newWorkflowData);
                alert(`工作流 "${workflowName}" 创建成功（模拟）！`);
                onCreate(newWorkflowData);
            };
            const ToggleSwitch = ({ checked, onChange }) => ( <button type="button" onClick={() => onChange(!checked)} className={`${checked ? 'bg-blue-500' : 'bg-gray-200'} relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none`} role="switch" aria-checked={checked}><span className={`${checked ? 'translate-x-5' : 'translate-x-0'} pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out`}></span></button> );
            const HostList = ({ title, hosts, checked, onToggleCheck, onToggleAll }) => {
                const isAllChecked = hosts.length > 0 && checked.size === hosts.length;
                return (
                     <div className="flex-1 border rounded-md flex flex-col bg-white">
                        <div className="p-2 border-b text-sm font-semibold bg-gray-50 flex justify-between items-center"><span>{title}</span><span className="text-gray-500 font-normal">{hosts.length} 项</span></div>
                        <div className="p-2 border-b"><input type="text" placeholder="搜索主机名" className="w-full border rounded px-2 py-1 text-sm"/></div>
                        <div className="p-2 text-sm text-gray-600"><label className="flex items-center space-x-2 px-1 cursor-pointer"><input type="checkbox" className="rounded-sm" disabled={hosts.length === 0} checked={isAllChecked} onChange={onToggleAll} /><span>主机名称</span></label></div>
                        <div className="flex-1 overflow-y-auto p-2 space-y-1">
                            {hosts.length === 0 ? (<div className="text-center text-gray-400 pt-10 text-sm">暂无数据</div>) : hosts.map(host => (<label key={host.id} className="flex items-center space-x-2 p-1 rounded hover:bg-blue-50 cursor-pointer"><input type="checkbox" className="rounded-sm" checked={checked.has(host.id)} onChange={() => onToggleCheck(host)} /><span className="text-sm">{host.name}</span></label>))}
                        </div>
                    </div>
                );
            };
            return (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-end z-50" onClick={onClose}>
                    <div className="bg-gray-100 h-full w-full max-w-3xl shadow-xl flex flex-col" onClick={e => e.stopPropagation()}>
                        <div className="flex-shrink-0 p-4 border-b bg-white flex justify-between items-center"><h2 className="text-lg font-semibold">创建工作流</h2><button onClick={onClose} className="text-gray-500 hover:text-gray-800 text-3xl font-light">×</button></div>
                        <div className="flex-1 p-6 space-y-4 overflow-y-auto">
                            <div className="flex items-center bg-white p-4 rounded-md border"><label className="w-28 text-sm text-gray-600">应用名称:</label><span className="text-sm font-medium text-gray-800">{app.name}</span><label className="w-28 text-sm text-gray-600 ml-auto text-right pr-4">是否推荐:</label><ToggleSwitch checked={isRecommended} onChange={setIsRecommended} /></div>
                            <div className="bg-white p-4 rounded-md border"><label className="block text-sm text-gray-600 mb-2">工作流名称:</label><input type="text" value={workflowName} onChange={e => setWorkflowName(e.target.value)} className="w-full border rounded px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-400 text-sm"/></div>
                            <div className="bg-white p-4 rounded-md border"><label className="block text-sm text-gray-600 mb-2">工作流描述:</label><textarea value={description} onChange={e => setDescription(e.target.value)} rows="2" className="w-full border rounded px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-400 text-sm resize-none"></textarea></div>
                            <div className="bg-white p-4 rounded-md border"><label className="block text-sm text-gray-600 mb-2">主机组:</label><select value={selectedGroupId} onChange={e => setSelectedGroupId(e.target.value)} className="w-full bg-white border rounded px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-400 text-sm">{loading ? <option>加载中...</option> : hostGroups.map(group => <option key={group.id} value={group.name}>{group.name}</option>)}</select></div>
                            <div className="bg-white p-4 rounded-md border">
                                <label className="text-sm text-gray-600 mb-2 block">主机:</label>
                                <div className="flex items-stretch space-x-4 h-72">
                                    <HostList title="待选主机" hosts={availableHosts} checked={checkedAvailable} onToggleCheck={(host) => handleToggleCheck(host, 'available')} onToggleAll={() => handleToggleCheckAll('available')} />
                                    <div className="flex flex-col justify-center space-y-2"><button onClick={moveCheckedRight} disabled={checkedAvailable.size === 0} className="border p-2 rounded-md hover:bg-gray-100 disabled:opacity-50">&lt;</button>
                                        <button onClick={moveCheckedLeft} disabled={checkedSelected.size === 0} className="border p-2 rounded-md hover:bg-gray-100 disabled:opacity-50">&gt;</button></div>
                                    <HostList title="已选主机" hosts={selectedHosts} checked={checkedSelected} onToggleCheck={(host) => handleToggleCheck(host, 'selected')} onToggleAll={() => handleToggleCheckAll('selected')} />
                                 </div>
                            </div>
                        </div>
                        <div className="flex-shrink-0 p-4 border-t bg-white flex justify-end space-x-3"><button onClick={onClose} className="px-6 py-2 border rounded-md text-sm hover:bg-gray-100">关闭</button><button onClick={handleCreateClick} className="px-6 py-2 bg-blue-500 text-white rounded-md text-sm hover:bg-blue-600">创建</button></div>
                    </div>
                </div>
            );
        };
        
        const ApplicationDetailPage = ({ appId, onBack, onWorkflowCreate }) => {
            
            const [app, setApp] = React.useState(null);
            const [isLoading, setIsLoading] = React.useState(true);
            const [error, setError] = React.useState(null);
            const [isModalOpen, setIsModalOpen] = React.useState(false);
            const handleOpenCreateModal = () => { setIsModalOpen(true); };
            const handleCloseCreateModal = () => { setIsModalOpen(false); };
            const handleWorkflowCreated = (newWorkflowData) => { if (onWorkflowCreate) { onWorkflowCreate(newWorkflowData); } handleCloseCreateModal(); };
            React.useEffect(() => {
                const fetchAppDetail = async () => {
                    setIsLoading(true);
                    setError(null);
                    try {
                        const response = await fetch(`http://localhost:5000/api/applications/${appId}`);
                        if (!response.ok) { throw new Error(`无法加载应用数据 (ID: ${appId})，请检查后端文件是否存在。`); }
                        const data = await response.json();
                        setApp(data);
                    } catch (err) {
                        console.error("获取应用详情失败:", err);
                        setError(err.message);
                    } finally { setIsLoading(false); }
                };
                fetchAppDetail();
            }, [appId]);
            const FlowStep = ({ name, isLast = false }) => ( <div className="flex items-center"><div className="bg-white border-2 border-gray-300 rounded-md shadow-sm px-8 py-3 text-center"><span className="text-gray-800 font-semibold">{name}</span></div>{!isLast && (<div className="w-16 h-px bg-gray-400 mx-4 relative"><div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 border-t-2 border-r-2 border-gray-400 transform rotate-45"></div></div>)}</div> );
            if (isLoading) return <div className="p-8 text-center text-gray-500">正在加载应用详情...</div>;
            if (error) return ( <div className="p-8 text-center"><h3 className="text-lg font-semibold text-red-600">加载失败</h3><p className="text-red-500 mt-2">{error.message}</p></div> );
            if (!app) return <div className="p-8 text-center text-gray-500">未找到应用数据。</div>;
            return (
                <React.Fragment>
                <div className="space-y-6">
                    <div className="text-sm text-gray-500"><a href="#" onClick={(e) => { e.preventDefault(); onBack(); }} className="text-blue-600 hover:underline">应用</a><span className="mx-2">/</span><span className="text-gray-800">{app.name}</span></div>
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <div className="flex justify-between items-center">
                            <div className="flex items-center">
                               <div className="w-12 h-12 flex items-center justify-center rounded-lg bg-blue-100 mr-4"><svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5"><path strokeLinecap="round" strokeLinejoin="round" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg></div>
                               <div><h1 className="text-xl font-bold text-gray-800">{app.name}</h1><p className="mt-1 text-sm text-gray-500">描述：{app.description}</p></div>
                            </div>
                            <button onClick={handleOpenCreateModal} className="bg-blue-500 text-white font-semibold py-2 px-4 rounded-md hover:bg-blue-600 transition text-sm flex items-center">创建工作流</button>
                        </div>
                    </div>
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <div className="flex items-center justify-between mb-6"><h2 className="text-lg font-semibold">应用流程</h2><div></div></div>
                        <div className="flex items-center justify-center p-8 bg-gray-50 rounded-lg">{app.flow && app.flow.map((step, index) => ( <FlowStep key={step.id} name={step.name} isLast={index === app.flow.length - 1} /> ))}</div>
                    </div>
                </div>
                {app && ( <CreateWorkflowModal app={app} isOpen={isModalOpen} onClose={handleCloseCreateModal} onCreate={handleAddNewWorkflow} /> )}
                </React.Fragment>
            );
        };

        const WorkflowListPage = ({ workflows, applications, onOpenAddAppModal, workflowLoading, appLoading, paginatedWorkflows, paginatedApps, onNavigateToDetail, onNavigateToAppDetail, fetchWorkflows, fetchApplications, onUpdateStatus, onDelete, onToggleRecommend, ...props }) => {
            // ... (此组件代码无变化, 保持原样)
            const handleActionClick = (action, workflow) => {
                switch(action) {
                    case '执行': 
                        onUpdateStatus(workflow.id, '运行中'); 
                        // alert(`工作流 "${workflow.name}" 已开始执行（模拟）。`); 
                        break;
                    case '暂停': 
                        onUpdateStatus(workflow.id, '已暂停'); 
                        // alert(`工作流 "${workflow.name}" 已暂停（模拟）。`); 
                        break;
                    case '删除': 
                        //if (window.confirm(`您确定要删除工作流 "${workflow.name}" 吗？`)) { onDelete(workflow.id); } 
                        onDelete(workflow.id);
                        break;
                    case '推荐': onToggleRecommend(workflow.id); break;
                    default: break;
                }
            };
            const FilterIcon = () => <svg className="w-3 h-3 text-gray-400" fill="currentColor" viewBox="0 0 20 20"><path d="M3 3a1 1 0 011-1h12a1 1 0 011 1v3a1 1 0 01-.293.707L12 12.414V17a1 1 0 01-1.447.894l-2-1A1 1 0 018 16v-3.586L3.293 6.707A1 1 0 013 6V3z"></path></svg>;
            const getStatusPill = (status) => {
                const baseClass = "flex items-center space-x-1.5";
                switch(status) {
                    case '运行中': return <span className={baseClass}><span className="h-2 w-2 rounded-full bg-green-500"></span><span>运行中</span></span>;
                    case '已暂停': return <span className={baseClass}><span className="h-2 w-2 rounded-full bg-yellow-500"></span><span>已暂停</span></span>;
                    case '失败': return <span className={baseClass}><span className="h-2 w-2 rounded-full bg-red-500"></span><span>失败</span></span>;
                    default: return <span className={baseClass}><span className="h-2 w-2 rounded-full bg-gray-400"></span><span>{status}</span></span>;
                }
            };
            const LoadingRow = ({ colSpan }) => <tr><td colSpan={colSpan} className="text-center p-8 text-gray-500">加载中...</td></tr>;
            const EmptyRow = ({ colSpan }) => <tr><td colSpan={colSpan} className="text-center p-8 text-gray-500">无信息</td></tr>;
            return (
                <div className="space-y-6">
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <div className="flex justify-between items-center mb-4">
                            <div><h2 className="text-lg font-semibold">工作流</h2><p className="text-sm text-gray-500 mt-1">共获取到 {workflows.length} 条工作流信息</p></div>
                            <button onClick={fetchWorkflows} className="bg-blue-500 text-white font-semibold py-1.5 px-4 rounded-md hover:bg-blue-600 transition text-sm">刷新</button>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead className="bg-gray-50 border-b"><tr className="text-left text-gray-600">{['名称', '描述', '主机组', '应用', '状态', '操作'].map(header => ( <th key={header} className="py-2 px-3 font-semibold"><div className="flex items-center space-x-1"><span>{header}</span> <FilterIcon/></div></th> ))}</tr></thead>
                                <tbody>
                                    {workflowLoading ? <LoadingRow colSpan={6} /> : paginatedWorkflows.length === 0 ? <EmptyRow colSpan={6} /> : paginatedWorkflows.map(wf => (
                                        <tr key={wf.id} className="border-b hover:bg-blue-50/50">
                                            <td className="py-3 px-3"><a href="#" onClick={(e) => { e.preventDefault(); onNavigateToDetail(wf.id); }} className="text-blue-600 hover:underline">{wf.name}</a></td>
                                            <td className="py-3 px-3 text-gray-700">{wf.description}</td><td className="py-3 px-3 text-gray-700">{wf.hostGroup}</td><td className="py-3 px-3 text-gray-700">{wf.application}</td><td className="py-3 px-3 text-gray-700">{getStatusPill(wf.status)}</td>
                                            <td className="py-3 px-3 space-x-3 text-blue-600">
                                                <button onClick={() => handleActionClick('执行', wf)} disabled={wf.status === '运行中'} className="hover:underline disabled:text-gray-400 disabled:cursor-not-allowed">执行</button>
                                                <button onClick={() => handleActionClick('暂停', wf)} disabled={wf.status !== '运行中'} className="hover:underline disabled:text-gray-400 disabled:cursor-not-allowed">暂停</button>
                                                <button onClick={() => handleActionClick('删除', wf)} className="hover:underline">删除</button>
                                                <button onClick={() => handleActionClick('推荐', wf)} className="hover:underline">{wf.isRecommended ? '已推荐' : '推荐'}</button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        {workflows.length > 0 && <div className="pt-4"><Pagination currentPage={props.workflowCurrentPage} totalItems={workflows.length} pageSize={props.workflowPageSize} onPageChange={props.handleWorkflowPageChange} onPageSizeChange={props.handleWorkflowPageSizeChange} options={[10, 20, 50]}/></div>}
                    </div>
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <div className="flex justify-between items-center mb-4">
                            <div><h2 className="text-xl font-bold text-gray-800">应用</h2><p className="text-sm text-gray-500 mt-1">共获取到 {applications.length} 个应用信息</p></div>
                            <button onClick={fetchApplications} className="bg-blue-500 text-white font-semibold py-1.5 px-4 rounded-md hover:bg-blue-600 transition text-sm">刷新</button>
                        </div>
                        {appLoading ? <div className="text-center p-8 text-gray-500">加载中...</div> : 
                            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-5">
                                <div onClick={onOpenAddAppModal} className="border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center text-gray-500 h-44 cursor-pointer hover:border-blue-500 hover:text-blue-500 transition"><span className="text-5xl font-thin">+</span><span className="mt-1">新增应用</span></div>
                                {paginatedApps.map(app => (
                                    <a key={app.id} href="#" onClick={(e) => { e.preventDefault(); onNavigateToAppDetail(app.id); }} className="block border border-gray-200 rounded-lg p-4 h-44 hover:shadow-md hover:border-blue-400 transition-all duration-200">
                                        <div className="flex flex-col h-full">
                                            <div className="flex justify-between items-start">
                                                <div className="w-10 h-10 flex items-center justify-center rounded-lg bg-blue-100"><svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5"><path strokeLinecap="round" strokeLinejoin="round" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg></div>
                                                <p className="text-xs text-gray-400">描述:</p>
                                            </div>
                                            <p className="text-sm text-gray-600 mt-2 flex-grow">{app.description}</p>
                                            <div className="border-t pt-2 mt-2"><p className="text-sm font-semibold text-gray-800 truncate">应用名: {app.name}</p><p className="text-xs text-gray-500">版本号: {app.version}</p></div>
                                        </div>
                                    </a>
                                ))}
                            </div>
                        }
                        {applications.length > 0 && <div className="pt-4"><Pagination currentPage={props.appCurrentPage} totalItems={applications.length} pageSize={props.appPageSize} onPageChange={props.handleAppPageChange} onPageSizeChange={props.handleAppPageSizeChange} options={[4, 8, 12]}/></div>}
                    </div>
                </div>
            );
        };

        // -----------------------------------------------------------------
        // 渲染逻辑 (Render Logic)
        // -----------------------------------------------------------------
        if (view.page === 'app_detail') {
            return <ApplicationDetailPage 
                        appId={view.param} 
                        onBack={handleNavigateToList}
                        onWorkflowCreate={handleAddNewWorkflow} 
                    />;
        }        
        if (view.page === 'detail') {
            const currentWorkflow = workflows.find(wf => wf.id === view.param);
            if (!currentWorkflow) {
                // 如果工作流被删除，则不渲染详情页，避免错误
                return null; 
            }
            
            return <WorkflowDetailPage 
                        workflowId={view.param}
                        sharedStatus={currentWorkflow.status}
                        onUpdateStatus={handleUpdateWorkflowStatus}
                        onBack={handleNavigateToList} 
                        onDelete={handleDeleteWorkflow}
                   />;
        }
        
        // 默认渲染列表页
        return (
            <React.Fragment> 
                {/* 根据 view.page 的值来决定渲染哪个主页面 */}
                {view.page === 'app_detail' && (
                    <ApplicationDetailPage 
                        appId={view.param} 
                        onBack={handleNavigateToList}
                        onWorkflowCreate={handleAddNewWorkflow} 
                    />
                )}
                {view.page === 'detail' && (() => {
                    const currentWorkflow = workflows.find(wf => wf.id === view.param);
                    if (!currentWorkflow) return null;
                    return (
                        <WorkflowDetailPage 
                            workflowId={view.param}
                            sharedStatus={currentWorkflow.status}
                            onUpdateStatus={handleUpdateWorkflowStatus}
                            onBack={handleNavigateToList} 
                            onDelete={handleDeleteWorkflow}
                        />
                    );
                })()}
                {view.page === 'list' && (
                    <WorkflowListPage
                        workflows={workflows}
                        applications={applications}
                        workflowLoading={workflowLoading}
                        appLoading={appLoading}
                        paginatedWorkflows={paginatedWorkflows}
                        paginatedApps={paginatedApps}
                        onNavigateToDetail={handleNavigateToDetail}
                        onNavigateToAppDetail={handleNavigateToAppDetail}
                        fetchWorkflows={fetchWorkflows}
                        fetchApplications={fetchApplications}
                        onUpdateStatus={handleUpdateWorkflowStatus}
                        onDelete={handleDeleteWorkflow}
                        onToggleRecommend={handleToggleRecommend}
                        workflowCurrentPage={workflowCurrentPage}
                        workflowPageSize={workflowPageSize}
                        appCurrentPage={appCurrentPage}
                        appPageSize={appPageSize}
                        handleWorkflowPageChange={handleWorkflowPageChange}
                        handleWorkflowPageSizeChange={handleWorkflowPageSizeChange}
                        handleAppPageChange={handleAppPageChange}
                        handleAppPageSizeChange={handleAppPageSizeChange}
                        onOpenAddAppModal={handleOpenAddAppModal}
                    />
                )}

                {/* 在这里统一渲染所有的弹窗组件 */}
                <AddApplicationModal 
                    isOpen={isAddAppModalOpen} 
                    onClose={handleCloseAddAppModal} 
                    onSave={handleSaveNewApp} 
                />
            </React.Fragment>
        );
    };
    //工作流页面组件结束 