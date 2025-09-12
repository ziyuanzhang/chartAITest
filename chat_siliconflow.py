import requests

import os
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")


async def chat_siliconflow_fn(content,model="deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",api_key=SILICONFLOW_API_KEY):
      headers = {"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"}

      data = {
        "model": model,
        "messages": [
          {
            "role": "user",
            "content": content
          }
        ]}
      x =requests.post("https://api.siliconflow.cn/v1/chat/completions",headers=headers,json=data)
      res = x.json()


      print(res)
      # print(res['choices'])
      return res