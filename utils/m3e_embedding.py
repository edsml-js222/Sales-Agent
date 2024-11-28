import requests
import numpy as np

def m3e_embedding(text: str):
    data = {
    "api_key": "4d38043f29355bc7e9bf7bab7dccba8f",
    "text": [text],
    "is_norm": False
    }
    url = "http://121.201.110.83:30304/v1/embedding"
    response = requests.post(url, json=data)
    emb_res = np.array(response.json()['emb'][0], dtype=np.float32).tolist()
    return emb_res