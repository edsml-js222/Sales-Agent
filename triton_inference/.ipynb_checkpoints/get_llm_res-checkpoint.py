import requests

def get_llm_res(message, model_name, temperature=0.1, api_key='4d38043f29355bc7e9bf7bab7dccba8f'):
    model_platform = {
        "gpt-4o": "chatgpt",
        "gpt-4o-mini": "chatgpt",
        "ernie_speed": "百度文心",
        "ernie-4.0-turbo-8k": "百度文心",
        "ernie-3.5-8k-preview": "百度文心",
        "qwen1.5-1.8b-chat": "阿里千问",
        "qwen-turbo": "阿里千问",
        "hunyuan-lite": "腾讯混元",
        "ep-20240711084128-2tpgm": "字节豆包",
        "ep-20240711083920-lsxn9": "字节豆包",
        "generalv3.5": "科大讯飞星火",
        "glm-4": "智谱AI",
        "moonshot-v1-8k": "月之暗面kimi",
        "EnChat_v1": "Enchat",
        "deepseek-chat": "deepseek",
        "deepseek-coder": "deepseek"
    }
    url = "http://121.201.110.83:30304/chat"
    data = {
        "api_key": str(api_key), #需要自己注册一个,参考api_key注册
        "messages": message,
        "model_name": model_name,
        "platform": model_platform[model_name],
        "is_model_free": True, #谨慎使用，需要到官方文档确定是免费
        "temperature": temperature
        
    }
    data = requests.post(url=url, json=data)
    return data.json()['content'], data.json()['usage']['prompt_tokens'], data.json()['usage']['completion_tokens']