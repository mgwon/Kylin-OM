//LLM界面页面
    const LLMInterface = () => {
        // --- 1. 状态管理 (State Management) ---
        const ws = React.useRef(null);
        const messagesEndRef = React.useRef(null);

        const [messages, setMessages] = React.useState([]);
        const [inputValue, setInputValue] = React.useState('');
        const [quickActions, setQuickActions] = React.useState([]);
        const [sessionId, setSessionId] = React.useState(null);
        const [isConnected, setIsConnected] = React.useState(false);
        const [isTaskRunning, setIsTaskRunning] = React.useState(false);
        const [confirmDialog, setConfirmDialog] = React.useState({ isOpen: false, message: '', operationId: null });
        

        const [isHistoryPanelOpen, setIsHistoryPanelOpen] = React.useState(false);
        const [history, setHistory] = React.useState([]); // 用于存储历史会话
        const [isModelModalOpen, setIsModelModalOpen] = React.useState(false);
        const [modelServerUrl, setModelServerUrl] = React.useState('http://localhost:11434'); // 默认模型服务器地址

        // --- 2. 效果与副作用 (Effects & Side Effects) ---
        React.useEffect(() => {
            messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
        }, [messages]);
        
        React.useEffect(() => {
            connect();
            // 加载本地存储的历史记录
            const savedHistory = JSON.parse(localStorage.getItem('kylin_om_history') || '[]');
            setHistory(savedHistory);
            
            return () => { // 组件卸载时断开连接
                if (ws.current) ws.current.close();
            };
        }, []);

        // 当会话结束时，保存历史记录
        React.useEffect(() => {
            if (!isTaskRunning && messages.length > 1 && sessionId) {
                const sessionExists = history.some(h => h.id === sessionId);
                const newHistoryEntry = {
                    id: sessionId,
                    title: messages.find(m => m.agent === 'user')?.content.substring(0, 20) || '无标题对话',
                    messages: messages,
                    timestamp: new Date().toISOString()
                };

                let updatedHistory;
                if (sessionExists) {
                    updatedHistory = history.map(h => h.id === sessionId ? newHistoryEntry : h);
                } else {
                    updatedHistory = [newHistoryEntry, ...history];
                }
                setHistory(updatedHistory);
                localStorage.setItem('kylin_om_history', JSON.stringify(updatedHistory));
            }
        }, [isTaskRunning]);


        // --- 3. WebSocket 核心逻辑 ---
        const connect = () => {
            // 后端端口是 8003，端点是 /ws/chat
            const wsUrl = `ws://localhost:8003/ws/chat`;
            const socket = new WebSocket(wsUrl);
            ws.current = socket;

            socket.onopen = () => {
                setIsConnected(true);
                // 清空旧消息，显示连接成功
                setMessages([{ agent: 'system', content: '已成功连接到智能助理。', timestamp: new Date().toLocaleTimeString() }]);
            };
            socket.onclose = () => {
                if (isConnected) {
                    addMessage('error', '与服务器的连接已断开，请刷新页面重试。');
                }
                setIsConnected(false);
                setIsTaskRunning(false); // 使用旧的状态名，但逻辑更新
            };
            socket.onerror = () => {
                addMessage('error', '无法连接到服务器。请确保后端服务在 8003 端口上运行。');
                setIsConnected(false);
            };
            socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleServerMessage(data); // 交给新的消息处理器
            };
        };
        const handleServerMessage = (data) => {
            const agent = data.source || 'system';

				if (agent.toLowerCase() === 'user') {
					return; // 直接退出函数，不进行任何处理
				}

            const content = data.content || '';

            switch(data.type) {
                case 'streaming_start':
                    // 当流开始时，添加一条新消息，并标记为 'stream'
                    addMessage(agent, content, 'stream');
                    setIsTaskRunning(true);
                    break;

                case 'streaming_update':
                    // 更新最后一条正在“流式”传输的消息
                    setMessages(prev => {
                        const lastMessage = prev[prev.length - 1];
                        // 确保我们只更新属于同一个 agent 的流消息
                        if (lastMessage && lastMessage.type === 'stream' && lastMessage.agent === agent) {
                            const updatedMessage = { ...lastMessage, content: content };
                            return [...prev.slice(0, -1), updatedMessage];
                        }
                        return prev;
                    });
                    break;
                
                case 'streaming_end':
                    // 当流结束时，将最后一条消息的类型从 'stream' 改为 'message'
                    setMessages(prev => {
                        const lastMessage = prev[prev.length - 1];
                        if (lastMessage && lastMessage.type === 'stream' && lastMessage.agent === agent) {
                            const finalMessage = { ...lastMessage, content: content, type: 'message' };
                            return [...prev.slice(0, -1), finalMessage];
                        }
                        return prev;
                    });
                    // 注意：流结束不代表整个任务结束，所以不设置 setIsTaskRunning(false)
                    break;

                case 'task_completed':
                    // 整个任务完成，可以再次输入
                    addMessage('system', content);
                    setIsTaskRunning(false); // 启用输入框
                    break;

                case 'UserInputRequestedEvent':
                    // 后端请求用户输入
                    addMessage(agent, content);
                    setIsTaskRunning(false); // 启用输入框让用户回答
                    break;
                
                case 'error':
                    addMessage('error', content, 'error');
                    setIsTaskRunning(false); // 出现错误，允许用户重试
                    break;

                default:
                    // 处理非流式、非事件的普通消息
                    if (content) {
                        addMessage(agent, content, 'message');
                    }
                    break;
            }
        };

        // --- 4. API & 事件处理函数 ---
        const addMessage = (agent, content, type = 'message') => {
            const newMessage = { 
                agent: agent.toLowerCase(), 
                content, 
                type, 
                timestamp: new Date().toLocaleTimeString() 
            };
            setMessages(prev => [...prev, newMessage]);
        };

        const sendWebSocketMessage = (payload) => {
            if (ws.current && ws.current.readyState === WebSocket.OPEN) {
                ws.current.send(JSON.stringify(payload));
            } else {
                addMessage('error', '连接已断开，无法发送消息。');
            }
        };

        const fetchQuickActions = async (serverUrl) => {
            try {
                const response = await fetch(`http://${serverUrl}/api/quick-actions`);
                const data = await response.json();
                setQuickActions(data.actions); 
            } catch (error) { console.error("获取快捷操作失败:", error); }
        };
        
        const handleSendMessage = () => {
            const content = inputValue.trim();
            if (!content) return;
            addMessage('user', content);

            // 构造符合后端 TextMessage 格式的消息
            const messagePayload = {
                content: content,
                role: 'user',// 必须包含 role 字段
					source: 'user'
            };

            sendWebSocketMessage(messagePayload);
            setInputValue('');
            setIsTaskRunning(true); // 发送后禁用输入框
        };
        
        const handleInterruptTask = () => sendWebSocketMessage({ type: 'interrupt', reason: '用户手动中断' });

        const handleLoadHistory = (session) => {
            setSessionId(session.id);
            setMessages(session.messages);
            setIsHistoryPanelOpen(false);
        };

        const handleNewChat = () => {
            setMessages([]);
            setSessionId(null);
            if (ws.current) ws.current.close(); // 断开旧连接
            setTimeout(connect, 100); // 延迟一小会再建立新连接
        };

        // --- 5. UI 渲染 (Rendering) ---
        return (
            <div className="relative flex flex-col h-full w-full bg-white rounded-lg shadow-sm overflow-hidden">
                {/* 右上角历史记录按钮 */}
                <div className="absolute top-4 right-4 z-10">
                    <button onClick={() => setIsHistoryPanelOpen(true)} className="p-2 bg-gray-100 hover:bg-gray-200 rounded-full" title="历史会话">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    </button>
                </div>
                
                {/* 聊天主界面 */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {/* ... (聊天消息渲染逻辑，与上一版相同) ... */}
                    {messages.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
                            <img src="../src/assets/Kylin.png" alt="Kylin" className="w-24 h-24 mb-4" />
                            <h2 className="text-3xl font-semibold text-gray-800">Kylin-OM 智能助手</h2>
                            {!isConnected && <p className="mt-2 animate-pulse">正在连接服务器...</p>}
                        </div>
                    ) : (
                        messages.map((msg, index) => (
                            <div key={index} className={`flex items-start gap-3 ${msg.agent === 'user' ? 'justify-end' : ''}`}>
                                {msg.agent !== 'user' && <img src="../src/assets/Kylin.png" className="w-8 h-8 rounded-full flex-shrink-0" alt="AI Avatar" />}
                                <div className={`max-w-3xl p-3 rounded-lg shadow-sm ${
                                    msg.agent === 'user' ? 'bg-blue-600 text-white' : 
                                    msg.agent === 'system' ? 'bg-yellow-100 text-yellow-800' :
                                    msg.type === 'error' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
                                }`}>
                                    <p className="font-bold text-xs capitalize mb-1">{msg.agent} <span className="font-normal text-gray-500">{msg.timestamp}</span></p>
                                    <div className="text-sm prose max-w-none" style={{whiteSpace: 'pre-wrap'}}>{msg.content}</div>
                                </div>
                            </div>
                        ))
                    )}
                    <div ref={messagesEndRef} />
                </div>
                
                {/* 输入区 */}
                <div className="p-4 pt-2 border-t border-gray-200 bg-white">
                    {/* 快捷操作按钮 */}
                    {!isTaskRunning && isConnected && quickActions.length > 0 && (
                        <div className="flex flex-wrap gap-2 mb-3">
                            {quickActions.map(action => (
                                <button key={action.id} onClick={() => handleQuickAction(action)} title={action.description} className="px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm rounded-full transition-colors">
                                    {action.name}
                                </button>
                            ))}
                        </div>
                    )}
                    <div className="relative flex items-center gap-2">
                        {/* 模型选择按钮 */}
                        <button onClick={() => setIsModelModalOpen(true)} className="flex-shrink-0 flex items-center gap-1 px-3 py-3 bg-gray-100 hover:bg-gray-200 rounded-lg" title="切换模型服务器">
                            <span className="text-sm text-gray-700">默认模型</span>
                            <svg className="w-4 h-8 text-gray-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" /></svg>
                        </button>
                        
                        {/* 主输入框 */}
                        <div className="relative flex-1">
                            <textarea
                                className="w-full pl-4 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none transition"
                                placeholder={!isConnected ? "正在连接服务器..." : "有何疑问，尽管问... (Enter 发送, Shift+Enter 换行)"}
                                value={inputValue}
                                onChange={e => setInputValue(e.target.value)}
                                onKeyDown={e => {
                                    if (e.key === 'Enter' && !e.shiftKey) { 
                                        e.preventDefault(); 
                                        handleSendMessage(); 
                                    }
                                }}
                                rows="1"
                                disabled={!isConnected || isTaskRunning}
                            />
                            <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center">
                                {isTaskRunning ? (
                                    <button onClick={handleInterruptTask} className="bg-gray-700 hover:bg-black text-white rounded-full w-8 h-8 flex items-center justify-center transition-colors" title="停止回答">
                                        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M6 6h12v12H6z" /></svg>
                                    </button>
                                ) : (
                                    <button onClick={handleSendMessage} disabled={!isConnected || !inputValue.trim()} className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white rounded-full w-8 h-8 flex items-center justify-center transition-colors" title="发送">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor"><path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" /></svg>
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* 历史会话侧边栏 */}
                <div className={`absolute top-0 right-0 h-full w-80 bg-white border-l border-gray-200 shadow-lg transform transition-transform z-20 ${isHistoryPanelOpen ? 'translate-x-0' : 'translate-x-full'}`}>
                    <div className="flex flex-col h-full">
                        <div className="flex items-center justify-between p-4 border-b">
                            <h3 className="font-semibold">历史会话</h3>
                            <button onClick={() => setIsHistoryPanelOpen(false)} className="p-1 hover:bg-gray-100 rounded-full">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
                            </button>
                        </div>
                        <div className="flex-1 overflow-y-auto p-2">
                            <button onClick={handleNewChat} className="w-full text-left p-2 mb-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                                + 新建对话
                            </button>
                            {history.map(session => (
                                <div key={session.id} onClick={() => handleLoadHistory(session)} className="p-2 rounded cursor-pointer hover:bg-gray-100">
                                    <p className="text-sm font-medium truncate">{session.title}</p>
                                    <p className="text-xs text-gray-500">{new Date(session.timestamp).toLocaleString()}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
                
                {/* 模型配置弹窗 */}
                {isModelModalOpen && (
                    <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                        <div className="bg-white p-6 rounded-lg shadow-xl w-full max-w-md">
                            <h3 className="text-lg font-bold mb-4">配置模型服务器</h3>
                            <label className="text-sm">Ollama 服务器地址:</label>
                            <input type="text" value={modelServerUrl} onChange={e => setModelServerUrl(e.target.value)} className="w-full p-2 border rounded mt-1" placeholder="例如: http://192.168.1.10:11434"/>
                            <div className="flex justify-end gap-4 mt-4">
                                <button onClick={() => setIsModelModalOpen(false)} className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300">取消</button>
                                <button onClick={() => { alert('模型地址已更新！新对话将使用此地址。'); setIsModelModalOpen(false); }} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">保存</button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        );
    };
