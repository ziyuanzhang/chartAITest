from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chat_second import chat_fn
import uvicorn

class Item(BaseModel):
    api_key: str
    content:str
    model:str|None = "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B"

app = FastAPI()
# 可选：允许跨域（前端访问用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或指定你的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/api/chart")
async def chart(data: Item):
    print(data.content)
    return chart_fn(**data.dict())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")