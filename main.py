from fastapi import FastAPI, Body
from pydantic import BaseModel
from chart import chart_fn

class Item(BaseModel):
    api_key: str
    content:str
    model:str|None = "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B"

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/chart")
async def chart(data: Item):
    print(data.content)
    return chart_fn(**data.dict())