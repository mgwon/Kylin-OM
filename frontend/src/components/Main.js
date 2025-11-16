const directoryStructure = [
      { name: '工作台' }, { name: 'LLM界面' },
      { name: '资产管理', subSections: [{ name: '主机管理' }, { name: '主机组管理' }, { name: '资产监控' }, { name: '资产日志' }, { name: '资产备份及恢复' }] },
      { name: '安全中心', subSections: [{ name: 'CVEs' }, { name: '主机列表' }, { name: '漏洞修复记录' }] },
      { name: '故障中心', subSections: [{ name: '工作流' }, { name: '告警' }, { name: '故障监控及分析' }, { name: '故障修复记录' }] },
      { name: '配置溯源' }, { name: '架构感知' },
    ];

    const Header = ({ onToggleSidebar }) => {
      return (
        <header className="bg-white text-gray-700 border-b border-gray-300 shadow-sm p-4 flex justify-between items-center tracking-wide leading-loose relative">
          <div className="flex items-center">
            <img src="../src/assets/Kylin.png" alt="Kylin" className="h-10 mr-2" />
            <span className="mr-2">Kylin-OM</span>
            <button onClick={onToggleSidebar} className="absolute left-60">☰</button>
          </div>
          <div className="flex items-center">
            <span className="mr-2">用户</span>
            <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
          </div>
        </header>
      );
    };

    const Sidebar = ({ directoryStructure, onMenuClick, isHidden, selectedPath }) => {
        const [expandedItems, setExpandedItems] = React.useState({});
        const toggleExpand = (itemName) => { setExpandedItems((prev) => ({ ...prev, [itemName]: !prev[itemName] })); };
        return (
            <aside className={`bg-white w-64 border-r border-gray-300 shadow-inner p-4 h-full overflow-auto space-y-3 ${isHidden ? 'hidden' : ''}`}>
            {directoryStructure.map((item) => (
                <MenuItem key={item.name} item={item} path={[]} onMenuClick={onMenuClick} isExpanded={expandedItems[item.name] || false} toggleExpand={toggleExpand} selectedPath={selectedPath} />
            ))}
            </aside>
        );
    };

    const MenuItem = ({ item, path, onMenuClick, isExpanded, toggleExpand, selectedPath }) => {
      const currentPath = [...path, item.name];
      const isSelected = selectedPath.join('/') === currentPath.join('/');
      const hasSubSections = item.subSections && item.subSections.length > 0;
      return (
        <div className="mb-1 ml-6">
          {hasSubSections ? (
            <div>
              <div className={`text-gray-700 cursor-pointer flex justify-between items-center ${isSelected ? 'text-blue-600 bg-blue-100 px-3 rounded' : ''} tracking-wide leading-loose`} onClick={() => toggleExpand(item.name)}>
                {item.name}
                <span>{isExpanded ? '︿' : '﹀'}</span>
              </div>
              {isExpanded && (<div className="ml-1">
                  {item.subSections.map((subItem) => ( <MenuItem key={subItem.name} item={subItem} path={currentPath} onMenuClick={onMenuClick} isExpanded={false} toggleExpand={toggleExpand} selectedPath={selectedPath} /> ))}
                </div>)}
            </div>
          ) : ( <div className={`text-gray-700 cursor-pointer ${isSelected ? 'text-blue-600 bg-blue-100 p-1 rounded' : 'hover:underline'} tracking-wide leading-loose`} onClick={() => onMenuClick(currentPath)}> {item.name} </div> )}
        </div>
      );
    };
    
    const Pagination = ({ currentPage, totalItems, pageSize, onPageChange, onPageSizeChange, options = [5, 10, 20] }) => {
        const totalPages = Math.ceil(totalItems / pageSize);
        const handlePageClick = (page) => { if (page >= 1 && page <= totalPages) { onPageChange(page); } };
        return (
            <div className="flex justify-end items-center space-x-2 text-sm">
                <button onClick={() => handlePageClick(currentPage - 1)} disabled={currentPage === 1} className="px-2 py-1 border rounded-md bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">&lt;</button>
                <span className="px-3 py-1 border border-blue-500 bg-blue-50 text-blue-600 rounded-md font-semibold">{currentPage}</span>
                <button onClick={() => handlePageClick(currentPage + 1)} disabled={currentPage === totalPages || totalItems === 0} className="px-2 py-1 border rounded-md bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">&gt;</button>
                <select value={pageSize} onChange={(e) => onPageSizeChange(Number(e.target.value))} className="border rounded-md bg-white p-1 focus:outline-none focus:ring-1 focus:ring-blue-500">
                    {options.map(size => ( <option key={size} value={size}>{size} / 页</option>))}
                </select>
            </div>
        );
    };

    const MainContent = ({ selectedPath, allRepairRecords, setAllRepairRecords, onAddRepairRecord, onOpenExplanationModal}) => {
        const sectionName = selectedPath.length > 0 ? selectedPath[selectedPath.length - 1] : '请选择一个目录';
        const [viewedHost, setViewedHost] = React.useState(null);
        React.useEffect(() => { setViewedHost(null); }, [selectedPath]);
        const onViewHostDetails = (host) => { setViewedHost(host); };
        const onReturnToList = () => { setViewedHost(null); };

        const renderContent = () => {
            switch(sectionName) {
                case '工作台': 
                    return <Workbench />;
                case 'LLM界面': 
                    return <LLMInterface />;
                case '主机管理': 
                    return <HostManagement />;
                case '主机组管理': 
                    return <HostGroupManagement />;
                case '资产日志': 
                    return <AssetLogs onOpenExplanationModal={onOpenExplanationModal}/>;
                case '资产监控': 
                    return <AssetMonitoringReport />;
                case '资产备份及恢复': 
                    return <AssetBackupAndRestore />;
                case 'CVEs': 
                    return <CVEsManagement onAddRepairRecord={onAddRepairRecord} />;
                case '漏洞修复记录': 
                    return <VulnerabilityRepairRecords allRecordsProp={allRepairRecords} setAllRecordsProp={setAllRepairRecords} />;
                case '主机列表':
                    if (viewedHost) {
                        return <HostDetailPage host={viewedHost} onReturnToList={onReturnToList} onAddRepairRecord={onAddRepairRecord} />;
                    }
                    return <VulnerabilityHostListPage onViewHostDetails={onViewHostDetails} />;
                case '工作流': 
                    return <WorkflowManagement />;
                case '告警': 
                    return <AlarmsPage />;
                case '故障监控及分析':
                    return <FaultMonitoringAnalysis />;
                case '故障修复记录': 
                    return <FaultRepairRecords />;
                case '配置溯源': 
                    return <ConfigurationTracing />;
                case '架构感知': 
                    return <ArchitecturePerception />;
                default:
                    return (<div className="bg-white h-full p-4 border border-gray-300 rounded-lg"><p>这里是“{sectionName}”页面的内容。</p></div>);
            }
        }
        return (
            <main className="flex-1 bg-white p-4 tracking-wide leading-loose overflow-y-auto">
            <Breadcrumb path={selectedPath} />
            <h1 className="text-2xl font-bold mb-4">{sectionName}</h1>
            <div className="bg-blue-50 h-full p-4 border border-gray-300 rounded-lg">
                {renderContent()}
                </div>
            </main>
        );
    };

    const Breadcrumb = ({ path }) => {
        return ( <div className="text-gray-500 mb-2 tracking-wide leading-loose">{path.length > 0 ? path.join(' / ') : '主页'}</div> );
    };

    const App = () => {
        const [selectedPath, setSelectedPath] = React.useState(['工作台']);
        const [isSidebarHidden, setIsSidebarHidden] = React.useState(false);
        const [allRepairRecords, setAllRepairRecords] = React.useState(null);
        
        const [isExplanationModalOpen, setIsExplanationModalOpen] = React.useState(false);
        const [logToExplain, setLogToExplain] = React.useState(null);

        React.useEffect(() => {
            const fetchInitialRecords = async () => {
                try {
                    const response = await fetch('/static/api/vulnerability-records/list.txt');
                    if (response.ok) {
                        const data = await response.json();
                        setAllRepairRecords(data);
                    } else { 
                        setAllRepairRecords([]);
                    }
                } catch (error) {
                    console.error("在App组件中预加载修复记录失败:", error);
                    setAllRepairRecords([]);
                }
            };
            fetchInitialRecords();
        }, []);

        const handleMenuClick = (path) => {
            setSelectedPath(path);
        };

        const toggleSidebar = () => {
            setIsSidebarHidden(prev => !prev);
        };

        const handleAddRepairRecord = (newTask) => {
            setAllRepairRecords(prevRecords => [newTask, ...(prevRecords || [])]);
            setSelectedPath(['安全中心', '漏洞修复记录']);
            alert('修复任务已成功创建！将为您跳转到任务列表。');
        };

        const handleOpenExplanationModal = (logObject) => {
            setLogToExplain(logObject);
            setIsExplanationModalOpen(true);
        };

        const handleCloseExplanationModal = () => {
            setIsExplanationModalOpen(false);
            setLogToExplain(null);
        };

        if (allRepairRecords === null) {
            return <div className="text-center p-20 text-lg">正在初始化应用...</div>;
        }

        return (
            <div className="flex flex-col h-screen">
                <Header onToggleSidebar={toggleSidebar} />
                <div className="flex flex-1 overflow-hidden">
                    <Sidebar 
                        directoryStructure={directoryStructure} 
                        onMenuClick={handleMenuClick} 
                        isHidden={isSidebarHidden} 
                        selectedPath={selectedPath} 
                    />
                    <MainContent 
                        selectedPath={selectedPath} 
                        allRepairRecords={allRepairRecords} 
                        setAllRepairRecords={setAllRepairRecords} 
                        onAddRepairRecord={handleAddRepairRecord} 
                        onOpenExplanationModal={handleOpenExplanationModal} 
                    />
                </div>
                {isExplanationModalOpen && (
                    <LogExplanationInterface 
                        log={logToExplain}
                        onClose={handleCloseExplanationModal}
                    />
                )}
            </div>
        );
    };

    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(<App />);
