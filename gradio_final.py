import gradio as gr
from utils.connect_mongo import _init_mongo_connect
import requests
import random
import json
import time
import os
import setproctitle

# 获取当前进程pid
pid = str(os.getpid())
project_name = "smart_salesman_gradio"
setproctitle.setproctitle(project_name)

model_options = [
    "gpt-4o-mini",
    "gpt-4o",
]
model_using = ''

init_mess_store = [
    "您好，我是Health-OK公司的专属销售助手小H！我们专注于提供优质医疗设备，很高兴能为您提供帮助，让我们一起找到最合适的解决方案吧！😊", 
    "您好！我是Health-OK公司的销售代表小H。我们的医疗设备能够大大提升工作效率，期待与您分享更多信息！✨", 
    "嗨！我是Health-OK的小H，专注于医疗设备的销售。您有什么需求，我非常乐意为您提供专业的建议哦！🤗", 
    "您好！我是来自Health-OK的小H，专业为您介绍优质医疗设备。让我们一起探讨一下您的需求吧！🌟", 
    "您好，我是Health-OK的小H。我们提供的医疗设备注重品质与功能，期待能为您提供帮助！💼", 
    "您好！我是Health-OK的小H，您对我们的医疗设备感兴趣吗？我随时准备为您提供更多信息！📞", 
    "嘿，您好！我是Health-OK的销售助手小H，期待与您交流一下我们的医疗设备优势哦！🌈", 
    "您好，我是小H，来自Health-OK。我们的医疗设备旨在提升您的工作效率，随时为您解答疑问！👍", 
    "您好！我是Health-OK的小H。很高兴能为您提供我们的医疗设备资讯，让我们一起找出最佳选择吧！🌟", 
    "您好，我是Health-OK的小H，期待帮助您找到理想的医疗设备解决方案，随时乐意为您服务！😊"
]
init_mess = init_mess_store[random.randint(0, len(init_mess_store)-1)]

# 连接到MongoDB
database_name = 'smart_salesman'
db = _init_mongo_connect(database_name=database_name)
sales_template_db = db["sales_template_db"]

# 获取industry_id和template_id的选项
industry_ids = sales_template_db.distinct('industry_id')
template_ids = sales_template_db.distinct('template_id')

def get_template_content(industry_id, template_id):
    # 根据industry_id和template_id获取template_content
    result = db.collection.find_one({'industry_id': industry_id, 'template_id': template_id})
    return result['template_content'] if result else "未找到对应的模板内容"

def update_or_create_template(industry_id, template_id, template_content):
    # 检查是否存在对应的记录
    existing_record = db.collection.find_one({'industry_id': industry_id, 'template_id': template_id})
    if existing_record:
        # 更新记录
        db.collection.update_one(
            {'industry_id': industry_id, 'template_id': template_id},
            {'$set': {'template_content': template_content}}
        )
        return "模板内容已更新！"
    else:
        # 创建新记录
        db.collection.insert_one({
            'industry_id': industry_id,
            'template_id': template_id,
            'template_content': template_content
        })
        return "新模板已创建！"

with gr.Blocks() as demo1:
    def model_select(model_name):
        global model_using
        model_using = model_name
        
    gr.Markdown("""
                ## 智能销售助手demo:\n
                🧑‍💼**AI销售助手**: 引导客户的交互，留下留资\n
                😊**行业销售话术配置**: 配置行业的销售话术
                """)
    dropdown = gr.Dropdown(choices=model_options, label="选择你想要使用的大模型吧🤖")
    dropdown.change(model_select, dropdown)
    
    with gr.Tab("🧑‍💼AI销售助手"):
        initial_message = [[None, init_mess]]
        chatbot = gr.Chatbot(value=initial_message)
        msg = gr.Textbox(placeholder="👉我能帮您什么呀？在这儿告诉我吧", label='')
        with gr.Row():
            clear = gr.Button("🗑️清除历史对话")
            #save = gr.Button("📁存入数据库吧")
        
        def user(user_message, history):
            return "", history + [[user_message, None]]

        def bot(history):
            # 目标URL
            url = 'http://121.201.110.83:30204/chat'
            user_message = history[-1][0]
            # JSON数据
            chat_id = 0
            pre_data = {"chat_id": chat_id,
                        "model_using": model_using,
                        "question": user_message}
            json_data = json.dumps(pre_data)

            # 发送POST请求，并指定headers中的Content-Type为application/json
            response = requests.post(url, data=json_data)
            response_text = json.loads(response.json())['text']
            print(f"response: {response_text}")
            history[-1][1] = response_text
            time.sleep(0.05)
            yield history

        msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot, chatbot, chatbot)
        clear.click(lambda: None, None, chatbot, queue=False)
    with gr.Tab("📥话术配置"):
        industry_dropdown = gr.Dropdown(choices=industry_ids, label="选择行业ID")
        template_dropdown = gr.Dropdown(choices=template_ids, label="选择模板ID")
        
        template_content_display = gr.Textbox(label="模板内容", interactive=False)
        
        industry_input = gr.Textbox(label="行业ID输入")
        template_input = gr.Textbox(label="模板ID输入")
        content_input = gr.Textbox(label="模板内容输入")
        
        confirm_button = gr.Button("确认")

        # 绑定下拉菜单的变化事件
        industry_dropdown.change(get_template_content, [industry_dropdown, template_dropdown], template_content_display)
        template_dropdown.change(get_template_content, [industry_dropdown, template_dropdown], template_content_display)
        
        # 绑定确认按钮的点击事件
        confirm_button.click(update_or_create_template, [industry_input, template_input, content_input], None)

demo1.launch(server_name="0.0.0.0", server_port=7880)