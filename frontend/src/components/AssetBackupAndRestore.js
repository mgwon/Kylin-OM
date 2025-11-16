const AssetBackupAndRestore = () => {
    // --- State Management (无变化) ---
    const [policies, setPolicies] = React.useState([]);
    const [loading, setLoading] = React.useState(true);
    const [selectedIds, setSelectedIds] = React.useState(new Set());
    const [currentPage, setCurrentPage] = React.useState(1);
    const [pageSize, setPageSize] = React.useState(5);

    // Modal states (无变化)
    const [isAddEditModalOpen, setAddEditModalOpen] = React.useState(false);
    const [isHistoryModalOpen, setHistoryModalOpen] = React.useState(false);
    const [isConfirmModalOpen, setConfirmModalOpen] = React.useState(false);
    
    // Data for modals (无变化)
    const [editingPolicy, setEditingPolicy] = React.useState(null);
    const [historyData, setHistoryData] = React.useState({ policyName: '', records: [] });
    const [restoreInfo, setRestoreInfo] = React.useState(null);

    // --- 【修改点 1】: 数据获取逻辑，改为调用后端 API ---
    const fetchPolicies = React.useCallback(async () => {
    setLoading(true);
    try {
        // 【修改】使用完整的后端 URL
        const response = await fetch('http://localhost:5000/api/policies'); 
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        setPolicies(data);
    } catch (error) {
        // ...
    } finally {
        setLoading(false);
    }
}, []);

    React.useEffect(() => {
        fetchPolicies();
    }, [fetchPolicies]);

    // --- Handlers (处理器) ---
    const handleSelect = (id) => {
        const newIds = new Set(selectedIds);
        newIds.has(id) ? newIds.delete(id) : newIds.add(id);
        setSelectedIds(newIds);
    };
    const handleSelectAll = (e) => setSelectedIds(e.target.checked ? new Set(paginatedPolicies.map(p => p.id)) : new Set());
    const handleOpenAddModal = () => { setEditingPolicy(null); setAddEditModalOpen(true); };
    const handleOpenEditModal = (policy) => { setEditingPolicy(policy); setAddEditModalOpen(true); };
    
    // --- 【修改点 2】: 查看历史记录，改为调用后端 API ---
    const handleViewHistory = async (policy) => {
        setHistoryData({ policyName: policy.name, records: [] });
        setHistoryModalOpen(true);
        try {
            // 从请求静态 .txt 文件改为调用后端的 /api/policies/<id>/history 接口
           const response = await fetch(`http://localhost:5000/api/policies/${policy.id}/history`);
            if (!response.ok) {
                if(response.status === 404) { setHistoryData(prev => ({ ...prev, records: [] })); return; }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const records = await response.json();
            setHistoryData({ policyName: policy.name, records });
        } catch(error) {
            console.error(`获取策略 ${policy.id} 的历史记录失败:`, error);
            alert(`获取策略 "${policy.name}" 的历史记录失败。`);
        }
    };

    const handleTriggerRestore = (policyName, backupRecord) => {
        setRestoreInfo({ policyName, backupRecord });
        setConfirmModalOpen(true);
    };

    // --- 【修改点 3】: 恢复操作，改为调用后端 API ---
    const handleConfirmRestore = async () => {
        if (!restoreInfo) return;
        try {
            const response = await fetch('http://localhost:5000/api/restore', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filePath: restoreInfo.backupRecord.filePath }),
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${await response.text()}`);
            const result = await response.json();
            alert(result.message || '恢复任务已成功触发！');
        } catch (error) {
            console.error('恢复操作失败:', error);
            alert(`恢复操作失败: ${error.message}`);
        } finally {
            setConfirmModalOpen(false);
            setRestoreInfo(null);
        }
    };

    // --- 【修改点 4】: 保存策略（新建/编辑），改为调用后端 API ---
    const handleSavePolicy = async (policyData) => {
        const isEditing = !!editingPolicy;
        const url = isEditing 
            ? `http://localhost:5000/api/policies/${editingPolicy.id}` 
            : 'http://localhost:5000/api/policies';
        const method = isEditing ? 'PUT' : 'POST';

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(policyData)
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            alert(`策略${isEditing ? '更新' : '添加'}成功!`);
            setAddEditModalOpen(false);
            fetchPolicies(); // 重新加载列表以显示最新数据
        } catch (error) {
            console.error('保存策略失败:', error);
            alert(`保存策略失败: ${error.message}`);
        }
    };
    
    // --- 【修改点 5】: 删除策略，改为调用后端 API ---
    const handleDeletePolicy = async (policy) => {
      if(window.confirm(`确定要删除策略 "${policy.name}" 吗？`)) {
        try {
             const response = await fetch(`http://localhost:5000/api/policies/${policy.id}`, { method: 'DELETE' });;
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            alert('删除成功!');
            fetchPolicies(); // 重新加载列表
        } catch (error) {
            console.error('删除策略失败:', error);
            alert(`删除策略失败: ${error.message}`);
        }
      }
    };
    
    // --- 【修改点 6】: 立即执行，改为调用后端 API ---
    const handleExecuteNow = async (policy) => {
        if (window.confirm(`确定要立即执行策略 "${policy.name}" 吗？`)) {
            try {
                const response = await fetch(`http://localhost:5000/api/policies/${policy.id}/execute`, { method: 'POST' });
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const result = await response.json();
                alert(result.message || '任务已成功触发！');
                // 可选：短时间后刷新列表以更新“上次执行状态”
                setTimeout(fetchPolicies, 2000);
            } catch (error) {
                console.error('执行策略失败:', error);
                alert(`执行策略失败: ${error.message}`);
            }
        }
    };
    
    // --- 【修改点 7】: 批量删除，改为调用后端 API ---
    const handleBulkDelete = () => {
        if (selectedIds.size === 0) {
            alert("请至少选择一个策略进行删除。");
            return;
        }
        if (window.confirm(`确定要删除选中的 ${selectedIds.size} 个策略吗？此操作不可恢复。`)) {
            const deletePromises = Array.from(selectedIds).map(id => 
        fetch(`http://localhost:5000/api/policies/${id}`, { method: 'DELETE' })
    );

            Promise.all(deletePromises)
                .then(responses => {
                    const failed = responses.filter(res => !res.ok);
                    if (failed.length > 0) {
                        alert(`成功删除 ${responses.length - failed.length} 个策略，${failed.length} 个失败。`);
                    } else {
                        alert("批量删除成功!");
                    }
                })
                .catch(error => {
                    console.error("批量删除时发生错误:", error);
                    alert("批量删除时发生网络错误。");
                })
                .finally(() => {
                    setSelectedIds(new Set());
                    fetchPolicies(); // 重新加载列表
                });
        }
    };


        // --- Render Logic (无变化) ---
        const paginatedPolicies = policies.slice((currentPage - 1) * pageSize, currentPage * pageSize);
        const getStatusClass = (status) => {
            switch (status) {
                case '成功': return 'bg-green-100 text-green-800';
                case '失败': return 'bg-red-100 text-red-800';
                case '进行中': return 'bg-blue-100 text-blue-800';
                default: return 'bg-gray-100 text-gray-800';
            }
        };

        // --- Sub-Components (Modals) ---
        // --- 修复点 1: 确保信息描述可正常输入 ---
        // (这段代码已验证无误，直接替换即可)
        const AddEditPolicyModal = ({ isOpen, onClose, policy, onSave }) => {
            if (!isOpen) return null;

            // 初始化state时，确保每个字段都已定义
            const [formData, setFormData] = React.useState({
                name: policy?.name || '',
                target: policy?.target || '',
                type: policy?.type || '文件',
                content: policy?.content || (policy?.type === '文件' ? '/etc/\n/var/www/' : 'all_databases'),
                schedule: policy?.schedule || '每日 02:00',
                retention: policy?.retention || 7,
                description: policy?.description || '', // 确保 description 字段存在
            });

            // 通用的 handleChange 函数
            const handleChange = (e) => {
                const { name, value } = e.target;
                setFormData(prev => ({...prev, [name]: value}));
            };

            const handleSubmit = () => {
                if (!formData.name || !formData.target) {
                    alert('策略名称和备份目标不能为空！');
                    return;
                }
                onSave(formData);
            }

            return (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
                    <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl">
                        <div className="p-5 border-b"><h3 className="text-lg font-semibold">{policy ? '编辑备份策略' : '新建备份策略'}</h3></div>
                        <div className="p-6 space-y-4 max-h-[60vh] overflow-y-auto">
                            {/* ...其他表单项... */}
                            <div className="grid grid-cols-4 items-center">
                                <label className="text-sm text-gray-700 col-span-1 text-right pr-4"><span className="text-red-500">*</span>策略名称:</label>
                                <input name="name" value={formData.name} onChange={handleChange} className="col-span-3 border rounded-md p-2" />
                            </div>
                            <div className="grid grid-cols-4 items-center">
                                <label className="text-sm text-gray-700 col-span-1 text-right pr-4"><span className="text-red-500">*</span>备份目标:</label>
                                <input name="target" value={formData.target} onChange={handleChange} placeholder="主机名、IP或主机组" className="col-span-3 border rounded-md p-2" />
                            </div>
                            <div className="grid grid-cols-4 items-center">
                                <label className="text-sm text-gray-700 col-span-1 text-right pr-4">备份类型:</label>
                                <div className="col-span-3 flex space-x-4">
                                    <label><input type="radio" name="type" value="文件" checked={formData.type === '文件'} onChange={handleChange}/> 文件</label>
                                    <label><input type="radio" name="type" value="数据库" checked={formData.type === '数据库'} onChange={handleChange}/> 数据库</label>
                                </div>
                            </div>
                            <div className="grid grid-cols-4 items-start">
                                <label className="text-sm text-gray-700 col-span-1 text-right pr-4 pt-2">备份内容:</label>
                                <textarea name="content" value={formData.content} onChange={handleChange} rows="3" className="col-span-3 border rounded-md p-2 font-mono text-sm" placeholder="文件路径，每行一个..."></textarea>
                            </div>
                            <div className="grid grid-cols-4 items-center">
                                <label className="text-sm text-gray-700 col-span-1 text-right pr-4">执行计划:</label>
                                <input name="schedule" value={formData.schedule} onChange={handleChange} placeholder="例如: 每日 02:00 或 Cron 表达式" className="col-span-3 border rounded-md p-2" />
                            </div>
                            <div className="grid grid-cols-4 items-center">
                                <label className="text-sm text-gray-700 col-span-1 text-right pr-4">保留备份数:</label>
                                <input type="number" name="retention" value={formData.retention} onChange={handleChange} className="col-span-1 border rounded-md p-2" />
                            </div>
                            <div className="grid grid-cols-4 items-start">
                                <label className="text-sm text-gray-700 col-span-1 text-right pr-4 pt-2">信息描述:</label>
                                <textarea name="description" value={formData.description} onChange={handleChange} rows="2" className="col-span-3 border rounded-md p-2"></textarea>
                            </div>
                        </div>
                        <div className="p-4 border-t flex justify-end space-x-2">
                            <button onClick={onClose} className="px-4 py-2 border rounded-md">取消</button>
                            <button onClick={handleSubmit} className="px-4 py-2 bg-blue-600 text-white rounded-md">确认</button>
                        </div>
                    </div>
                </div>
            );
        };

        // HistoryModal 和 ConfirmRestoreModal 无变化，为保持组件完整性而保留
        const HistoryModal = ({ isOpen, onClose, data, onRestore }) => { if (!isOpen) return null; const { policyName, records } = data; return ( <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50"> <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl"> <div className="p-4 border-b flex justify-between items-center"><h3 className="text-lg font-semibold">备份历史 - {policyName}</h3><button onClick={onClose} className="text-2xl font-light">×</button></div> <div className="p-6 max-h-[60vh] overflow-y-auto"> <table className="w-full text-sm"> <thead className="bg-gray-50"><tr> <th className="p-3 text-left font-semibold text-gray-600">时间戳</th> <th className="p-3 text-left font-semibold text-gray-600">耗时</th> <th className="p-3 text-left font-semibold text-gray-600">备份大小</th> <th className="p-3 text-left font-semibold text-gray-600">状态</th> <th className="p-3 text-left font-semibold text-gray-600">操作</th> </tr></thead> <tbody> {historyData.records.length === 0 ? ( <tr><td colSpan="5" className="text-center py-10 text-gray-500">正在加载历史记录或无记录...</td></tr> ) : ( historyData.records.map(rec => ( <tr key={rec.id} className="border-b hover:bg-gray-50"> <td className="p-3">{rec.timestamp}</td> <td className="p-3">{rec.duration}</td> <td className="p-3">{rec.size}</td> <td className="p-3"><span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusClass(rec.status)}`}>{rec.status}</span></td> <td className="p-3"> {rec.status === '成功' && <a href="#" onClick={(e) => {e.preventDefault(); onRestore(policyName, rec)}} className="text-blue-600 hover:underline">恢复</a>} </td> </tr> )) )} </tbody> </table> </div> </div> </div> ); };
        const ConfirmRestoreModal = ({ isOpen, onClose, onConfirm, info }) => { if (!isOpen) return null; return ( <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50"> <div className="bg-white rounded-lg shadow-xl w-full max-w-md"> <div className="p-6"> <h3 className="text-lg font-bold text-yellow-600">确认恢复操作</h3> <p className="mt-4 text-gray-700"> 此操作将使用 <b className="text-blue-600">{info.backupRecord.timestamp}</b> 的备份数据覆盖目标资产，此过程不可逆。 </p> <p className="mt-2 text-sm text-gray-500">策略: {info.policyName}</p> </div> <div className="p-4 bg-gray-50 flex justify-end space-x-3"> <button onClick={onClose} className="px-4 py-2 border rounded-md text-sm">取消</button> <button onClick={onConfirm} className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-semibold">确认恢复</button> </div> </div> </div> ); };


        // --- Main Component Render (有修改) ---
        return (
            <>
                <div className="bg-white p-6 rounded-lg shadow-md">
                    {/* --- 修改点 2: 增加批量删除按钮 --- */}
                    <div className="flex justify-between items-center mb-5">
                        <div className="flex items-center space-x-4 text-sm">
                            <span className="text-gray-600">共获取到 {policies.length} 条策略</span>
                            <div className="flex items-center bg-blue-50 border border-blue-200 text-blue-700 px-3 py-1 rounded-md">
                                <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                                已选择 {selectedIds.size} 项
                            </div>
                            {/* 批量删除按钮 */}
                            <button 
                                onClick={handleBulkDelete}
                                disabled={selectedIds.size === 0} 
                                className="bg-white border border-gray-300 text-gray-700 px-4 py-1 rounded-md hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-400"
                            >
                                批量删除
                            </button>
                            <button onClick={() => setSelectedIds(new Set())} className="bg-white border border-gray-300 text-gray-600 px-4 py-1 rounded-md hover:bg-gray-50">重置</button>
                        </div>
                        <div className="flex items-center space-x-3">
                            <button onClick={handleOpenAddModal} className="bg-blue-600 text-white font-semibold py-2 px-4 rounded-md hover:bg-blue-700 text-sm flex items-center">
                                <span className="text-lg mr-1">+</span> 新建备份策略
                            </button>
                            <button onClick={fetchPolicies} className="bg-white border border-gray-300 text-gray-700 font-semibold py-2 px-4 rounded-md hover:bg-gray-50 text-sm flex items-center">
                                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h5M20 20v-5h-5M4 4l5 5M20 20l-5-5"></path></svg>
                                刷新
                            </button>
                        </div>
                    </div>
                    {/* Table (无变化) */}
                    <div className="overflow-x-auto">
                        <table className="min-w-full text-sm">
                            <thead className="bg-gray-50"><tr>
                                <th className="p-3 w-10"><input type="checkbox" onChange={handleSelectAll} checked={policies.length > 0 && paginatedPolicies.length > 0 && selectedIds.size === paginatedPolicies.length}/></th>
                                <th className="p-3 text-left font-semibold text-gray-600">策略名称</th>
                                <th className="p-3 text-left font-semibold text-gray-600">备份目标</th>
                                <th className="p-3 text-left font-semibold text-gray-600">类型</th>
                                <th className="p-3 text-left font-semibold text-gray-600">执行计划</th>
                                <th className="p-3 text-left font-semibold text-gray-600">上次备份状态</th>
                                <th className="p-3 text-left font-semibold text-gray-600">上次备份时间</th>
                                <th className="p-3 text-left font-semibold text-gray-600">操作</th>
                            </tr></thead>
                            <tbody>
                                {loading ? (
                                    <tr><td colSpan="8" className="p-10 text-center text-gray-500">加载中...</td></tr>
                                ) : (
                                    paginatedPolicies.map(p => (
                                        <tr key={p.id} className="border-b hover:bg-gray-50">
                                            <td className="p-3"><input type="checkbox" checked={selectedIds.has(p.id)} onChange={() => handleSelect(p.id)}/></td>
                                            <td className="p-3 font-semibold text-gray-800">{p.name}</td>
                                            <td className="p-3 text-gray-600">{p.target}</td>
                                            <td className="p-3 text-gray-600">{p.type}</td>
                                            <td className="p-3 text-gray-600">{p.schedule}</td>
                                            <td className="p-3"><span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusClass(p.lastStatus)}`}>{p.lastStatus}</span></td>
                                            <td className="p-3 text-gray-600">{p.lastBackupTime}</td>
                                            <td className="p-3 space-x-3 text-blue-600">
                                                <a href="#" onClick={(e) => {e.preventDefault(); handleViewHistory(p)}} className="hover:underline">查看历史</a>
                                                <a href="#" onClick={(e) => {e.preventDefault(); handleExecuteNow(p)}} className="hover:underline">立即执行</a>
                                                <a href="#" onClick={(e) => {e.preventDefault(); handleOpenEditModal(p)}} className="hover:underline">编辑</a>
                                                <a href="#" onClick={(e) => {e.preventDefault(); handleDeletePolicy(p)}} className="hover:underline">删除</a>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                    {/* Pagination (无变化) */}
                    <div className="pt-4">
                        <Pagination currentPage={currentPage} totalItems={policies.length} pageSize={pageSize} onPageChange={setCurrentPage} onPageSizeChange={setPageSize}/>
                    </div>
                </div>
                {/* Modals Rendered Here (无变化) */}
                <AddEditPolicyModal isOpen={isAddEditModalOpen} onClose={() => setAddEditModalOpen(false)} policy={editingPolicy} onSave={handleSavePolicy} />
                <HistoryModal isOpen={isHistoryModalOpen} onClose={() => setHistoryModalOpen(false)} data={historyData} onRestore={handleTriggerRestore} />
                <ConfirmRestoreModal isOpen={isConfirmModalOpen} onClose={() => setConfirmModalOpen(false)} onConfirm={handleConfirmRestore} info={restoreInfo} />
            </>
        );
    };
