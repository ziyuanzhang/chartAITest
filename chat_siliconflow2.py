from openai import OpenAI  # 注意：仍然使用openai库，因为硅基流动兼容OpenAI API
# 硅基流动的API配置
import os
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")  # 从环境变量读取硅基流动的密钥
SILICONFLOW_BASE_URL = "https://api.siliconflow.cn/v1"  # 硅基流动的API端点

# 初始化OpenAI客户端，但指向硅基流动的端点
client = OpenAI(
    api_key=SILICONFLOW_API_KEY,
    base_url=SILICONFLOW_BASE_URL
)


# 调用硅基流动API - 模型名称需要修改为硅基流动支持的模型
async def chat_siliconflow2_fn(content):
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",  # 硅基流动上的模型名称，例如：DeepSeek-LLM-67B, Qwen-7B-Chat等
        messages=[{"role": "user", "content": content}],
        stream=True,
        max_tokens=500,
        temperature=0.7,
    )
    print("chat_siliconflow2_fn:",response)
    return response