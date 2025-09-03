import requests


def chart_fn(api_key,content,model):
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
  return res
  # print(res)
  # print(res['choices'])