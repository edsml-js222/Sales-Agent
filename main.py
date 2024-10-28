import warnings
import requests
import os
import sys
warnings.filterwarnings("ignore")
import uvicorn
import setproctitle
import logging
import time
import json
import numpy as np
from tqdm import tqdm
#from pymilvus import FieldSchema, DataType, CollectionSchema

# 获取当前进程ID
pid = str(os.getpid())
project_name = "smart_salesman"
# 设置进程名字
setproctitle.setproctitle(project_name)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# 获取项目文件夹目录 & 根目录
current_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_path)
#root_path = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(f"{current_dir}/utils")


from utils.logger_config import setup_logger
from utils.connect_mongo import _init_mongo_connect
from algorithm.sales_reply.get_sales_reply import get_sales_reply
from algorithm.slots_recognition.get_slots_recognition import extract_slot_info
# import utils.MilvusDB as mdb


app = FastAPI()

# 日志数据记录
# 创建mongodb数据库连接
db = _init_mongo_connect(database_name=project_name, port=27017)
sales_template_db = db["sales_template_db"]
user_dialogue_db = db["user_dialogue_db"]
slots_db = db["slots_db"]

# 存储日志数据
# log_db = db["log_db"]
# model_db = db["model_db"]


# Create a logger for the application
app_logger = setup_logger('app_logger', f"{current_dir}/logs/app.log")
slots_logger = setup_logger('slots_logger', f"{current_dir}/logs/slots.log")

# 获取历史对话数据
def get_dialogue_data(data):
    try:
        history_dialogue = []
        if user_dialogue_db.count_documents({"chat_id": data.get("chat_id")}):
            for dialogue_order, dialogue in enumerate(user_dialogue_db.find({"chat_id": data.get("chat_id")}, sort=[('insert_time', 1)])):
                history_dialogue.append(
                    {f"The number {dialogue_order} dialogue content": [{"role": "user", "content":dialogue.get("user_input")}, {"role": "assistant", "content": dialogue.get("model_reply")}]}
                )
        return history_dialogue
    except Exception as e:
        app_logger.error(f"Error in get_dialogue_data: {str(e)}")
        return []

# 接口示例
@app.get("/test")
async def test():
    return {"status": 200, "msg": "hello world"}

# 话术存储模块
@app.post("/sales_template_save")
async def sales_template_save(request:Request):
    try:
        data = await request.json()
        industry_id = data.get("industry_id")
        template_id = data.get("template_id")
        template_content = data.get("template_content")

        if not industry_id or not template_id or not template_content:
            return {"status": 400, "msg": "Missing required information"}
        # 检查是否存在对应的记录
        existing_record = sales_template_db.find_one({'industry_id': industry_id, 'template_id': template_id})
        if existing_record:
            # 更新记录
            sales_template_db.update_one(
                {'industry_id': industry_id, 'template_id': template_id},
                {'$set': {'template_content': template_content}}
            )
        else:
            # 创建新记录
            sales_template_db.insert_one({
            "industry_id": industry_id, 
            "template_id": template_id, 
                "template_content": template_content
            })
        return {"status": 200, "msg": "success"}
    
    except Exception as e:
        app_logger.error(f"Error in sales_template_save: {str(e)}")
        return {"status": 500, "msg": "Internal server error"}
    

# 槽位信息提取模块
@app.post("/slots_recognition")
async def slots_recognition(request:Request):
    try:
        data = await request.json()
        user_input = data.get("user_input")
        current_slots = data.get("current_slots")
        chat_id = data.get("chat_id")
        slots_recognition, _, _ = extract_slot_info(user_input, current_slots)

        # 用专门的槽位日志记录器
        slots_logger.info(
            json.dumps({
                "chat_id": chat_id,
                "user_input": user_input,
                "current_slots": current_slots,
                "after_slots_recognition": slots_recognition
            }, ensure_ascii=False)
        )

        # 将槽位信息存入数据库
        slots_db.insert_one({
            "chat_id": chat_id,
            "slots_recognition": slots_recognition,
            "insert_time":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        })
        return {"status": 200, "msg": "Slots recognition success", "slots_recognition": slots_recognition}
    except Exception as e:
        app_logger.error(f"Error in slots_recognition: {str(e)}")
        return {"status": 500, "msg": "Internal server error"}
    


# 模型回复模块
@app.post("/model_reply")
async def model_reply(request:Request):
    try:
        data = await request.json()
        industry_id = data.get("industry_id")
        template_id = data.get("template_id")
        user_input = data.get("user_input")
        history = get_dialogue_data(data)
        
        template_info = sales_template_db.find_one(
            {"industry_id": industry_id, "template_id": template_id}, sort=[('_id', -1)]
        )

        # if not template_info:
        #     return {"status": 404, "msg": "Template not found"}

        template_content = template_info.get("template_content", "")        

        if not template_content:
            app_logger.warning(f"Template content not found for chat_id: {data.get('chat_id')}, use default template content")
            template_content = "以一名有亲和力的，有耐心的销售人员身份来回答客户的问题。"
        print(f"template_content: {template_content}")
        # 实现模型回复的逻辑
        model_reply, input_tokens, output_tokens = get_sales_reply(industry_id, template_content, user_input, history, model_name="gpt-4o-mini", temperature=0.1)

        # 将当前对话存入数据库
        user_dialogue_db.insert_one({
            "chat_id": data.get("chat_id"),
            "user_input": user_input,
            "model_reply": model_reply,
            "insert_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        })
        return {"status": 200, "msg": "Model reply success", "model_reply": model_reply, "input_tokens": input_tokens, "output_tokens": output_tokens}

    except Exception as e:
        app_logger.error(f"Error in model_reply: {str(e)}")
        return {"status": 500, "msg": "Internal server error"}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=30504, reload=False)