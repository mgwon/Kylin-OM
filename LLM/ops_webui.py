import json
import logging
import os
from typing import Any, Awaitable, Callable, Optional
import asyncio
from datetime import datetime

import aiofiles
from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import TextMessage, UserInputRequestedEvent, ModelClientStreamingChunkEvent
from autogen_core import CancellationToken
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ops_team import get_ops_team, simple_message_dump

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

history_path = "ops_team_history.json"

app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def root():
    """Serve the chat interface HTML file."""
    return FileResponse("ops_webui.html")

@app.get("/favicon.ico")
async def favicon():
    """Handle favicon request to prevent 404 errors."""
    return {"status": "no favicon"}

async def get_history() -> list[dict[str, Any]]:
    """Get chat history from file."""
    if not os.path.exists(history_path):
        return []
    try:
        async with aiofiles.open(history_path, "r") as file:
            content = await file.read()
            if content.strip():
                return json.loads(content)
            else:
                return []
    except Exception as e:
        logger.error(f"加载历史记录失败: {e}")
        return []

@app.get("/history")
async def history() -> list[dict[str, Any]]:
    try:
        return await get_history()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.websocket("/ws/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()

    # 用户输入功能
    async def _user_input(prompt: str, cancellation_token: CancellationToken | None) -> str:
        try:
            data = await websocket.receive_json()
            message = TextMessage.model_validate(data)
            return message.content
        except WebSocketDisconnect:
            logger.info("Client disconnected while waiting for user input")
            raise

    try:
        while True:
            data = await websocket.receive_json()
            request = TextMessage.model_validate(data)

            try:
                team = await get_ops_team(_user_input)
                history = await get_history()
                stream = team.run_stream(task=request)
                
                # 流式消息处理 - 简化版本
                current_streaming_content = ""
                current_streaming_source = None
                
                async for message in stream:
                    if isinstance(message, TaskResult):
                        await websocket.send_json({
                            "type": "task_completed",
                            "content": "任务已完成",
                            "source": "system"
                        })
                        continue
                    
                    if isinstance(message, ModelClientStreamingChunkEvent):
                        if current_streaming_source is None:
                            current_streaming_source = message.source
                            current_streaming_content = message.content
                            await websocket.send_json({
                                "type": "streaming_start",
                                "source": message.source,
                                "content": current_streaming_content
                            })
                        else:
                            current_streaming_content += message.content
                            await websocket.send_json({
                                "type": "streaming_update",
                                "source": message.source,
                                "content": current_streaming_content
                            })
                    
                    elif current_streaming_source is not None:
                        await websocket.send_json({
                            "type": "streaming_end",
                            "source": current_streaming_source,
                            "content": current_streaming_content
                        })
                        
                        # 重置流式状态
                        current_streaming_source = None
                        current_streaming_content = ""
                        
                        # 检查当前消息是否为UserInputRequestedEvent
                        if isinstance(message, UserInputRequestedEvent):
                            message_data = simple_message_dump(message)
                            await websocket.send_json(message_data)
                        else:
                            # 跳过当前消息，因为它是流式响应的完整版本
                            # 不发送到前端，但保存到历史记录
                            message_data = simple_message_dump(message)
                            history.append(message_data)
                    
                    else:
                        message_data = simple_message_dump(message)
                        await websocket.send_json(message_data)
                        
                        if not isinstance(message, UserInputRequestedEvent):
                            history.append(message_data)
                
                # 确保流式响应完成
                if current_streaming_source is not None:
                    await websocket.send_json({
                        "type": "streaming_end",
                        "source": current_streaming_source,
                        "content": current_streaming_content
                    })

                # 保存当前状态
                try:
                    from ops_team import state_path
                    async with aiofiles.open(state_path, "w") as file:
                        state = await team.save_state()
                        # 使用default=str确保datetime等对象被正确序列化
                        await file.write(json.dumps(state, default=str, ensure_ascii=False))
                except Exception as e:
                    logger.error(f"保存状态失败: {e}")

                try:
                    async with aiofiles.open(history_path, "w") as file:
                        await file.write(json.dumps(history, default=str, ensure_ascii=False))
                except Exception as e:
                    logger.error(f"保存历史记录失败: {e}")
                    
            except WebSocketDisconnect:
                logger.info("Client disconnected during message processing")
                break
            except Exception as e:
                error_message = {
                    "type": "error",
                    "content": f"Error: {str(e)}",
                    "source": "system"
                }
                try:
                    await websocket.send_json(error_message)
                    # Re-enable input after error
                    await websocket.send_json({
                        "type": "UserInputRequestedEvent",
                        "content": "An error occurred. Please try again.",
                        "source": "system"
                    })
                except WebSocketDisconnect:
                    logger.info("Client disconnected while sending error message")
                    break
                except Exception as send_error:
                    logger.error(f"Failed to send error message: {str(send_error)}")
                    break

    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "content": f"Unexpected error: {str(e)}",
                "source": "system"
            })
        except WebSocketDisconnect:
            logger.info("Client disconnected before error could be sent")
        except Exception:
            logger.error("Failed to send error message to client")
            pass

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003) 
