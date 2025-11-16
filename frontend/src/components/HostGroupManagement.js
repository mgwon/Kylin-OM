//主机组管理页面
    const ViewHostsInGroupModal = ({ isOpen, onClose, group, allHosts }) => {
        if (!isOpen || !group) return null;

        const hostsInGroup = allHosts.filter(host => host.group === group.name);

        return (
            <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50">
                <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl m-4">
                    <div className="p-4 border-b flex justify-between items-center">
                        <h2 className="text-lg font-semibold">拥有主机</h2>
                        <button onClick={onClose} className="text-gray-400 hover:text-gray-800 text-3xl font-light leading-none">×</button>
                    </div>
                    <div className="p-6 max-h-[60vh] overflow-y-auto">
                        <table className="w-full text-left text-sm">
                            <thead className="text-gray-700 border-b">
                                <tr>
                                    <th className="py-2 px-3 font-normal">主机名称</th>
                                    <th className="py-2 px-3 font-normal">IP地址</th>
                                    <th className="py-2 px-3 font-normal">SSH登录接口</th>
                                    <th className="py-2 px-3 font-normal">管理节点</th>
                                </tr>
                            </thead>
                            <tbody>
                                {hostsInGroup.length > 0 ? (
                                    hostsInGroup.map(host => (
                                        <tr key={host.id || host.ip} className="border-b hover:bg-gray-50">
                                            <td className="py-3 px-3">{host.name}</td>
                                            <td className="py-3 px-3">{host.ip}</td>
                                            <td className="py-3 px-3">{host.ssh}</td>
                                            <td className="py-3 px-3">{host.isMgmt}</td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan="4" className="text-center py-10 text-gray-500">该主机组内没有主机。</td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        );
    };
    
    const AddGroupModal = ({ isOpen, onClose, onSubmit }) => {
        if (!isOpen) return null;

        const [groupName, setGroupName] = React.useState('');
        const [description, setDescription] = React.useState('');

        const handleSubmit = () => {
          if (!groupName.trim()) { // 增加 trim() 检查，防止只输入空格
            alert('请输入主机组名称！'); 
            return; 
          }
          // 修正点：formData 中不再包含不存在的 hosts 变量
          const formData = { groupName, description };
          onSubmit(formData);
        };

        return (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl">
              <div className="p-6 border-b"><h3 className="text-xl font-semibold">添加主机组</h3></div>
              <div className="p-6 space-y-4 max-h-[60vh] overflow-y-auto">
                <div><label className="block text-sm font-medium text-gray-700">主机组名称</label><input type="text" value={groupName} onChange={(e) => setGroupName(e.target.value)} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2" /></div>
                <div><label className="block text-sm font-medium text-gray-700">信息描述</label><textarea value={description} onChange={(e) => setDescription(e.target.value)} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"></textarea></div>
              </div>
              <div className="p-6 border-t flex justify-end space-x-2">
                {/* 这两个按钮现在可以正常工作了 */}
                <button onClick={onClose} className="px-4 py-2 border rounded-md text-sm">取消</button>
                <button onClick={handleSubmit} className="px-4 py-2 bg-blue-500 text-white rounded-md text-sm">确认</button>
              </div>
            </div>
          </div>
        );
    }

    const HostGroupManagement = () => {
        const [allGroups, setAllGroups] = React.useState([]);
        const [loading, setLoading] = React.useState(true);
        const [isAddModalOpen, setIsAddModalOpen] = React.useState(false);
        const [currentPage, setCurrentPage] = React.useState(1);
        const [pageSize, setPageSize] = React.useState(5);
        const [selectedGroupIds, setSelectedGroupIds] = React.useState([]);
        const [allHosts, setAllHosts] = React.useState([]);
        const [isViewHostsModalOpen, setIsViewHostsModalOpen] = React.useState(false);
        const [selectedGroupForView, setSelectedGroupForView] = React.useState(null);
        
        const fetchGroupsAndHosts = async () => {
            setLoading(true);
            try {
            const groupPromise = fetch('http://localhost:5000/api/host-groups').then(res => res.json());
            const hostPromise = fetch('http://localhost:5000/api/hosts').then(res => res.json());
            
            const [groupData, hostData] = await Promise.all([groupPromise, hostPromise]);
            setAllGroups(groupData);
            setAllHosts(hostData);

            } catch (error) {
            console.error("获取主机组或主机列表失败:", error);
            alert("加载数据失败，请稍后重试。");
            setAllGroups([]);
            setAllHosts([]);
            } finally {
            setLoading(false);
            }
        };

        React.useEffect(() => {
            fetchGroupsAndHosts();
        }, []);
        
        const currentGroups = allGroups.slice((currentPage - 1) * pageSize, currentPage * pageSize);

        const handlePageChange = (newPage) => setCurrentPage(newPage);
        const handlePageSizeChange = (newSize) => { setPageSize(newSize); setCurrentPage(1); };
        /* 
        const handleFormSubmit = (formData) => {
            const newGroup = { id: `g-${Date.now()}`, name: formData.groupName, hostCount: formData.hosts.length, description: formData.description };
            setAllGroups([newGroup, ...allGroups]);
            setIsAddModalOpen(false);
            alert('主机组添加成功（模拟）');
        };
        */
        const handleFormSubmit = (formData) => {
                fetch('http://localhost:5000/api/host-groups/add', { // API 调用
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData),
                })
                .then(response => {
                    if (!response.ok) throw new Error('网络响应错误');
                    return response.json();
                })
                .then(data => {
                    alert(data.message || '主机组添加成功');
                    setIsAddModalOpen(false);
                    fetchGroupsAndHosts(); // 重新加载数据
                })
                .catch(error => alert(`添加主机组失败: ${error.message}`));
            };
        
        const handleViewHostsInGroup = (group) => {
            setSelectedGroupForView(group);
            setIsViewHostsModalOpen(true);
        };
    /*
        const handleDelete = (group) => {
            if(window.confirm(`确认删除主机组 "${group.name}"?`)) {
            const updatedGroups = allGroups.filter(g => g.id !== group.id);
            setAllGroups(updatedGroups);
            setSelectedGroupIds(ids => ids.filter(id => id !== group.id));
            alert('删除成功（模拟）');
            }
        };
        */
        const handleDelete = (group) => {
                if(window.confirm(`确认删除主机组 "${group.name}"?`)) {
                    fetch('http://localhost:5000/api/host-groups/delete', { // API 调用
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ id: group.id }),
                    })
                    .then(response => {
                        if (!response.ok) throw new Error('网络响应错误');
                        return response.json();
                    })
                    .then(data => {
                        alert(data.message || '删除成功');
                        fetchGroupsAndHosts(); // 重新加载数据
                    })
                    .catch(error => alert(`删除主机组失败: ${error.message}`));
                }
            };
        const handleSelectRow = (e, id) => setSelectedGroupIds(e.target.checked ? [...selectedGroupIds, id] : selectedGroupIds.filter(rowId => rowId !== id));
        const handleSelectAll = (e) => setSelectedGroupIds(e.target.checked ? currentGroups.map(g => g.id) : []);
        const handleResetSelection = () => { setSelectedGroupIds([]); };
        
        return (
            <>
            <div className="bg-white p-6 rounded-lg shadow-md">
                <div className="flex justify-between items-start mb-5">
                <div className="flex flex-col space-y-3 text-sm">
                    <span className="text-gray-600">共获取到 {allGroups.length} 条主机组信息</span>
                    <div className="flex items-center space-x-4">
                    <div className="flex items-center bg-blue-50 border border-blue-200 text-blue-700 px-3 py-1 rounded-md">
                        <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                        已选择 {selectedGroupIds.length} 项
                    </div>
                    <button onClick={handleResetSelection} className="bg-white border border-gray-300 text-gray-600 px-4 py-1 rounded-md hover:bg-gray-50">
                        重置条件
                    </button>
                    </div>
                </div>
                <div className="flex items-center space-x-3">
                    <button onClick={() => setIsAddModalOpen(true)} className="bg-blue-600 text-white font-semibold py-2 px-4 rounded-md hover:bg-blue-700 transition text-sm flex items-center">
                    <span className="text-lg mr-1">+</span> 添加主机组
                    </button>
                    <button onClick={fetchGroupsAndHosts} className="bg-white border border-gray-300 text-gray-700 font-semibold py-2 px-4 rounded-md hover:bg-gray-50 transition text-sm flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h5M20 20v-5h-5M4 4l5 5M20 20l-5-5"></path></svg>
                    刷新
                    </button>
                </div>
                </div>
                <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                    <thead className="bg-gray-50">
                    <tr>
                        <th className="p-3 w-10"><input type="checkbox" onChange={handleSelectAll} checked={selectedGroupIds.length === currentGroups.length && currentGroups.length > 0} /></th>
                        <th className="p-3 text-left font-semibold text-gray-600">主机组</th>
                        <th className="p-3 text-left font-semibold text-gray-600">拥有主机数</th>
                        <th className="p-3 text-left font-semibold text-gray-600">信息描述</th>
                        <th className="p-3 text-left font-semibold text-gray-600">操作</th>
                    </tr>
                    </thead>
                    <tbody>
                    {loading ? (
                        <tr><td colSpan="5" className="p-10 text-center text-gray-500">加载中...</td></tr>
                    ) : (
                        currentGroups.map(item => (
                        <tr key={item.id} className="border-b hover:bg-gray-50">
                            <td className="p-3"><input type="checkbox" checked={selectedGroupIds.includes(item.id)} onChange={(e) => handleSelectRow(e, item.id)}/></td>
                            <td className="p-3 text-gray-800">{item.name}</td>
                            <td className="p-3 text-gray-800">{item.hostCount}</td>
                            <td className="p-3 text-gray-800">{item.description}</td>
                            <td className="p-3 space-x-4">
                            <a href="#" onClick={(e) => {e.preventDefault(); handleDelete(item)}} className="text-blue-600 hover:underline">删除</a>
                            <a href="#" onClick={(e) => { e.preventDefault(); handleViewHostsInGroup(item); }} className="text-blue-600 hover:underline">组内主机</a>
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
                    totalItems={allGroups.length}
                    pageSize={pageSize}
                    onPageChange={handlePageChange}
                    onPageSizeChange={handlePageSizeChange}
                    />
                </div>
            </div>
            <AddGroupModal 
                isOpen={isAddModalOpen} 
                onClose={() => setIsAddModalOpen(false)} 
                onSubmit={handleFormSubmit} 
            />
            <ViewHostsInGroupModal
                isOpen={isViewHostsModalOpen}
                onClose={() => setIsViewHostsModalOpen(false)}
                group={selectedGroupForView}
                allHosts={allHosts}
            />
            </>
        );
        }
    //主机组管理页面结束