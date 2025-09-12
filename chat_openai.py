import os
from openai import OpenAI
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
# 调用OpenAI API
def chat_openai_fn(content:str):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content":content}],
        stream=True,
        max_tokens=500,
    )
    print(response)
    return response
