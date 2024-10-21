import time
import random
from utils.chatgpt import openai_predict

def get_triton_http_res(prompts, use_model="qwen", temperature=0.01, **kwargs):
    model_db = kwargs.get("model_db")
    if "qwen" in use_model:
        use_model = "qwen"

    try:
        timeout = model_db.find_one({"model_type": "timeout"}, sort=[("_id", -1)])['timeout']
    except:
        timeout = 5
    
    model_config = model_db.find_one({"model_config": "model_config"}, sort=[("_id", -1)])
    config = model_config[use_model]
    conf = random.choices(config["conf"], weights=config["prob"], k=1)[0]

    OPENAI_API_BASE = conf["OPENAI_API_BASE"]
    OPENAI_API_KEY = conf["OPENAI_API_KEY"]
    model = conf["model"]
    
    if isinstance(prompts, str):
        prompts = [prompts]

    try:
        # print(f"输入长度：{len(prompts[0])}", flush=True)
        t1 = time.time()
        res = openai_predict(OPENAI_API_BASE=OPENAI_API_BASE, OPENAI_API_KEY=OPENAI_API_KEY,
                                          prompt=prompts[0], temperature=temperature, model=model, timeout=timeout)
        # print(f"输出长度：{len(res)}, 时间记录：{time.time() - t1}", flush=True)
        return {"result": [res],
                "api_type": use_model}
    except Exception as e:
        print(f"use_model:{use_model}, OPENAI_API_BASE:{OPENAI_API_BASE}, model:{model}, 报错；{e}", flush=True)
        OPENAI_API_BASE = "http://localhost:20202/v1/"
        OPENAI_API_KEY = "EMPTY"
        model = "Qwen-72B-Chat-Int4"

        text = openai_predict(OPENAI_API_BASE=OPENAI_API_BASE, OPENAI_API_KEY=OPENAI_API_KEY,
                                        prompt=prompts[0], temperature=temperature, model=model)
        return {"result": [text], "api_type": use_model}