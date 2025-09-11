import asyncio
from http.client import responses

import uvicorn
from fastapi import FastAPI,Request,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Dict
import uuid
import json
import time

from websockets import connect

app = FastAPI()


sessions:Dict[str,dict]={}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/api/chat/start")
async def start_chat_session(request: Request):
    """
    启动一个新的聊天会话
    返回唯一的stream_id用于后续的流式连接
    """
    try:
        data = await request.json()
        use_message =data.get('message','').strip()
        if not use_message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        stream_id = str(uuid.uuid4())

        sessions[stream_id] = {
            "message": use_message,
            "created_at":time.time(),
            "status":"pending" # pending, streaming, completed, error
        }
        await cleanup_old_sessions()

        return {
            "stream_id":stream_id,
            "status":"session_created"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start request: {str(e)}")

@app.post("/api/chat/stream/{stream_id}")
async def start_chat_stream(stream_id: str):
    """
    通过GET请求连接到此会话的流式响应
    使用EventSource监听此端点
    """
    # 检查会话是否存在
    if stream_id not in sessions:
        raise HTTPException(status_code=404, detail="Stream not found")

    session = sessions[stream_id]
    # 检查会话是否已完成或出错
    if session["status"] in ["completed", "error"]:

        async def completed_response():
            yield f"data:{json.dumps({'error':'Session already completed'})}\n\n"

        return StreamingResponse(completed_response(),media_type="text/event-stream")
    # 标记会话为流式传输中
    session["status"]="streaming"
    try:
        # 调用OpenAI API
        response = {}
        async def generate():
            full_response=""
            try:
                for chunk in response:
                    if chunk.choice[0].finish_reason =="stop":
                        break
                    content =chunk.choice[0].delta.content
                    if connect is not None:
                        full_response += content
                        # 发送SSE格式的数据
                        yield f"data:{json.dumps({'content':content})}\n\n"
                        await asyncio.sleep(0.01) # 控制输出速度
                # 标记会话完成
                session["status"]="completed"
                session["message"] = full_response
                # 发送完成信号
                yield f"data:{json.dumps({'done':True})}\n\n"
            except Exception as e:
                session["status"]="error"
                session["error"]=str(e)
                yield f"data:{json.dumps({'error':str(e)})}\n\n"
        return  StreamingResponse(generate(),media_type="text/event-stream",headers={
            "Cache-Control":"no-cache",
            "Connection":"keep-alive",
        })
    except Exception as e:
        session["status"]="error"
        session["error"] = str(e)
        async def error_response():
            yield f"data:{json.dumps({'error':f'OpenAI API error: {str(e)}'})}\n\n"
        return StreamingResponse(error_response(),media_type="text/event-stream")

async def cleanup_old_sessions():
    """清理10分钟前的旧会话"""
    current_time = time.time()
    # 获取键列表【key】
    expired_sessions = [stream_id for stream_id,session in sessions.items() if current_time - session['created_at'] > 600]
    for stream_id in expired_sessions:
        del sessions[stream_id]

# 获取会话状态
@app.get("/api/chat/status{stream_id}")
async def get_chat_status(stream_id: str):
    if stream_id not in sessions:
        raise HTTPException(status_code=404, detail="Stream not found")
    return sessions[stream_id]

# 删除会话
@app.delete("/api/chat/{stream_id}")
async def delete_chat_session(stream_id: str):
    if stream_id in sessions:
        del sessions[stream_id]
        return {"status":"deleted"}
    return {"status":"not_found"}

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status":"healthy","session_count":len(sessions)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)