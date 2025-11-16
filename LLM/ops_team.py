import json
import logging
import os
from typing import Any, Awaitable, Callable, Optional, Sequence
import asyncio
from datetime import datetime

import aiofiles
import yaml
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import TextMessage, UserInputRequestedEvent, ModelClientStreamingChunkEvent, ThoughtEvent, StopMessage
from autogen_agentchat.teams import Swarm
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
from autogen_core import CancellationToken
from autogen_core.models import ChatCompletionClient

from monitoring_tools import search_monitoring_data
from script_executor import execute_script_remotely, execute_script_locally
from host_management_tools import (
    list_hosts_and_groups, add_host_to_group, remove_host_from_group, 
    update_host_info, add_host_group, remove_host_group, 
    check_host_connectivity, get_hosts_by_group, search_hosts_by_criteria
)
from process_monitor import get_process_monitoring_report

logger = logging.getLogger(__name__)

model_config_path = "model_config.yaml"
state_path = "ops_team_state.json"

# =============================================================================
# 自定义终止条件 - 忽略thinking内容
# =============================================================================

class ThinkingFilteredTextMentionTermination(TextMentionTermination):
    """忽略ThoughtEvent中thinking内容的文本提及终止条件"""
    
    async def __call__(self, messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> StopMessage | None:
        if self._terminated:
            from autogen_agentchat.base import TerminatedException
            raise TerminatedException("Termination condition has already been reached")
        
        for message in messages:
            if self._sources is not None and message.source not in self._sources:
                continue

            content = message.to_text()
            
            # 对于ThoughtEvent，过滤掉thinking标签内的内容
            if isinstance(message, ThoughtEvent):
                import re
                filtered_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
                if filtered_content.strip():
                    content = filtered_content
                    logger.debug(f"[终止条件] 过滤thinking内容后检查: {content[:50]}...")
                else:
                    logger.debug(f"[终止条件] 跳过纯thinking内容")
                    continue
            
            # 检查是否包含终止文本
            if self._termination_text in content:
                self._terminated = True
                return StopMessage(
                    content=f"Text '{self._termination_text}' mentioned", source="TextMentionTermination"
                )
        return None


async def generate_script_from_code_blocks(content: str, purpose: str = "运维脚本") -> str:
    """
    从代码块生成可执行的脚本文件
    
    Args:
        content: 包含代码块的内容
        purpose: 脚本用途描述
        
    Returns:
        生成结果报告
    """
    from script_generator import generate_script_from_code_blocks as generate_script
    
    try:
        result = generate_script(content, purpose)
        
        if result["success"]:
            report = f"脚本生成成功！\n"
            report += f"生成脚本数量: {result['total_scripts']}\n\n"
            
            for script_info in result["results"]:
                if "error" not in script_info:
                    report += f"{script_info['language'].upper()} 脚本:\n"
                    report += f"   文件名: {script_info['filename']}\n"
                    report += f"   路径: {script_info['filepath']}\n"
                    report += f"   代码预览: {script_info['code_preview']}\n\n"
                else:
                    report += f"{script_info['language'].upper()} 脚本生成失败: {script_info['error']}\n\n"
            
            report += "重要提醒:\n"
            report += "1. 请在执行前仔细检查脚本内容\n"
            report += "2. 建议在测试环境中先验证脚本\n"
            report += "3. 执行前请确保有足够的权限\n"
            
            return report
        else:
            return f"脚本生成失败: {result.get('error', '未知错误')}"
            
    except Exception as e:
        return f"脚本生成过程中发生错误: {str(e)}"

async def list_generated_scripts() -> str:
    """
    列出已生成的脚本文件
    
    Returns:
        脚本文件列表报告
    """
    from script_generator import list_generated_scripts as list_scripts
    
    try:
        result = list_scripts()
        
        if result["success"]:
            if result["total"] == 0:
                return "暂无生成的脚本文件"
            
            report = f"已生成脚本文件列表 (共 {result['total']} 个):\n\n"
            
            for script in result["scripts"]:
                status = "可执行" if script["executable"] else "不可执行"
                report += f" {script['filename']}\n"
                report += f"   大小: {script['size']} 字节\n"
                report += f"   创建时间: {script['created']}\n"
                report += f"   状态: {status}\n\n"
            
            return report
        else:
            return f"获取脚本列表失败: {result.get('error', '未知错误')}"
            
    except Exception as e:
        return f"获取脚本列表时发生错误: {str(e)}"

async def get_script_content(filepath: str) -> str:
    """
    获取脚本文件内容
    
    Args:
        filepath: 脚本文件路径
        
    Returns:
        脚本文件内容
    """
    from script_generator import get_script_content as get_content
    
    try:
        content = get_content(filepath)
        return f"脚本文件内容 ({filepath}):\n\n```\n{content}\n```"
    except Exception as e:
        return f"读取脚本文件失败: {str(e)}"

# =============================================================================
# 简化的消息序列化 - 参考core_streaming_handoffs_fastapi
# =============================================================================

def simple_message_dump(message):
    """简化的消息序列化，避免复杂对象问题，确保Unicode正确显示"""
    try:
        # 提取基本信息
        content = getattr(message, 'content', str(message))
        source = getattr(message, 'source', 'unknown')
        message_type = getattr(message, 'type', 'message')
        
        # 处理内容 - 确保datetime等对象被正确转换
        if isinstance(content, (list, dict)):
            content = json.dumps(content, default=str, ensure_ascii=False)
        elif hasattr(content, '__dict__'):
            content = str(content)
        elif isinstance(content, datetime):
            content = content.isoformat()
        else:
            content = str(content)
        
        return {
            "type": message_type,
            "content": content,
            "source": source
        }
    except Exception as e:
        return {
            "type": "error",
            "content": f"序列化错误: {str(e)}",
            "source": "system"
        }

# =============================================================================
# 创建运维团队
# =============================================================================

async def get_ops_team(
    user_input_func: Callable[[str, Optional[CancellationToken]], Awaitable[str]],
) -> Swarm:
    """创建智能运维团队"""

    try:
        async with aiofiles.open(model_config_path, "r") as file:
            model_config = yaml.safe_load(await file.read())
        model_client = ChatCompletionClient.load_component(model_config)
    except Exception as e:
        logger.error(f"模型配置加载失败: {e}")
        # 默认配置
        from autogen_ext.models.ollama import OllamaChatCompletionClient
        from autogen_core.models import ModelFamily
        model_client = OllamaChatCompletionClient(
            model="qwen3:8b",
            host="http://localhost:11434",
            model_info={
                "vision": False,
                "function_calling": True,
                "json_output": False,
                "family": ModelFamily.R1,
                "structured_output": False,
            },
            options={
                "num_ctx": 20000,
                "temperature": 0.3,
                "top_p": 0.8,
                "repeat_penalty": 1.1,
            }
        )
    
    # 1. 用户代理
    user_proxy = UserProxyAgent(
        name="user_requester",
        description="运维请求提交者，代表用户进行问题描述和操作确认",
        input_func=user_input_func,
    )
    
    # 2. 运维协调员
    ops_coordinator = AssistantAgent(
        name="ops_coordinator",
        model_client=model_client,
        description="经验丰富的系统运维协调员，负责协调整个运维流程和用户交互",
        handoffs=["system_monitor", "ops_engineer", "code_executor", "user_requester"],
        tools=[
            list_hosts_and_groups, add_host_to_group, remove_host_from_group, 
            update_host_info, add_host_group, remove_host_group, 
            check_host_connectivity, get_hosts_by_group, search_hosts_by_criteria
        ],
        system_message="""你是一位银河麒麟v10服务器操作系统的系统运维协调员，负责协调整个运维处理流程。你有三名专员可供调遣，分别是system_monitor, ops_engineer, code_executor。

你的核心职责：
- 作为运维团队的核心协调者，接收并分析用户的运维问题
- 制定系统诊断和解决方案
- 指挥其他专员的工作
- 管理主机和主机组信息，使用相关工具来为其他专员提供需要执行任务的主机地址等信息

标准运维任务流程：
用户需求-->系统状态检查-->判别故障种类和等级，制定处置对策-->生成运维脚本-->脚本审查-->用户授权-->执行脚本-->系统状态复查-->总结汇报，决定是否结束任务

重要的工作模式：
- 你的任务是分析、协调和交流。除非用户明确需求，否则按照标准运维任务流程执行任务
- 你可以使用主机管理工具来管理主机和主机组信息
- 每当你接手任务时，需要向用户简要汇报当前任务状态和所处的流程位置，并简要说明接下来的计划
- 在系统检查结束之后,为用户给出清晰的故障种类和等级(P0~P4),以及处置对策
- 当需要收集系统信息时，先在消息中对system_monitor下达指令,然后handoff
- 当需要生成运维脚本时，先在消息中对ops_engineer下达指令,然后进行handoff；ops_engineer会将脚本交由code_executor进行审查
- 当需要用户发言或无事可做时，对user_requester进行handoff；
- 当需要处理脚本（审查或执行）时，先在消息中对code_executor下达指令,然后进行handoff
- 如果任务已经结束 → 说 "TERMINATE"

主机管理工具：
- list_hosts_and_groups(): 列出所有主机和主机组信息
- add_host_to_group(group_id, host_info): 向指定主机组添加主机
- remove_host_from_group(host_id): 从主机组中移除指定主机
- update_host_info(host_id, updated_info): 更新指定主机的信息
- add_host_group(group_info): 添加新的主机组
- remove_host_group(group_id): 移除指定的主机组
- check_host_connectivity(host_id): 检查指定主机的连接状态
- get_hosts_by_group(group_id): 获取指定主机组的所有主机信息
- search_hosts_by_criteria(criteria, value): 根据条件搜索主机

给ops_engineer的指令示例：
- "生成清理系统缓存的脚本"
- "创建优化MySQL连接池的脚本"
- "生成重启web服务的脚本"
- "创建检查系统资源的脚本"

Handoff规则：
- 在进行handoff之前确保自己当前步骤的工作已经完成;
- handoff是一个工具，调用时的格式为：transfer_to_[agent_name]()，括号内不要添加任何参数
- 同一次消息中只能进行一次handoff""",
        model_client_stream=True
    )
    
    # 3. 系统监控员
    system_monitor = AssistantAgent(
        name="system_monitor",
        model_client=model_client,
        description="专业的监控数据分析员，负责检索和分析系统监控数据",
        handoffs=["ops_coordinator"],
        tools=[search_monitoring_data, get_process_monitoring_report],
        system_message="""你是专业的监控数据分析员，专门负责检索和分析系统监控数据。

可用工具：
1. search_monitoring_data(query, time_range, host_name): 智能搜索监控数据
   Args:
        query: 查询关键词，支持以下类型：
            - CPU相关: "CPU", "CPU使用率", "CPU负载"
            - 内存相关: "内存", "RAM", "内存使用率"
            - 磁盘相关: "磁盘", "磁盘空间", "磁盘IO", "磁盘IOPS"
            - 网络相关: "网络", "网络流量", "网络错误", "TCP连接", "UDP连接"
            - 服务相关: "服务", "进程", "系统负载"
            - 安全相关: "漏洞", "安全", "CVE"
            - 系统状态: "系统状态", "系统概览"
        time_range: 时间范围，支持 "1h", "6h", "24h", "7d"
        host_name: 主机名称，默认为localhost，可以指定为其他主机名称

2. get_process_monitoring_report(process_name, status_filter, limit, sort_by): 获取进程监控报告
   Args:
        process_name: 指定进程名进行筛选，None表示获取所有进程
        status_filter: 按状态筛选，可选值：running, faulty, stopped
        limit: 返回进程数量限制，默认10个
        sort_by: 排序字段，可选：resource_usage(资源占用), memory(内存), cpu(CPU使用)

工作流程：
1. 理解用户的监控需求
2. 根据需求选择合适的工具：
   - 需要系统级监控数据（CPU、内存、磁盘等）→ 使用search_monitoring_data
   - 需要进程级监控信息 → 使用get_process_monitoring_report
3. 可以多次调用工具，直到获取到满意的数据为止
4. 无需发言，直接进行handoff返回协调员

查询示例：
- "检查CPU使用情况" → search_monitoring_data("CPU使用率", "1h")
- "分析最近6小时的磁盘空间" → search_monitoring_data("磁盘空间", "6h")
- "查看所有运行中的进程" → get_process_monitoring_report(status_filter="running")
- "查看内存占用最高的5个进程" → get_process_monitoring_report(limit=5, sort_by="memory")
- "检查nginx进程状态" → get_process_monitoring_report(process_name="nginx")

Handoff规则：
- 在进行handoff之前确保自己当前步骤的工作已经完成;
- handoff工具的格式为：transfer_to_ops_coordinator()，括号内不要添加任何参数
- 同一次消息中只能进行一次handoff""",
    model_client_stream=True
)

    # 4. 运维工程师
    ops_engineer = AssistantAgent(
        name="ops_engineer",
        model_client=model_client,
        description="智能运维工程师，负责根据自然语言指令生成可执行的脚本代码",
        handoffs=["ops_coordinator", "code_executor", "user_requester"],
        tools=[generate_script_from_code_blocks, list_generated_scripts, get_script_content],
        system_message="""你是银河麒麟v10服务器操作系统的智能运维工程师，专门负责根据自然语言指令生成可执行的脚本代码。

核心能力：
- 理解运维协调员的自然语言指令
- 生成bash或python代码块
- 将代码块转换为可执行的脚本文件
- 管理生成的脚本文件

工作模式：
- 你能调用脚本生成工具：generate_script_from_code_blocks, list_generated_scripts, get_script_content
- 你可以使用handoff把任务交给ops_coordinator
- 你可以使用handoff转交code_executor进行脚本审查（并在消息中提供脚本文件名、目标host_name及必要说明）

工作流程：
1. 【接收指令】：接收协调员的自然语言运维指令
2. 【分析需求】：分析指令中的具体运维需求
3. 【生成代码】：根据需求生成相应的bash或python代码块
4. 【创建脚本】：使用generate_script_from_code_blocks工具将代码块转换为可执行脚本
5. 【转交审查】：脚本生成后，使用transfer_to_code_executor发起脚本审查；请在消息中提供：脚本文件名（不含路径）、目标host_name、脚本用途与可能风险说明
6. 【等待结果】：若code_executor审查不通过，会附带具体审查意见并转交回你；请据此修订并重复步骤3–5。若审查通过，code_executor会向用户请求授权并在获得授权后执行；若用户拒绝，code_executor会将任务转交给协调员由其决定是否继续

可用工具：
- generate_script_from_code_blocks(content, purpose): 从代码块生成脚本文件，返回生成的脚本文件名称和信息
  Args:
    content: 包含代码块的内容（支持```bash和```python格式）
    purpose: 脚本用途描述
- list_generated_scripts(): 列出已生成的脚本文件
- get_script_content(filepath): 获取脚本文件内容

代码生成规则：
1. 根据指令类型选择合适的语言（bash用于系统命令，python用于复杂逻辑）
2. 生成的代码必须安全、高效、符合最佳实践
3. 包含适当的错误处理和日志记录
4. 添加必要的注释说明

示例指令和代码：
- "清理系统缓存" → bash脚本，包含清理命令
- "优化MySQL配置" → python脚本，包含配置修改逻辑
- "重启web服务" → bash脚本，包含服务重启命令
- "检查系统资源" → bash脚本，包含资源检查命令

重要规则：
- 生成的脚本必须安全可靠
- 包含适当的权限检查
- 添加错误处理和回滚机制
- 脚本生成后必须先由code_executor进行审查；审查通过后再由code_executor向用户请求授权
- 脚本的执行由code_executor负责
- 不要直接执行脚本，只负责生成和转交执行

Handoff规则：
- 在进行handoff之前确保自己当前步骤的工作已经完成;
- 同一次消息中只能进行一次handoff""",
        model_client_stream=True
    )
    
    # 5. 脚本执行员
    code_executor = AssistantAgent(
        name="code_executor",
        model_client=model_client,
        description="脚本审查与执行专员，负责审查脚本并执行已授权的运维脚本",
        handoffs=["ops_coordinator", "ops_engineer", "user_requester"],
        tools=[execute_script_remotely, execute_script_locally],
        system_message="""你是银河麒麟v10服务器操作系统的脚本审查与执行专员，专门负责先审查再执行运维脚本。

核心职责：
- 接收来自ops_engineer的脚本审查/执行任务
- 审查脚本安全性、正确性与可回滚性，并输出明确的审查结论与改进建议
- 审查通过时，请求用户授权；获得授权后安全地执行脚本
- 返回详细的执行结果或审查意见报告

工作模式：
- 你可以基于自身能力进行脚本审查，并在消息中输出审查结论与改进建议（无需调用任何工具）
- 审查通过后，使用无参数的transfer_to_user_requester请求用户确认与授权
- 获得用户授权后，选择远程或本地执行；执行完成后，使用无参数的transfer_to_ops_coordinator返回协调员
- 审查未通过时，附带具体审查意见与修改建议，使用无参数的transfer_to_ops_engineer返回让其重生成

工作流程：
1. 【接收任务】：接收来自ops_engineer的脚本与上下文（脚本文件名、目标host_name、用途与风险说明）
2. 【审查脚本】：基于安全性、正确性、幂等性、可观察性与回滚策略进行审查并给出结论
   - 通过 → 进入【请求授权】
   - 不通过 → 附带清单化的改进建议，transfer_to_ops_engineer
3. 【请求授权】：使用transfer_to_user_requester向用户发起授权请求，明确说明操作影响与回滚方案
4. 【执行脚本】：若授权通过，选择远程或本地执行并调用相应执行工具；若用户拒绝，则transfer_to_ops_coordinator
5. 【回报结果】：执行完成后，transfer_to_ops_coordinator并附带执行详情与后续复查建议

可用工具：
- execute_script_remotely(script_name, user_name, host_name): 远程执行脚本
  Args:
    script_name: 脚本文件名（如 "clean_cache.sh"），无需包含路径
    user_name: 远程用户名（如 "admin",默认为kylin_om）
    host_name: 远程主机名（如 "server01.example.com"）
- execute_script_locally(script_name): 本地执行脚本
  Args:
    script_name: 脚本文件名，无需包含路径

执行规则：
1. 确保脚本文件存在且可执行
2. 优先使用远程执行，除非明确指定本地执行


重要提醒：
- 审查阶段不调用任何工具，仅输出审查意见
- 只执行已授权的脚本；未经授权不得执行
- 确保执行环境安全
- 记录所有执行活动
- 及时报告执行结果或审查意见

Handoff规则：
- 在进行handoff之前确保自己当前步骤的工作已经完成;
- handoff工具的格式为：transfer_to_[agent_name]()，括号内不要添加任何参数
- 同一次消息中只能进行一次handoff""",
        model_client_stream=True
    )
    
    termination_conditions = (
        ThinkingFilteredTextMentionTermination("TERMINATE") |
        MaxMessageTermination(max_messages=25)
    )
    
    # 创建Swarm
    ops_team = Swarm(
        participants=[
            ops_coordinator,
            user_proxy,
            system_monitor,
            ops_engineer,
            code_executor
        ],
        termination_condition=termination_conditions
    )
    
    # Load state from file if exists
    if not os.path.exists(state_path):
        return ops_team
    try:
        async with aiofiles.open(state_path, "r") as file:
            state = json.loads(await file.read())
        await ops_team.load_state(state)
    except Exception as e:
        logger.error(f"加载状态失败: {e}")
    
    return ops_team 
