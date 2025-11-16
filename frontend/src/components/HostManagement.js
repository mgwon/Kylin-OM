//主机管理页面
    const AddGroupSubModal = ({ isOpen, onClose, onSaveSuccess }) => {
        if (!isOpen) return null;

        const [groupName, setGroupName] = React.useState('');
        const [description, setDescription] = React.useState('');
        const [isSubmitting, setIsSubmitting] = React.useState(false);

        const handleSubmit = () => {
            if (!groupName.trim()) {
                alert('主机组名称不能为空！');
                return;
            }
            setIsSubmitting(true);
            fetch('http://localhost:5000/api/host-groups/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ groupName, description }),
            })
            .then(res => res.ok ? res.json() : Promise.reject('添加失败'))
            .then(data => {
                alert(data.message || '添加成功');
                onSaveSuccess(data.group); // Pass the new group object back
            })
            .catch(err => alert(err.toString()))
            .finally(() => setIsSubmitting(false));
        };

        return (
            <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-[60]">
                <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
                    <div className="p-4 border-b"><h3 className="text-lg font-semibold">添加主机组</h3></div>
                    <div className="p-6 space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">主机组名称</label>
                            <input type="text" value={groupName} onChange={(e) => setGroupName(e.target.value)} className="mt-1 block w-full border border-gray-300 rounded-md p-2"/>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">信息描述</label>
                            <textarea value={description} onChange={(e) => setDescription(e.target.value)} className="mt-1 block w-full border border-gray-300 rounded-md p-2"></textarea>
                        </div>
                    </div>
                    <div className="p-4 border-t flex justify-end space-x-2">
                        <button onClick={onClose} disabled={isSubmitting} className="px-4 py-2 border rounded-md">取消</button>
                        <button onClick={handleSubmit} disabled={isSubmitting} className="px-4 py-2 bg-blue-600 text-white rounded-md disabled:bg-gray-400">
                            {isSubmitting ? '添加中...' : '确认'}
                        </button>
                    </div>
                </div>
            </div>
        );
    };

    const AddHostModal = ({ isOpen, onClose, onAddSuccess }) => {
        if (!isOpen) { return null; }

        const [formData, setFormData] = React.useState({
            name: '111',
            group: '', // Initially empty, will be set after fetching
            ip: '',
            ssh: '22',
            nodeType: '管理节点',
            username: 'admin',
            password: '123456',
            sudoPassword: '',
            encryptionKey: ''
        });

        // NEW STATE: To hold the list of groups for the dropdown
        const [hostGroups, setHostGroups] = React.useState([]);
        // NEW STATE: To control the visibility of the new sub-modal
        const [isAddGroupModalOpen, setIsAddGroupModalOpen] = React.useState(false);

        // NEW: Fetch host groups when the modal opens
        React.useEffect(() => {
            fetch('http://localhost:5000/api/host-groups')
                .then(res => res.json())
                .then(data => {
                    setHostGroups(data);
                    // Set the default selection to the first group if available
                    if (data.length > 0) {
                        setFormData(prev => ({ ...prev, group: data[0].name }));
                    }
                })
                .catch(err => console.error("Failed to fetch host groups for modal:", err));
        }, []);
        
        // NEW: Handler for when a new group is successfully added via the sub-modal
        const handleGroupAdded = (newGroup) => {
            // Add the new group to our list and select it in the dropdown
            setHostGroups(prev => [newGroup, ...prev]);
            setFormData(prev => ({...prev, group: newGroup.name}));
            setIsAddGroupModalOpen(false); // Close the sub-modal
        };

        const [showPassword, setShowPassword] = React.useState(false);
        const [showSudoPassword, setShowSudoPassword] = React.useState(false);
        const [showEncryptionKey, setShowEncryptionKey] = React.useState(false);

        const handleChange = (e) => {
            const { name, value } = e.target;
            setFormData(prev => ({ ...prev, [name]: value }));
        };

        const handleSubmit = () => {
            const newHostData = {
                name: formData.name,
                ip: formData.ip,
                ssh: formData.ssh,
                group: formData.group,
                isMgmt: formData.nodeType === '管理节点' ? '是' : '否',
                status: '运行中'
            };
            onAddSuccess(newHostData);
        };
        
        const InfoIcon = React.useCallback(() => (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
        ), []);

        const EyeOffIcon = React.useCallback(() => ( <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5"><path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.243 4.243L6.228 6.228" /></svg> ), []);

        const PasswordInput = React.useCallback(({ name, value, onChange, show, onToggle, placeholder = "请输入", isLightBg = false }) => (
            <div className="relative w-full">
                <input
                    type={show ? 'text' : 'password'}
                    name={name}
                    value={value}
                    onChange={onChange}
                    placeholder={placeholder}
                    className={`w-full border rounded-md p-2 pr-10 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 ${isLightBg ? 'bg-blue-50' : 'bg-white'}`}
                />
                <button type="button" onClick={onToggle} className="absolute inset-y-0 right-0 px-3 flex items-center text-gray-500 hover:text-gray-700">
                    <EyeOffIcon />
                </button>
            </div>
        ), [EyeOffIcon]);

        const FormField = React.useCallback(({ label, children }) => (
            <div className="flex items-center">
                <label className="text-right w-36 flex-shrink-0 text-sm text-gray-700 pr-4">
                    <span className="text-red-500 mr-1">*</span>{label}:
                </label>
                <div className="flex-grow flex items-center">
                    {children}
                </div>
            </div>
        ), []);

        return (
            <>
                {/* NEW: Render the sub-modal */}
                <AddGroupSubModal 
                    isOpen={isAddGroupModalOpen} 
                    onClose={() => setIsAddGroupModalOpen(false)}
                    onSaveSuccess={handleGroupAdded}
                />

                <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
                    <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl">
                        <div className="p-8 space-y-5">
                            <FormField label="主机名称">
                                <input type="text" name="name" value={formData.name} onChange={handleChange} className="w-full border border-blue-400 rounded-md p-2 focus:ring-1 focus:ring-blue-500"/>
                                <span className="ml-2 cursor-help"><InfoIcon /></span>
                            </FormField>

                            <FormField label="所属主机组">
                                {/* MODIFIED: Populate dropdown from state */}
                                <select name="group" value={formData.group} onChange={handleChange} className="w-full border border-gray-300 rounded-md p-2 bg-white focus:ring-1 focus:ring-blue-500">
                                    {hostGroups.length === 0 && <option disabled>加载中...</option>}
                                    {hostGroups.map(g => <option key={g.id} value={g.name}>{g.name}</option>)}
                                </select>
                                {/* MODIFIED: Button now opens the sub-modal */}
                                <button onClick={() => setIsAddGroupModalOpen(true)} className="ml-2 bg-blue-500 text-white font-semibold py-2 px-4 rounded-md hover:bg-blue-600 text-sm whitespace-nowrap">+ 添加主机组</button>
                            </FormField>

                            <FormField label="IP地址">
                                <input type="text" name="ip" value={formData.ip} onChange={handleChange} placeholder="请输入" className="w-full border border-gray-300 rounded-md p-2 focus:ring-1 focus:ring-blue-500" />
                            </FormField>

                            <FormField label="SSH登录端口">
                                <input type="number" name="ssh" value={formData.ssh} onChange={handleChange} className="border border-gray-300 rounded-md p-2 w-full focus:ring-1 focus:ring-blue-500" />
                            </FormField>

                            <div className="flex items-center">
                                <label className="text-right w-36 flex-shrink-0 text-sm text-gray-700 pr-4">管理/监控节点:</label>
                                <div className="flex items-center space-x-6">
                                    <label className="flex items-center cursor-pointer"><input type="radio" name="nodeType" value="管理节点" checked={formData.nodeType === '管理节点'} onChange={handleChange} className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"/><span className="ml-2 text-sm">管理节点</span></label>
                                    <label className="flex items-center cursor-pointer"><input type="radio" name="nodeType" value="监控节点" checked={formData.nodeType === '监控节点'} onChange={handleChange} className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"/><span className="ml-2 text-sm">监控节点</span></label>
                                </div>
                            </div>

                            <FormField label="主机用户名">
                                <input type="text" name="username" value={formData.username} onChange={handleChange} className="w-full border border-gray-300 rounded-md p-2 bg-blue-50 focus:ring-1 focus:ring-blue-500"/>
                                <span className="ml-2 cursor-help"><InfoIcon /></span>
                            </FormField>

                            <FormField label="主机登录密码">
                                <PasswordInput name="password" value={formData.password} onChange={handleChange} show={showPassword} onToggle={() => setShowPassword(!showPassword)} isLightBg={true} />
                            </FormField>
                            
                            <FormField label="主机sudo密码">
                                <PasswordInput name="sudoPassword" value={formData.sudoPassword} onChange={handleChange} show={showSudoPassword} onToggle={() => setShowSudoPassword(!showSudoPassword)} />
                            </FormField>

                            <FormField label="加密密钥">
                                <PasswordInput name="encryptionKey" value={formData.encryptionKey} onChange={handleChange} show={showEncryptionKey} onToggle={() => setShowEncryptionKey(!showEncryptionKey)} />
                            </FormField>
                        </div>
                        <div className="flex justify-center items-center p-6 pt-2 space-x-4">
                            <button onClick={onClose} className="bg-white border border-gray-300 text-gray-800 font-semibold py-2 px-8 rounded-md hover:bg-gray-100">取消</button>
                            <button onClick={handleSubmit} className="bg-blue-500 text-white font-semibold py-2 px-8 rounded-md hover:bg-blue-600">添加</button>
                        </div>
                    </div>
                </div>
            </>
        );
    };

    const ViewHostModal = ({ isOpen, onClose, host }) => {
        if (!isOpen || !host) return null;
        const DetailItem = ({ label, value }) => (
            <div className="grid grid-cols-3 gap-4 py-2">
                <dt className="text-sm font-medium text-gray-500">{label}</dt>
                <dd className="text-sm text-gray-900 col-span-2">{value}</dd>
            </div>
        );
        return (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
                <div className="bg-white rounded-lg shadow-xl w-full max-w-lg">
                    <div className="flex justify-between items-center p-4 border-b">
                        <h3 className="text-lg font-semibold text-gray-800">主机详情</h3>
                        <button onClick={onClose} className="text-gray-500 hover:text-gray-800 text-2xl">×</button>
                    </div>
                    <div className="p-6">
                        <dl>
                            <DetailItem label="主机名称" value={host.name} />
                            <DetailItem label="IP 地址" value={host.ip} />
                            <DetailItem label="SSH 登录端口" value={host.ssh} />
                            <DetailItem label="所属主机组" value={host.group} />
                            <DetailItem label="管理节点" value={host.isMgmt} />
                            <DetailItem label="运行状态" value={host.status} />
                        </dl>
                    </div>
                    <div className="flex justify-end items-center p-4 border-t">
                        <button onClick={onClose} className="bg-blue-600 text-white font-semibold py-2 px-4 rounded-md hover:bg-blue-700">关闭</button>
                    </div>
                </div>
            </div>
        );
    };

    const HostManagement = () => {
        const [allHosts, setAllHosts] = React.useState([]);
        const [displayedHosts, setDisplayedHosts] = React.useState([]);
        const [selectedRows, setSelectedRows] = React.useState([]);
        const [loading, setLoading] = React.useState(true);
        const [currentPage, setCurrentPage] = React.useState(1);
        const [pageSize, setPageSize] = React.useState(5);
        const [isAddModalOpen, setIsAddModalOpen] = React.useState(false);
        const [isViewModalOpen, setIsViewModalOpen] = React.useState(false);
        const [selectedHost, setSelectedHost] = React.useState(null);

        const fetchHosts = async () => {
          setLoading(true);
          try {
            const response = await fetch('http://localhost:5000/api/hosts');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            setAllHosts(data);
          } catch (error) {
            console.error("获取主机列表失败:", error);
            alert(`获取主机列表失败: ${error.message}`);
            setAllHosts([]);
          } finally {
            setLoading(false);
          }
        };

        React.useEffect(() => { fetchHosts(); }, []);
        React.useEffect(() => {
          const paginatedData = allHosts.slice((currentPage - 1) * pageSize, currentPage * pageSize);
          setDisplayedHosts(paginatedData);
        }, [allHosts, currentPage, pageSize]);

        /*
        const deleteHost = (hostId) => {
          if (window.confirm(`确定要删除ID为 ${hostId} 的主机吗？`)) {
            const updatedHosts = allHosts.filter(h => h.id !== hostId);
            setAllHosts(updatedHosts);
            alert('删除成功（模拟）');
          }
        };
*/
        const deleteHost = (hostId) => {
            if (window.confirm(`确定要删除ID为 ${hostId} 的主机吗？`)) {
                fetch('http://localhost:5000/api/hosts/delete', { // API 调用
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: hostId }),
                })
                .then(response => {
                    if (!response.ok) throw new Error('网络响应错误');
                    return response.json();
                })
                .then(data => {
                    alert(data.message || '删除成功');
                    fetchHosts(); // 成功后重新加载数据
                })
                .catch(error => alert(`删除主机失败: ${error.message}`));
            }
        };
 /*       
        const handleAddHostSuccess = (newHostData) => {
            const newHost = { ...newHostData, id: `host-${Date.now()}` };
            setAllHosts([newHost, ...allHosts]);
            alert(`主机 "${newHostData.name}" 添加成功（模拟）`);
            setIsAddModalOpen(false); 
            setCurrentPage(1);
        };
*/
        const handleAddHostSuccess = (newHostData) => {
            fetch('http://localhost:5000/api/hosts/add', { // API 调用
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newHostData),
            })
            .then(response => {
                if (!response.ok) throw new Error('网络响应错误');
                return response.json();
            })
            .then(data => {
                alert(data.message || `主机 "${newHostData.name}" 添加成功`);
                setIsAddModalOpen(false);
                fetchHosts(); // 成功后重新加载数据
            })
            .catch(error => alert(`添加主机失败: ${error.message}`));
        };

        const handleViewHost = (host) => {
          setSelectedHost(host);
          setIsViewModalOpen(true);
        };
        
        const handlePageChange = (newPage) => setCurrentPage(newPage);
        const handlePageSizeChange = (newSize) => { setPageSize(newSize); setCurrentPage(1); };
        const handleSelectAll = (e) => setSelectedRows(e.target.checked ? displayedHosts.map(h => h.id) : []);
        const handleSelectRow = (e, id) => setSelectedRows(e.target.checked ? [...selectedRows, id] : selectedRows.filter(rowId => rowId !== id));

        return (
        <>
            <div className="bg-white p-6 rounded-lg shadow-md">
                <div className="flex justify-between items-center mb-5">
                    <div className="flex items-center space-x-4 text-sm">
                        <span className="text-gray-600">共获取到 {allHosts.length} 条主机信息</span>
                        <div className="flex items-center bg-blue-50 border border-blue-200 text-blue-700 px-3 py-1 rounded-md">
                            <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                            已选择 {selectedRows.length} 项
                        </div>
                        <button onClick={() => setSelectedRows([])} className="bg-white border border-gray-300 text-gray-600 px-4 py-1 rounded-md hover:bg-gray-50">重置条件</button>
                    </div>
                    <div className="flex items-center space-x-3">
                        <button onClick={() => setIsAddModalOpen(true)} className="bg-blue-600 text-white font-semibold py-2 px-4 rounded-md hover:bg-blue-700 transition text-sm flex items-center">
                            <span className="text-lg mr-1">+</span> 添加主机
                        </button>
                        <button onClick={fetchHosts} className="bg-white border border-gray-300 text-gray-700 font-semibold py-2 px-4 rounded-md hover:bg-gray-50 transition text-sm flex items-center">
                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h5M20 20v-5h-5M4 4l5 5M20 20l-5-5"></path></svg>
                            刷新
                        </button>
                    </div>
                </div>
                <div className="overflow-x-auto">
                    <table className="min-w-full text-sm">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="p-3 w-10"><input type="checkbox" onChange={handleSelectAll} checked={selectedRows.length === displayedHosts.length && displayedHosts.length > 0} /></th>
                                <th className="p-3 text-left font-semibold text-gray-600">主机名称</th><th className="p-3 text-left font-semibold text-gray-600">IP地址</th><th className="p-3 text-left font-semibold text-gray-600">SSH登录接口</th><th className="p-3 text-left font-semibold text-gray-600">所属主机组</th><th className="p-3 text-left font-semibold text-gray-600">管理节点</th><th className="p-3 text-left font-semibold text-gray-600">运行状态</th><th className="p-3 text-left font-semibold text-gray-600">操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                            <tr><td colSpan="8" className="p-10 text-center text-gray-500">加载中...</td></tr>
                            ) : (
                            displayedHosts.map(host => (
                                <tr key={host.id} className="border-b hover:bg-gray-50">
                                    <td className="p-3"><input type="checkbox" checked={selectedRows.includes(host.id)} onChange={(e) => handleSelectRow(e, host.id)} /></td>
                                    <td className="p-3 text-gray-800">{host.name}</td><td className="p-3 text-gray-800">{host.ip}</td><td className="p-3 text-gray-800">{host.ssh}</td><td className="p-3 text-gray-800">{host.group}</td><td className="p-3 text-gray-800">{host.isMgmt}</td><td className="p-3 text-gray-800">{host.status}</td>
                                    <td className="p-3 space-x-4">
                                        <a href="#" onClick={(e) => { e.preventDefault(); handleViewHost(host); }} className="text-blue-600 hover:underline">查看</a>
                                        <a href="#" onClick={(e) => { e.preventDefault(); deleteHost(host.id); }} className="text-blue-600 hover:underline">删除</a>
                                    </td>
                                </tr>
                            ))
                            )}
                        </tbody>
                    </table>
                </div>
                <div className="pt-4"><Pagination currentPage={currentPage} totalItems={allHosts.length} pageSize={pageSize} onPageChange={handlePageChange} onPageSizeChange={handlePageSizeChange}/></div>
            </div>
            <AddHostModal isOpen={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} onAddSuccess={handleAddHostSuccess}/>
            <ViewHostModal isOpen={isViewModalOpen} onClose={() => setIsViewModalOpen(false)} host={selectedHost}/>
        </>
        );
    };
    //主机管理页面结束