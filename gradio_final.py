import gradio as gr
from utils.connect_mongo import _init_mongo_connect
import requests
import random
import string
import json
import time
import os
import setproctitle

# 获取当前进程pid
pid = str(os.getpid())
project_name = "smart_salesman_gradio"
setproctitle.setproctitle(project_name)

# model_options = [
#     "gpt-4o-mini",
#     "gpt-4o",
# ]
# model_using = ''

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

industry_id_saved = ''
template_id_saved = ''
chat_id_saved = ''

def generate_chat_id():
    # 生成一个6位随机字符串
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# 绑定按钮点击事件
def start_chat():
    global chat_id_saved
    chat_id_saved = generate_chat_id()
    print(f"当前对话chat_id: {chat_id_saved}")
    return [gr.update(visible=True, interactive=True), gr.update(visible=True), gr.update(visible=False)] # 显示对话框

# 绑定结束对话按钮事件
def end_chat():
    global chat_id_saved
    chat_id_saved = ''
    print(f"检查对话chat_id是否已经重置: {chat_id_saved}")
    return [gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)] # 隐藏对话框

# 绑定用户输入事件
def user_input_handler(user_input):
    global chat_id_saved
    global industry_id_saved
    global template_id_saved
    model_reply = get_model_reply(industry_id_saved, template_id_saved, user_input, chat_id_saved)
    return [[user_input, model_reply], ""]

# 获取模型回复
def get_model_reply(industry_id, template_id, user_input, chat_id):
    url = "http://localhost:30504/model_reply"
    payload = {
        "industry_id": industry_id,
        "template_id": template_id,
        "user_input": user_input,
        "chat_id": chat_id
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        model_reply = data.get("model_reply", "")
        if model_reply:
            model_reply_content = json.loads(model_reply)['reply']
            return model_reply_content
        return "当前有些繁忙哦，请稍等一会"
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
        return "当前有些繁忙哦，请稍等一会"

# def model_select(model_name):
#     global model_using
#     model_using = model_name

def show_industry_id(industry_id):
    global industry_id_saved
    industry_id_saved = industry_id

def show_template_id(template_id):
    global template_id_saved
    template_id_saved = template_id

def get_template_content(industry_id, template_id):
    # 根据industry_id和template_id获取template_content
    result = sales_template_db.find_one({'industry_id': industry_id, 'template_id': template_id})
    return result['template_content'] if result else "没有已经存入的模版内容哦"

def update_or_create_template(industry_id, template_id, template_content):
    # 检查是否存在对应的记录
    existing_record = sales_template_db.find_one({'industry_id': industry_id, 'template_id': template_id})
    if existing_record:
        # 更新记录
        sales_template_db.update_one(
            {'industry_id': industry_id, 'template_id': template_id},
            {'$set': {'template_content': template_content}}
        )
        return "模板内容已更新！"
    else:
        # 创建新记录
        sales_template_db.insert_one({
            'industry_id': industry_id,
            'template_id': template_id,
            'template_content': template_content
        })
        return "新模板已创建！"

with gr.Blocks() as demo1:
    gr.Markdown("""
                ## 智能销售助手demo:\n
                🧑‍💼**AI销售助手**: 引导客户的交互，留下留资\n
                😊**行业销售话术配置**: 配置行业的销售话术
                """)
    # dropdown = gr.Dropdown(choices=model_options, label="选择你想要使用的大模型吧🤖", allow_custom_value=True, value='')
    # dropdown.change(model_select, dropdown)
    
    with gr.Tab("🧑‍💼AI销售助手"):
        initial_message = [[None, init_mess]]
        chatbot = gr.Chatbot(value=initial_message)

        # 开始对话按钮
        start_button = gr.Button("🚀开始对话")

        # 用户输入框
        msg = gr.Textbox(placeholder="👉想了解什么项目呀？在这儿告诉我吧", label='', visible=False)
        # 结束对话按钮
        end_button = gr.Button("🔚结束对话", visible=False)

        start_button.click(start_chat, None, [msg, end_button, start_button], queue=False)
        end_button.click(end_chat, None, [msg, end_button, start_button], queue=False)
        msg.submit(user_input_handler, msg, [chatbot, msg], queue=False)

    with gr.Tab("📥话术配置"):
        industry_dropdown = gr.Dropdown(choices=industry_ids, label="选择行业ID", allow_custom_value=True, value='')
        template_dropdown = gr.Dropdown(choices=template_ids, label="选择模板ID", allow_custom_value=True, value='')

        template_content_display = gr.Textbox(label="模板内容", interactive=False)
        
        industry_input = gr.Textbox(label="行业ID输入")
        template_input = gr.Textbox(label="模板ID输入")
        content_input = gr.Textbox(label="模板内容输入")
        
        confirm_button = gr.Button("确认")

        # 绑定下拉菜单的变化事件
        industry_dropdown.change(show_industry_id, industry_dropdown)
        template_dropdown.change(show_template_id, template_dropdown).then(
            lambda: get_template_content(industry_id_saved, template_id_saved),
            None,
            template_content_display
        )
        # 绑定确认按钮的点击事件
        confirm_button.click(update_or_create_template, [industry_input, template_input, content_input], None)

demo1.launch(server_name="0.0.0.0", server_port=7880)
