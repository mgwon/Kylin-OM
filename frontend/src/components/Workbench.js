const Workbench = () => {
        const [summary, setSummary] = React.useState(null);
        const [stats, setStats] = React.useState([]);
        const [records, setRecords] = React.useState([]);
        const [loading, setLoading] = React.useState(true);
        const [isModalOpen, setIsModalOpen] = React.useState(false);

        React.useEffect(() => {
            const fetchData = async () => {
            setLoading(true);
            try {
                const API_BASE_URL = 'http://localhost:5000';

                // MODIFIED: Update fetch URLs to point to the new backend
                const summaryPromise = fetch(`${API_BASE_URL}/api/workbench/summary`).then(res => res.json());
                const recordsPromise = fetch(`${API_BASE_URL}/api/workbench/records`).then(res => res.json());
                const [summaryData, recordsData] = await Promise.all([
                summaryPromise,
                recordsPromise
                ]);

                const hostErrorCounts = recordsData.reduce((acc, record) => {
                const { hostname, ip } = record;
                if (!acc[hostname]) {
                    acc[hostname] = { errors: 0, ip: ip };
                }
                acc[hostname].errors += 1;
                return acc;
                }, {});

                const generatedStats = Object.entries(hostErrorCounts)
                .map(([hostname, data]) => ({
                    hostname: hostname,
                    ip: data.ip,
                    errors: data.errors,
                }))
                .sort((a, b) => b.errors - a.errors)
                .map((stat, index) => ({
                    ...stat,
                    rank: index + 1,
                }));
                
                setSummary(summaryData);
                setRecords(recordsData);
                setStats(generatedStats);
            } catch (error) {
                console.error("获取工作台数据失败:", error);
                alert("获取工作台数据失败，请检查后端接口或网络连接。");
            } finally {
                setLoading(false);
            }
            };
            fetchData();
        }, []);
        
        if (loading) {
            return <div className="text-center p-10">正在加载工作台数据...</div>;
        }
        
        const radius = 15.9155;
        const circumference = 2 * Math.PI * radius;

        return (
            <React.Fragment>
            { summary && (
            <div className="space-y-6">
                {/* Top Cards Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Left Cards */}
                <div className="space-y-6">
                    <div className="bg-white p-6 rounded-lg shadow-md flex items-center justify-between">
                    <div><p className="text-gray-500">主机数量</p><p className="text-4xl font-bold">{summary.hostCount}</p></div>
                    <div className="text-3xl">💻</div>
                    </div>
                    <div className="bg-white p-6 rounded-lg shadow-md flex items-center justify-between">
                    <div><p className="text-gray-500">异常检测规则数量</p><p className="text-4xl font-bold">{summary.ruleCount}</p></div>
                    <div className="text-3xl">🛡️</div>
                    </div>
                </div>
                
                {/* Middle Donut Chart Card */}
                <div className="bg-white p-6 rounded-lg shadow-md flex items-center justify-center space-x-6">
                    <div className="relative w-32 h-32 flex-shrink-0">
                        <svg className="w-full h-full" viewBox="0 0 36 36"><circle className="text-gray-200" stroke="currentColor" strokeWidth="4" fill="transparent" r={radius} cx="18" cy="18"/><circle className="text-blue-500" stroke="currentColor" strokeWidth="4" strokeDasharray={`${(summary.syncRate / 100) * circumference}, ${circumference}`} strokeLinecap="round" fill="transparent" r={radius} cx="18" cy="18" style={{transform: 'rotate(-90deg)', transformOrigin: '50% 50%'}}/></svg>
                    </div>
                    <div className="space-y-4">
                        <div><div className="flex items-center space-x-2"><span className="w-2.5 h-2.5 bg-blue-500 rounded-full"></span><span className="text-gray-600">业务域同步率</span></div><p className="text-4xl font-bold text-gray-800 mt-1">{summary.syncRate}%</p></div>
                        <div><div className="flex items-center space-x-2"><span className="w-2.5 h-2.5 bg-red-500 rounded-full"></span><span className="text-gray-600">未同步业务域</span></div><p className="text-4xl font-bold text-gray-800 mt-1">{summary.unsyncedDomains.toLocaleString()}</p></div>
                    </div>
                </div>

                {/* Right List Card with "View All" button */}
                <div className="bg-white rounded-lg shadow-md relative overflow-hidden">
                    <div className="p-6 pr-16">
                        <h3 className="font-bold mb-4">异常检测结果统计</h3>
                        <div className="flex justify-between text-sm text-gray-500 mb-2">
                            <span>排名 主机名/IP地址</span>
                            <span>异常数</span>
                        </div>
                        <ul className="space-y-4 h-32 overflow-y-auto pr-2">
                            {stats.map(stat => (
                                <li key={stat.rank} className="flex items-center justify-between">
                                    <div className="flex items-center"><span className="bg-blue-500 text-white w-5 h-5 flex items-center justify-center rounded-full text-sm mr-3">{stat.rank}</span><div><p className="font-semibold">{stat.hostname}</p><p className="text-sm text-gray-500">{stat.ip}</p></div></div>
                                    <span className="text-red-500 font-bold">{stat.errors}项</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                    <button onClick={() => setIsModalOpen(true)} className="absolute top-0 right-0 h-full bg-blue-500 hover:bg-blue-600 text-white flex flex-col justify-center items-center w-12 cursor-pointer space-y-2 py-4">
                        {'查看全部结果'.split('').map(char => <span key={char}>{char}</span>)}
                    </button>
                </div>
                </div>

                {/* Bottom Table */}
                <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="font-bold mb-4">异常检测记录</h3>
                <table className="w-full text-left text-sm">
                    <thead className="text-gray-500 border-b"><tr><th className="py-2 px-3">序号</th><th className="py-2 px-3">主机名称</th><th className="py-2 px-3">IP地址</th><th className="py-2 px-3">检测项</th><th className="py-2 px-3">检测条件</th><th className="py-2 px-3">描述</th><th className="py-2 px-3">检测时间段</th></tr></thead>
                    <tbody>
                        {[...records]
                            .sort((a, b) => new Date(b.timestamp.split(' 至 ')[1]) - new Date(a.timestamp.split(' 至 ')[1]))
                            .slice(0, 3)
                            .map(record => (
                            <tr key={record.id} className="border-b hover:bg-gray-50">
                                <td className="py-3 px-3">{record.id}</td>
                                <td className="py-3 px-3">{record.hostname}</td>
                                <td className="py-3 px-3">{record.ip}</td>
                                <td className="py-3 px-3 font-mono text-green-600">{record.checkItem}</td>
                                <td className="py-3 px-3 font-mono">{record.condition}</td>
                                <td className="py-3 px-3">{record.description}</td>
                                <td className="py-3 px-3">{record.timestamp}</td>
                            </tr>
                        ))}
                        </tbody>
                </table>
                </div>
            </div>
            )}

            {isModalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50 transition-opacity">
                <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl m-4">
                    <div className="p-6 border-b flex justify-between items-center">
                    <h2 className="text-xl font-bold">全部异常具体信息</h2>
                    <button onClick={() => setIsModalOpen(false)} className="text-gray-400 hover:text-gray-800 text-3xl font-light leading-none">×</button>
                    </div>
                    <div className="p-6 max-h-[70vh] overflow-y-auto">
                    <table className="w-full text-left text-sm">
                        <thead className="text-gray-500 border-b bg-gray-50 sticky top-0"><tr><th className="py-2 px-3">序号</th><th className="py-2 px-3">主机名称</th><th className="py-2 px-3">IP地址</th><th className="py-2 px-3">检测项</th><th className="py-2 px-3">检测条件</th><th className="py-2 px-3">描述</th><th className="py-2 px-3">检测时间段</th></tr></thead>
                        <tbody>
                        {records.map(record => (
                            <tr key={record.id} className="border-b hover:bg-gray-50"><td className="py-3 px-3">{record.id}</td><td className="py-3 px-3">{record.hostname}</td><td className="py-3 px-3">{record.ip}</td><td className="py-3 px-3 font-mono text-green-600">{record.checkItem}</td><td className="py-3 px-3 font-mono">{record.condition}</td><td className="py-3 px-3">{record.description}</td><td className="py-3 px-3">{record.timestamp}</td></tr>
                        ))}
                        </tbody>
                    </table>
                    </div>
                </div>
                </div>
            )}
            </React.Fragment>
        );
        }