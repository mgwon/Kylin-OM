//配置溯源组件开始
    const ConfigurationTracing = () => {
        const API_BASE_URL = 'http://localhost:5000/api/config-tracing';
        // --- 子组件 1: 历史快照模态框 ---
        // --- 子组件: 历史快照模态框 (修正版) ---
        const HistorySnapshotModal = ({ isOpen, onClose, historyId }) => {
            if (!isOpen) return null;
            const [snapshot, setSnapshot] = React.useState(null);
            const [loading, setLoading] = React.useState(true);

            React.useEffect(() => {
                if (historyId) {
                    setLoading(true);
                    fetch(`${API_BASE_URL}/snapshots/${historyId}`)
                        .then(res => res.ok ? res.json() : Promise.reject('File not found'))
                        .then(data => setSnapshot(data))
                        .catch(() => setSnapshot(null))
                        .finally(() => setLoading(false));
                }
            }, [historyId]);
            
            return (
                // --- 修复点: 增加 style={{ zIndex: 100 }} 来提升层级 ---
                <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50" style={{ zIndex: 100 }}>
                    <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl">
                        <div className="p-4 border-b flex justify-between items-center">
                            <h3 className="text-lg font-semibold">历史快照详情</h3>
                            <button onClick={onClose} className="text-2xl font-light">×</button>
                        </div>
                        <div className="p-6">
                            {loading ? <p>加载中...</p> : !snapshot ? <p className="text-red-500">无法加载快照内容。</p> : (
                                <div className="space-y-2">
                                    <p><span className="font-semibold">版本:</span> {snapshot.version}</p>
                                    <p><span className="font-semibold">时间戳:</span> {snapshot.timestamp}</p>
                                    <p className="font-semibold mt-2">内容:</p>
                                    <pre className="bg-gray-100 p-4 rounded-md font-mono text-sm">{snapshot.content}</pre>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            );
        };

        // --- 子组件 2: 创建业务域模态框 ---
        const CreateDomainModal = ({ isOpen, onClose, onSave }) => {
            if (!isOpen) return null;
            const [name, setName] = React.useState('');
            const [isMonitorOn, setMonitorOn] = React.useState(true);
            const [isAlertOn, setAlertOn] = React.useState(false);
            const handleSave = () => { if (!name.trim() || name.length > 26) { alert('请输入业务域名称，且长度不超过26个字符。'); return; } onSave({ name, isMonitorOn, isAlertOn }); };
            const ToggleSwitch = ({ checked, onChange }) => (<button type="button" onClick={() => onChange(!checked)} className={`${checked ? 'bg-blue-600' : 'bg-gray-200'} relative inline-flex h-6 w-11 items-center rounded-full`}><span className={`${checked ? 'translate-x-6' : 'translate-x-1'} inline-block h-4 w-4 transform rounded-full bg-white transition`}/></button>);
            return (<div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50"><div className="bg-white rounded-lg shadow-xl w-full max-w-lg"><div className="p-4 border-b flex justify-between items-center"><h3 className="text-lg font-semibold">创建业务域</h3><button onClick={onClose} className="text-2xl font-light">×</button></div><div className="p-8 space-y-6"><div className="flex items-center"><label className="w-24 text-right pr-4 shrink-0"><span className="text-red-500">*</span>业务域名称:</label><input value={name} onChange={e => setName(e.target.value)} placeholder="请输入业务域名称，26个字符以内" className="flex-1 border rounded-md p-2" /></div><div className="flex items-center"><label className="w-24 text-right pr-4 shrink-0">优先级:</label><input value="未开放设置" disabled className="flex-1 border rounded-md p-2 bg-gray-100 cursor-not-allowed" /></div><div className="flex items-center"><label className="w-24 text-right pr-4 shrink-0">监控开关:</label><ToggleSwitch checked={isMonitorOn} onChange={setMonitorOn} /></div><div className="flex items-center"><label className="w-24 text-right pr-4 shrink-0">告警开关:</label><ToggleSwitch checked={isAlertOn} onChange={setAlertOn} /></div></div><div className="p-4 border-t flex justify-end space-x-2"><button onClick={onClose} className="px-4 py-2 border rounded-md">取消</button><button onClick={handleSave} className="px-4 py-2 bg-blue-600 text-white rounded-md">确定</button></div></div></div>);
        };

        // --- 子组件 3: 添加主机到业务域模态框 ---
        const AddHostToDomainModal = ({ isOpen, onClose, domain, onSaveSuccess }) => {
            if (!isOpen) return null;

            const [allHosts, setAllHosts] = React.useState([]);
            const [selectedHosts, setSelectedHosts] = React.useState([]);
            
            React.useEffect(() => {
                if (isOpen) {
                    setSelectedHosts([]);
                    fetch(`${API_BASE_URL}/all-hosts`)
                        .then(res => res.json())
                        .then(data => setAllHosts(data))
                        .catch(err => console.error("Failed to fetch hosts", err));
                }
            }, [isOpen]);

            const handleSelect = (host) => {
                if (!selectedHosts.find(sh => sh.id === host.id)) {
                    setSelectedHosts(prev => [...prev, host]);
                }
            };

            const handleUnselect = (host) => {
                setSelectedHosts(prev => prev.filter(h => h.id !== host.id));
            };

            const handleSave = () => {
                if (selectedHosts.length === 0) {
                    alert('请至少选择一个主机！');
                    return;
                }

                fetch(`${API_BASE_URL}/domains/${domain.id}/assets`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ hosts: selectedHosts })
                })
                .then(res => res.ok ? res.json() : Promise.reject('添加失败'))
                .then(data => {
                    alert(data.message || '添加主机成功');
                    onSaveSuccess();
                    onClose();
                })
                .catch(err => alert(`添加主机失败: ${err.toString()}`));
            };

            return (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
                    <div className="bg-white rounded-lg shadow-xl w-full max-w-3xl flex flex-col" style={{maxHeight: '80vh'}}>
                        <div className="p-4 border-b flex justify-between items-center">
                            <h3 className="text-lg font-semibold">添加主机</h3>
                            <button onClick={onClose} className="text-2xl font-light">×</button>
                        </div>
                        <div className="p-6 space-y-4 flex-grow overflow-y-auto">
                            <div><span className="font-semibold">归属业务域:</span> {domain?.name}</div>
                            {/* --- 修复点：将下面的占位符替换为完整的左右选择框渲染逻辑 --- */}
                            <div className="grid grid-cols-2 gap-4 h-full">
                                {/* 左侧：可选主机列表 */}
                                <div className="border rounded-md flex flex-col">
                                    <div className="p-2 border-b bg-gray-50 text-sm font-semibold">可选主机列表</div>
                                    <ul className="p-2 overflow-y-auto">
                                        {allHosts.length > 0 ? allHosts.map(host => (
                                            <li key={host.name} className="flex justify-between items-center p-2 hover:bg-gray-100 rounded-md text-sm">
                                                <span>{host.name}</span>
                                                <button 
                                                    onClick={() => handleSelect(host)}
                                                    className="text-blue-600 hover:underline disabled:text-gray-400 disabled:no-underline"
                                                    disabled={selectedHosts.some(sh => sh.id === host.id)}>
                                                    选择
                                                </button>
                                            </li>
                                        )) : <li className="p-4 text-center text-gray-500">无可选主机</li>}
                                    </ul>
                                </div>
                                {/* 右侧：已选主机列表 */}
                                <div className="border rounded-md flex flex-col">
                                    <div className="p-2 border-b bg-gray-50 text-sm font-semibold">已选主机列表</div>
                                    <ul className="p-2 overflow-y-auto">
                                        {selectedHosts.length > 0 ? selectedHosts.map(host => (
                                            <li key={host.name} className="flex justify-between items-center p-2 hover:bg-gray-100 rounded-md text-sm">
                                                <span>{host.name}</span>
                                                <button onClick={() => handleUnselect(host)} className="text-red-600 hover:underline">
                                                    移除
                                                </button>
                                            </li>
                                        )) : <li className="p-4 text-center text-gray-500">尚未选择主机</li>}
                                    </ul>
                                </div>
                            </div>
                        </div>
                        <div className="p-4 border-t flex justify-end space-x-2 flex-shrink-0">
                            <button onClick={onClose} className="px-4 py-2 border rounded-md">取消</button>
                            <button onClick={handleSave} className="px-4 py-2 bg-blue-600 text-white rounded-md">确定</button>
                        </div>
                    </div>
                </div>
            );
        };


        // --- 子组件 4: 新增基线配置模态框 ---
        const AddBaselineModal = ({ isOpen, onClose, onSave, domains }) => {
            if(!isOpen) return null;
            const [form, setForm] = React.useState({domainId: domains[0]?.id || '', path: '/etc/new-config.conf', source: '手动输入', content: ''});
            const handleChange = (e) => setForm(prev => ({...prev, [e.target.name]: e.target.value}));
            const handleSave = () => { onSave(form); };
            return (<div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50"><div className="bg-white rounded-lg shadow-xl w-full max-w-xl"><div className="p-4 border-b flex justify-between items-center"><h3 className="text-lg font-semibold">新增配置</h3><button onClick={onClose} className="text-2xl font-light">×</button></div><div className="p-6 space-y-4"><div><label className="block text-sm">所属业务域</label><select name="domainId" value={form.domainId} onChange={handleChange} className="w-full border p-2 rounded-md bg-white">{domains.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}</select></div><div><label className="block text-sm"><span className="text-red-500">*</span>配置路径</label><input name="path" value={form.path} onChange={handleChange} className="w-full border p-2 rounded-md"/></div><div><label className="block text-sm">配置来源</label><select name="source" value={form.source} onChange={handleChange} className="w-full border p-2 rounded-md bg-white"><option>手动输入</option><option>从主机获取</option></select></div><div><label className="block text-sm"><span className="text-red-500">*</span>配置内容</label><textarea name="content" value={form.content} onChange={handleChange} rows="6" className="w-full border p-2 rounded-md font-mono"></textarea></div></div><div className="p-4 border-t flex justify-end space-x-2"><button onClick={onClose} className="px-4 py-2 border rounded-md">取消</button><button onClick={handleSave} className="px-4 py-2 bg-blue-600 text-white rounded-md">确定</button></div></div></div>);
        };

        // --- 子组件 5: 基线内容模态框 ---
        const BaselineContentModal = ({ isOpen, onClose, baselineId }) => {
            if (!isOpen) return null;
            const [detail, setDetail] = React.useState(null);
            const [loading, setLoading] = React.useState(true);
            React.useEffect(() => { if (baselineId) { setLoading(true); fetch(`${API_BASE_URL}/baselines/content/${baselineId}`).then(res => res.ok ? res.json() : Promise.reject()).then(data => setDetail(data)).catch(() => setDetail(null)).finally(() => setLoading(false)); } }, [baselineId]);
            return (<div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50"><div className="bg-white rounded-lg shadow-xl w-full max-w-2xl"><div className="p-4 border-b flex justify-between items-center"><h3 className="text-lg font-semibold">配置文件内容</h3><button onClick={onClose} className="text-2xl font-light">×</button></div><div className="p-6">{loading ? <p>加载中...</p> : !detail ? <p className="text-red-500">无法加载内容。</p> : (<><p className="text-sm text-gray-600 mb-2">配置文件: {detail.path}</p><pre className="bg-gray-100 p-4 rounded-md h-96 overflow-auto font-mono text-sm">{detail.content}</pre></>)}</div></div></div>);
        };

        // --- 子组件 6: 状态详情模态框 ---
        const StatusDetailModal = ({ isOpen, onClose, assetId }) => {
            if (!isOpen) return null;
            const [detail, setDetail] = React.useState(null);
            const [loading, setLoading] = React.useState(true);
            React.useEffect(() => { if (assetId) { setLoading(true); fetch(`${API_BASE_URL}/assets/status/${assetId}`).then(res => res.ok ? res.json() : Promise.reject()).then(data => setDetail(data)).catch(() => setDetail(null)).finally(() => setLoading(false)); } }, [assetId]);
            const handleSyncOne = (config) => { alert(`已发送指令，开始同步配置文件: ${config.path}`); };
            const handleSyncAll = () => { if (window.confirm('确定要同步此主机上的所有未同步配置吗？')) { alert('已发送全部同步指令！'); } };
            return (<div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50"><div className="bg-white rounded-lg shadow-xl w-full max-w-3xl"><div className="p-4 border-b flex justify-between items-center"><h3 className="text-lg font-semibold">状态详情</h3><button onClick={onClose} className="text-2xl font-light">×</button></div><div className="p-6">{loading ? <p>加载状态详情中...</p> : !detail ? <p className="text-red-500">无法加载详情。</p> : (<div className="space-y-4"><p className="font-semibold">主机IP: {detail.ip}</p><div className="border rounded-lg max-h-96 overflow-y-auto"><table className="w-full text-sm"><thead className="bg-gray-50 sticky top-0"><tr><th className="p-2 text-left">配置文件路径</th><th className="p-2 text-left">同步状态</th><th className="p-2 text-left">操作</th></tr></thead><tbody>{detail.configs.map(config => (<tr key={config.id} className="border-b"><td className="p-2 font-mono">{config.path}</td><td className={`p-2 font-semibold ${config.status === '已同步' ? 'text-green-600' : 'text-yellow-600'}`}>{config.status}</td><td className="p-2">{config.status !== '已同步' && <button onClick={() => handleSyncOne(config)} className="text-blue-600 hover:underline">同步</button>}</td></tr>))}</tbody></table></div></div>)}</div><div className="p-4 border-t flex justify-end"><button onClick={handleSyncAll} className="bg-blue-600 text-white font-semibold py-2 px-4 rounded-md hover:bg-blue-700 text-sm">全部同步</button></div></div></div>);
        };

        // --- 子组件 7: 主机配置详情与溯源模态框 ---
        const HostConfigDetailModal = ({ isOpen, onClose, assetId, onSyncSuccess }) => {
            if (!isOpen) return null;
            const [detail, setDetail] = React.useState(null);
            const [loading, setLoading] = React.useState(true);
            const [activeTab, setActiveTab] = React.useState('trace');
            const [snapshotModal, setSnapshotModal] = React.useState({ isOpen: false, historyId: null });
            React.useEffect(() => { if (isOpen && assetId) { setLoading(true); fetch(`${API_BASE_URL}/assets/config/${assetId}`).then(res => res.ok ? res.json() : Promise.reject()).then(data => setDetail(data)).catch(() => setDetail(null)).finally(() => setLoading(false)); } }, [isOpen, assetId]);
            const handleSyncConfig = () => {
                if (window.confirm(`确定要将主机 ${detail.ip} 的配置恢复至基线标准吗？\n此操作将删除当前漂移的配置。`)) {
                    fetch(`${API_BASE_URL}/assets/${assetId}/sync`, { method: 'POST' })
                        .then(res => res.ok ? res.json() : Promise.reject(res.statusText))
                        .then(data => {
                            alert(data.message || '同步成功！');
                            if (onSyncSuccess) { onSyncSuccess(assetId); }
                            onClose();
                        })
                        .catch(err => alert(`同步失败: ${err.toString()}`));
                }
            };

            // --- 修改点: 实现真实设为基线逻辑 ---
            const handleSetAsBaseline = () => {
                if (window.confirm(`确定要将主机 ${detail.ip} 的当前配置设为业务域的新基线吗？\n此操作会覆盖现有基线。`)) {
                    fetch(`${API_BASE_URL}/assets/${assetId}/set-as-baseline`, { method: 'POST' })
                        .then(res => res.ok ? res.json() : Promise.reject(res.statusText))
                        .then(data => {
                            alert(data.message || '设为基线成功！');
                            if (onSyncSuccess) { onSyncSuccess(assetId); }
                            onClose();
                        })
                        .catch(err => alert(`操作失败: ${err.toString()}`));
                }
            };
            const handleViewSnapshot = (historyItem) => { setSnapshotModal({ isOpen: true, historyId: historyItem.id }); };
            const renderTabContent = () => { if(!detail) return null; switch(activeTab) { case 'props': return (<div className="p-4 space-y-2 text-sm"><div className="grid grid-cols-4 gap-4"><div><span className="font-semibold">fileAttr:</span> {detail.properties.fileAttr}</div><div><span className="font-semibold">fileOwner:</span> {detail.properties.fileOwner}</div></div><div className="font-semibold mt-4">文本内容:</div><pre className="bg-gray-100 p-3 rounded-md">{detail.content}</pre></div>); case 'trace': return (<div className="p-4 space-y-4"><blockquote className="border-l-4 border-blue-500 bg-blue-50 p-4"><p className="text-gray-700 italic">🤖 <span className="font-semibold">AIOps分析:</span> {detail.processTrace.llmSummary}</p></blockquote><div className="font-semibold">进程修改记录追溯:</div><pre className="bg-gray-800 text-white font-mono text-sm p-4 rounded-lg h-64 overflow-y-auto">{detail.processTrace.log}</pre></div>); case 'history': return (<table className="min-w-full text-sm"><thead className="bg-gray-100"><tr><th className="p-2 text-left">版本</th><th className="p-2 text-left">时间戳</th><th className="p-2 text-left">来源</th><th className="p-2 text-left">操作</th></tr></thead><tbody>{detail.history.map(h => (<tr key={h.id} className="border-b"><td className="p-2">{h.version}</td><td className="p-2">{h.timestamp}</td><td className="p-2">{h.source}</td><td className="p-2"><a href="#" onClick={(e)=>{e.preventDefault(); handleViewSnapshot(h);}} className="text-blue-600 hover:underline">查看快照</a></td></tr>))}</tbody></table>); default: return null; } };
            return (<><HistorySnapshotModal isOpen={snapshotModal.isOpen} onClose={() => setSnapshotModal({isOpen: false, historyId: null})} historyId={snapshotModal.historyId} /><div className={`fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50 ${isOpen ? '' : 'hidden'}`}><div className="bg-white rounded-lg shadow-xl w-full max-w-4xl flex flex-col" style={{height: '80vh'}}>{loading ? <div className="p-10 text-center">加载中...</div> : !detail ? (<div className="p-6"><h3 className="text-lg font-semibold text-red-600">加载失败</h3><p className="text-gray-600 my-4">无法获取配置详情。</p><button onClick={onClose} className="px-4 py-2 border rounded-md">关闭</button></div>) : (<><div className="p-4 border-b"><div className="flex justify-between items-center"><h3 className="text-lg font-semibold">主机当前配置</h3><button onClick={onClose} className="text-2xl font-light">×</button></div><div className="text-sm text-gray-600 mt-2">主机: {detail.ip}     配置项: {detail.filePath}</div>{detail.isDrift && <div className="mt-2 text-red-600 font-semibold border border-red-300 bg-red-50 p-2 rounded-md inline-block">⊗ 与业务域配置不一致</div>}</div><div className="border-b border-gray-200"><nav className="flex space-x-4 px-4"><button onClick={() => setActiveTab('trace')} className={`py-3 px-1 border-b-2 font-medium text-sm ${activeTab === 'trace' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500'}`}>进程级溯源</button><button onClick={() => setActiveTab('props')} className={`py-3 px-1 border-b-2 font-medium text-sm ${activeTab === 'props' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500'}`}>属性与内容</button><button onClick={() => setActiveTab('history')} className={`py-3 px-1 border-b-2 font-medium text-sm ${activeTab === 'history' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500'}`}>历史快照</button></nav></div><div className="flex-grow overflow-y-auto">{renderTabContent()}</div><div className="p-4 border-t flex justify-end space-x-3 bg-gray-50"><button onClick={handleSyncConfig} className="px-4 py-2 bg-red-600 text-white rounded-md font-semibold hover:bg-red-700">⟲ 同步配置</button><button onClick={handleSetAsBaseline} className="px-4 py-2 bg-green-600 text-white rounded-md font-semibold hover:bg-green-700">✔ 设为基线</button></div></>)}</div></div></>);
        };

        // --- 子组件 8: 业务域详情页 ---
        const DomainDetailView = ({ domainId, onBack }) => {
            const [detail, setDetail] = React.useState(null);
            const [loading, setLoading] = React.useState(true);
            const [configModal, setConfigModal] = React.useState({ isOpen: false, assetId: null });
            const [statusModal, setStatusModal] = React.useState({ isOpen: false, assetId: null });
            const fetchDetail = React.useCallback(() => {
                setLoading(true);
                fetch(`${API_BASE_URL}/domains/${domainId}`)
                    .then(res => res.ok ? res.json() : Promise.reject())
                    .then(data => setDetail(data))
                    .catch(() => setDetail(null))
                    .finally(() => setLoading(false));
            }, [domainId]);

            React.useEffect(() => {
                fetchDetail();
            }, [fetchDetail]);
            
            // --- 修改点: onSyncSuccess 现在只是重新加载详情 ---
            const handleSyncStatusUpdate = () => {
                fetchDetail(); // 操作成功后，重新获取详情以刷新整个列表状态
            };
            const handleScan = () => {
                alert('正在后台模拟扫描，请稍后...');
                fetch(`${API_BASE_URL}/domains/${domainId}/scan`, { method: 'POST' })
                    .then(res => res.ok ? res.json() : Promise.reject(res.statusText))
                    .then(data => {
                        alert(data.message || '扫描完成!');
                        fetchDetail(); // 扫描完成后，重新加载数据以显示最新状态
                    })
                    .catch(err => alert(`扫描失败: ${err.toString()}`));
            };
            const handleOpenConfigDetail = (asset) => { 
                // 只有未同步的主机才能打开 "当前配置"
                if (asset.syncStatus.includes('未同步')) {
                    setConfigModal({ isOpen: true, assetId: asset.id }); 
                } else {
                    alert('此主机配置已同步，无需查看当前配置。');
                }
            };
            const handleOpenStatusDetail = (asset) => { setStatusModal({ isOpen: true, assetId: asset.id }); };
            const handleDeleteAsset = (assetToDelete) => {
                if (window.confirm(`您确定要从业务域 "${detail.name}" 中移除主机 ${assetToDelete.ip} 吗？\n此操作不可撤销。`)) {
                    fetch(`${API_BASE_URL}/domains/${domainId}/assets/${assetToDelete.id}`, {
                        method: 'DELETE'
                    })
                    .then(res => res.ok ? res.json() : Promise.reject('删除失败'))
                    .then(data => {
                        alert(data.message || '主机移除成功');
                        // 成功后直接在前端更新UI，提供即时反馈，避免重新加载整个页面
                        setDetail(prev => ({
                            ...prev,
                            assets: prev.assets.filter(a => a.id !== assetToDelete.id)
                        }));
                    })
                    .catch(err => alert(`移除主机失败: ${err.toString()}`));
                }
            };
            if (loading) return <div className="text-center p-10">加载业务域资产...</div>;
            if (!detail) return <div className="bg-white p-6 rounded-lg shadow-md text-center"><h3 className="text-xl font-semibold text-red-600">加载详情失败</h3><p className="my-4 text-gray-600">无法获取该业务域的详情数据。</p><button onClick={onBack} className="text-blue-600 hover:underline font-semibold">← 返回列表</button></div>;
            return (
                <div className="bg-white p-6 rounded-lg shadow-md">
                    <HostConfigDetailModal isOpen={configModal.isOpen} onClose={() => setConfigModal({isOpen: false, assetId: null})} assetId={configModal.assetId} onSyncSuccess={handleSyncStatusUpdate} />
                    <StatusDetailModal isOpen={statusModal.isOpen} onClose={() => setStatusModal({isOpen: false, assetId: null})} assetId={statusModal.assetId} />
                    <div className="flex justify-between items-center mb-4">
                        <div>
                            <button onClick={onBack} className="text-blue-600 hover:underline text-sm mb-2">← 返回</button>
                            <h3 className="font-semibold text-lg">{detail.name}</h3>
                        </div>
                        {/* --- 新增扫描按钮 --- */}
                        <button onClick={handleScan} className="bg-blue-600 text-white font-semibold py-2 px-4 rounded-md hover:bg-blue-700 text-sm">☥ 扫描漂移</button>
                    </div>
                    <table className="min-w-full text-sm">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="p-3 text-left">IP地址</th>
                                <th className="p-3 text-left">IP协议</th>
                                <th className="p-3 text-left">同步状态</th>
                                <th className="p-3 text-left">操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            {detail.assets.length > 0 ? detail.assets.map(asset => (
                                <tr key={asset.id} className="border-b hover:bg-gray-50">
                                    <td className="p-3">{asset.ip}</td>
                                    <td className="p-3">{asset.protocol}</td>
                                    <td className={`p-3 font-semibold ${asset.syncStatus.includes('未同步') ? 'text-red-600' : 'text-green-600'}`}>{asset.syncStatus}</td>
                                    <td className="p-3 space-x-4">
                                        <a href="#" onClick={(e) => { e.preventDefault(); handleOpenConfigDetail(asset)}} className="text-blue-600 hover:underline">当前配置</a>
                                        <a href="#" onClick={(e) => { e.preventDefault(); handleOpenStatusDetail(asset); }} className="text-blue-600 hover:underline">状态详情</a>
                                        <a href="#" onClick={(e) => { e.preventDefault(); handleDeleteAsset(asset); }} className="text-blue-600 hover:underline">删除</a>
                                    </td>
                                </tr>
                            )) : (
                                <tr><td colSpan="4" className="p-10 text-center text-gray-500">该业务域下没有主机。</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            );
        };

        // --- 主组件逻辑 ---
        const [view, setView] = React.useState({ page: 'list', param: null });
        const [mainTab, setMainTab] = React.useState('domains');
        const [domains, setDomains] = React.useState([]);
        const [baselines, setBaselines] = React.useState([]);
        const [loading, setLoading] = React.useState(true);
        const [isCreateDomainModalOpen, setCreateDomainModalOpen] = React.useState(false);
        const [isAddHostModalOpen, setAddHostModalOpen] = React.useState(false);
        const [isAddBaselineModalOpen, setAddBaselineModalOpen] = React.useState(false);
        const [targetDomain, setTargetDomain] = React.useState(null);
        const [baselineModal, setBaselineModal] = React.useState({ isOpen: false, baselineId: null });


        const fetchData = React.useCallback(() => { 
            setLoading(true); 
            const endpoint = mainTab === 'domains' ? 'domains' : 'baselines';
            // --- 修改点: 调用新API ---
            const promise = fetch(`${API_BASE_URL}/${endpoint}`)
                .then(res => res.json())
                .then(data => {
                    if (mainTab === 'domains') {
                        setDomains(data);
                    } else {
                        setBaselines(data);
                    }
                });
            promise.catch(err => console.error(`Failed to load ${mainTab}`, err))
                .finally(() => setLoading(false));
        }, [mainTab]);
        React.useEffect(() => { if (view.page === 'list') { fetchData(); } }, [view.page, fetchData]);
        const handleCreateDomain = (domainData) => {
            fetch(`${API_BASE_URL}/domains`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(domainData)
            })
            .then(res => res.ok ? res.json() : Promise.reject('创建失败'))
            .then(data => {
                alert(data.message || '业务域创建成功');
                setCreateDomainModalOpen(false);
                fetchData(); // 重新加载数据以显示新条目
            })
            .catch(err => alert(`创建业务域失败: ${err.toString()}`));
        };
        
        const handleOpenAddHost = (domain) => { 
            setTargetDomain(domain); // 这个函数现在只是设置目标域
            setAddHostModalOpen(true); 
        };
        const handleSaveBaseline = (baselineData) => {
            fetch(`${API_BASE_URL}/baselines`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(baselineData)
            })
            .then(res => res.ok ? res.json() : Promise.reject('新增失败'))
            .then(data => {
                alert(data.message || '基线配置新增成功');
                setAddBaselineModalOpen(false);
                if (mainTab === 'baselines') {
                    fetchData(); // 如果当前就在基线tab，则刷新
                }
            })
            .catch(err => alert(`新增基线失败: ${err.toString()}`));
        };
        const handleDeleteBaseline = (baseline) => {
            if (window.confirm(`你确定删除该行配置吗？\n路径: ${baseline.path}`)) {
                fetch(`${API_BASE_URL}/baselines/${baseline.id}`, {
                    method: 'DELETE'
                })
                .then(res => res.ok ? res.json() : Promise.reject('删除失败'))
                .then(data => {
                    alert(data.message || '删除成功');
                    fetchData(); // 重新加载数据
                })
                .catch(err => alert(`删除基线失败: ${err.toString()}`));
            }
        };
        const handleViewBaselineContent = (baseline) => { setBaselineModal({ isOpen: true, baselineId: baseline.id }); };
        const getDriftStatusClass = (status) => ({'漂移': 'text-yellow-600', '健康': 'text-green-600', '未监控': 'text-gray-500'}[status] || '');
        
        const renderListView = () => (
            <div className="space-y-4">
                <div className="flex justify-between items-center"><div className="border-b border-gray-200"><nav className="flex space-x-8"><button onClick={() => setMainTab('domains')} className={`py-3 px-1 border-b-2 font-medium ${mainTab === 'domains' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500'}`}>业务域管理</button><button onClick={() => setMainTab('baselines')} className={`py-3 px-1 border-b-2 font-medium ${mainTab === 'baselines' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500'}`}>基线配置管理</button></nav></div><div className="flex space-x-2">{mainTab === 'domains' ? (<button onClick={() => setCreateDomainModalOpen(true)} className="bg-blue-600 text-white font-semibold py-2 px-4 rounded-md hover:bg-blue-700 text-sm">[+] 创建业务域</button>) : (<button onClick={() => setAddBaselineModalOpen(true)} className="bg-blue-600 text-white font-semibold py-2 px-4 rounded-md hover:bg-blue-700 text-sm">[+] 新增配置</button>)}<button onClick={fetchData} className="bg-white border text-gray-700 py-2 px-4 rounded-md hover:bg-gray-50 text-sm">刷新</button></div></div>
                <div className="bg-white p-6 rounded-lg shadow-md">
                    {loading ? <div className="text-center p-10">加载中...</div> : mainTab === 'domains' ? (<table className="min-w-full text-sm"><thead className="bg-gray-50"><tr><th className="p-3 text-left">业务域名称</th><th className="p-3 text-left">资产数量</th><th className="p-3 text-left">配置漂移状态</th><th className="p-3 text-left">操作</th></tr></thead><tbody>{domains.map(d => (<tr key={d.id} className="border-b hover:bg-gray-50"><td className="p-3 font-semibold">{d.name}</td><td className="p-3">{d.assetCount}</td><td className={`p-3 font-bold ${getDriftStatusClass(d.driftStatus)}`}>● {d.driftStatus}</td><td className="p-3 space-x-4"><a href="#" onClick={e => {e.preventDefault(); setView({page:'detail', param:d.id})}} className="text-blue-600 hover:underline">详情</a><a href="#" onClick={e => {e.preventDefault(); handleOpenAddHost(d)}} className="text-blue-600 hover:underline">添加主机</a></td></tr>))}</tbody></table>) : (<table className="min-w-full text-sm"><thead className="bg-gray-50"><tr><th className="p-3 text-left">配置路径</th><th className="p-3 text-left">所属业务域</th><th className="p-3 text-left">操作</th></tr></thead><tbody>{baselines.map(b => (<tr key={b.id} className="border-b hover:bg-gray-50"><td className="p-3 font-mono">{b.path}</td><td className="p-3">{b.domain}</td><td className="p-3 space-x-4"><a href="#" onClick={(e) => { e.preventDefault(); handleViewBaselineContent(b); }} className="text-blue-600 hover:underline">查看内容</a><a href="#" onClick={e => {e.preventDefault(); handleDeleteBaseline(b)}} className="text-blue-600 hover:underline">删除</a></td></tr>))}</tbody></table>)}
                </div>
            </div>
        );
        
        return (
            <>
                {view.page === 'list' ? renderListView() : <DomainDetailView domainId={view.param} onBack={() => setView({ page: 'list', param: null })} />}
                <CreateDomainModal isOpen={isCreateDomainModalOpen} onClose={() => setCreateDomainModalOpen(false)} onSave={handleCreateDomain}/>
                <AddHostToDomainModal 
                    isOpen={isAddHostModalOpen} 
                    onClose={() => setAddHostModalOpen(false)} 
                    domain={targetDomain} // 传递整个 domain 对象
                    onSaveSuccess={fetchData} // 传递 fetchData 作为成功回调
                />
                <AddBaselineModal isOpen={isAddBaselineModalOpen} onClose={() => setAddBaselineModalOpen(false)} onSave={handleSaveBaseline} domains={domains} />
                <BaselineContentModal isOpen={baselineModal.isOpen} onClose={() => setBaselineModal({isOpen: false, baselineId: null})} baselineId={baselineModal.baselineId} />
            </>
        );
    };
    //配置溯源组件结束