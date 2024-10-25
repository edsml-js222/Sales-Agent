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

industry_id_saved = '默认'
template_id_saved = '默认'
chat_id_saved = ''
database_name = 'smart_salesman'

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

# # 连接到MongoDB
# database_name = 'smart_salesman'
# db = _init_mongo_connect(database_name=database_name)
# sales_template_db = db["sales_template_db"]

# # 获取industry_id和template_id的选项
# industry_ids = sales_template_db.distinct('industry_id')
# template_ids = sales_template_db.distinct('template_id')


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
    init_mess = init_mess_store[random.randint(0, len(init_mess_store)-1)]
    initial_message = [[None, init_mess]]
    return [gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), initial_message] # 隐藏对话框

# 绑定用户输入事件
def user_input_handler(user_input, history):
    global chat_id_saved
    global industry_id_saved
    global template_id_saved
    model_reply = get_model_reply(industry_id_saved, template_id_saved, user_input, chat_id_saved)
    history.append([user_input, model_reply])
    return [history, ""]

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
        print(f"model_reply: {model_reply}\ndata: {data}")
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

# def get_template_content(industry_id, template_id):
#     # 根据industry_id和template_id获取template_content
#     result = sales_template_db.find_one({'industry_id': industry_id, 'template_id': template_id})
#     return result['template_content'] if result else "没有已经存入的模版内容哦"

def connect_database():
    """连接数据库并且获取独特的industry_id"""
    try:
        db = _init_mongo_connect(database_name=database_name)
        sales_template_db = db['sales_template_db']
        industry_ids = list(sales_template_db.distinct('industry_id'))
        return [
            gr.update(visible=True, choices=industry_ids, allow_custom_value=True, value=''), # show industry_ids options
            gr.update(visible=False), # hide template_ids options
            gr.update(visible=False), # hide template_content display
            "数据库连接成功",
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False)
        ]
    except Exception as e:
        print(f"连接数据库失败: {str(e)}")
        return [
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            "数据库连接失败"
        ]
        
def update_template_choices(industry_id):
    """update template_ids options according to industry_id"""
    if not industry_id:
        return [
            gr.update(visible=False),
            gr.update(visible=False),
            "请先选择行业id"
        ]
    global industry_id_saved
    industry_id_saved = industry_id

    db = _init_mongo_connect(database_name=database_name)
    sales_template_db = db['sales_template_db']
    templates_ids = list(sales_template_db.find(
        {'industry_id': industry_id}
    ).distinct('template_id'))
    return [
        gr.update(visible=True, choices=templates_ids, allow_custom_value=True, value=''), # show template_ids options
        gr.update(visible=False), # hide template_content display
        f"已找到{len(templates_ids)}个模板"
    ]

def show_template_content(industry_id, template_id):
    """update template_content according to industry_id and template_id"""
    if not template_id:
        return [
            gr.update(visible=False),
            "请先选择模板id"
        ]
    global template_id_saved
    template_id_saved = template_id

    db = _init_mongo_connect(database_name=database_name)
    sales_template_db = db['sales_template_db']
    template_content = sales_template_db.find_one(
        {'industry_id': industry_id, 'template_id': template_id}
    )
    if template_content and 'template_content' in template_content:
        return [
            gr.update(visible=True, value=template_content['template_content']), # show template_content
            "话术模版加载成功"
        ]
    return [gr.update(visible=False), "没有找到对应的话术模版"]

def show_new_template_input():
    return [
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=True, allow_custom_value=True, value=''),
        gr.update(visible=True, allow_custom_value=True, value=''),
        gr.update(visible=True)
    ]

def save_template_to_db(industry_id, template_id, template_content):
    """保存模版到数据库"""
    try:
        db = _init_mongo_connect(database_name=database_name)
        sales_template_db = db['sales_template_db']
        
        # 检查是否已存在相同的记录
        existing = sales_template_db.find_one({
            'industry_id': industry_id,
            'template_id': template_id
        })
        
        if existing:
            sales_template_db.update_one(
                {'industry_id': industry_id, 'template_id': template_id},
                {'$set': {'template_content': template_content}}
            )
            return "模板内容已更新！"
        
        # 插入新记录
        sales_template_db.insert_one({
            'industry_id': industry_id,
            'template_id': template_id,
            'template_content': template_content
        })
        return "模版内容已成功存入数据库！"
    except Exception as e:
        return f"保存失败：{str(e)}"
# def update_or_create_template(industry_id, template_id, template_content):
#     # 检查是否存在对应的记录
#     existing_record = sales_template_db.find_one({'industry_id': industry_id, 'template_id': template_id})
#     if existing_record:
#         # 更新记录
#         sales_template_db.update_one(
#             {'industry_id': industry_id, 'template_id': template_id},
#             {'$set': {'template_content': template_content}}
#         )
#         return "模板内容已更新！"
#     else:
#         # 创建新记录
#         sales_template_db.insert_one({
#             'industry_id': industry_id,
#             'template_id': template_id,
#             'template_content': template_content
#         })
#         return "新模板已创建！"

def save_with_confirmation(industry_id, template_id, template_content):
    """带确认对话框的保存功能"""
    return [
        gr.update(visible=True),
        f"确定要保存话术模版到:\n行业id: {industry_id}\n模板id: {template_id}吗？"
    ]

def confirm_save(industry_id, template_id, template_content, confirmed):
    """确认保存后的处理"""
    if not confirmed:
        return [gr.update(visible=False), "已取消保存"]

    result = save_template_to_db(industry_id, template_id, template_content)
    return [gr.update(visible=False), result]

with gr.Blocks() as demo1:
    gr.Markdown("""
                ## 智能销售助手demo:\n
                🧑‍💼**AI销售助手**: 引导客户的交互，留下留资\n
                😊**行业销售话术配置**: 配置行业的销售话术
                """)
    # dropdown = gr.Dropdown(choices=model_options, label="选择你想要使用的大模型吧🤖", allow_custom_value=True, value='')
    # dropdown.change(model_select, dropdown)
    
    with gr.Tab("🧑‍💼AI销售助手"):
        init_mess = init_mess_store[random.randint(0, len(init_mess_store)-1)]
        initial_message = [[None, init_mess]]
        chatbot = gr.Chatbot(value=initial_message)

        # 开始对话按钮
        start_button = gr.Button("🚀开始对话")

        # 用户输入框
        msg = gr.Textbox(placeholder="👉想了解什么项目呀？在这儿告诉我吧", label='', visible=False)
        # 结束对话按钮
        end_button = gr.Button("🔚结束对话", visible=False)

        start_button.click(start_chat, None, [msg, end_button, start_button], queue=False)
        end_button.click(end_chat, None, [msg, end_button, start_button, chatbot], queue=False)
        msg.submit(user_input_handler, [msg, chatbot], [chatbot, msg], queue=False)

    with gr.Tab("📥话术配置"):
        # industry_dropdown = gr.Dropdown(choices=industry_ids, label="选择行业ID", allow_custom_value=True, value='')
        # template_dropdown = gr.Dropdown(choices=template_ids, label="选择模板ID", allow_custom_value=True, value='')

        # template_content_display = gr.Textbox(label="模板内容", interactive=False)
        
        # industry_input = gr.Textbox(label="行业ID输入")
        # template_input = gr.Textbox(label="模板ID输入")
        # content_input = gr.Textbox(label="模板内容输入")
        
        # confirm_button = gr.Button("确认")

        # # 绑定下拉菜单的变化事件
        # industry_dropdown.change(show_industry_id, industry_dropdown)
        # template_dropdown.change(show_template_id, template_dropdown).then(
        #     lambda: get_template_content(industry_id_saved, template_id_saved),
        #     None,
        #     template_content_display
        # )
        # # 绑定确认按钮的点击事件
        # confirm_button.click(update_or_create_template, [industry_input, template_input, content_input], None)
        with gr.Row():
            gr.Markdown("### 话术模版配置")
        
        with gr.Row():
            with gr.Column(scale=1):
                status_message = gr.Textbox(label="状态信息", interactive=False)

                with gr.Row():
                    connect_btn = gr.Button("🔗连接数据库", variant="primary")
                    new_template_btn = gr.Button("📝插入新话术模版")

                industry_dropdown = gr.Dropdown(choices=[], label="选择行业ID", allow_custom_value=True, value='', visible=False)
                template_dropdown = gr.Dropdown(choices=[], label="选择模板ID", allow_custom_value=True, value='', visible=False)

                with gr.Row(visible=False) as new_template_row:
                    new_industry_input = gr.Textbox(label="行业ID输入", scale=1)
                    new_template_input = gr.Textbox(label="模板ID输入", scale=1)
                    
                new_template_content = gr.TextArea(label="模板内容输入", lines=5, visible=False)
                save_btn = gr.Button("💾存入数据库", visible=False)

                with gr.Group(visible=False) as confirm_box:
                    gr.Markdown("### 确认保存")
                    confirm_text = gr.Markdown("")
                    with gr.Row():
                        confirm_yes = gr.Button("确认")
                        confirm_no = gr.Button("取消")

            with gr.Column(scale=2):
                template_content = gr.TextArea(label="模版内容预览", interactive=False, visible=False, lines=10)
        # 事件绑定
        connect_btn.click(fn=connect_database, inputs=None, outputs=[industry_dropdown, template_dropdown, template_content, status_message, new_template_row, new_template_content, save_btn], queue=False)
        
        industry_dropdown.change(fn=update_template_choices, inputs=industry_dropdown, outputs=[template_dropdown, template_content, status_message], queue=False)

        template_dropdown.change(fn=show_template_content, inputs=[industry_dropdown, template_dropdown], outputs=[template_content, status_message], queue=False)

        new_template_btn.click(fn=show_new_template_input, inputs=None, outputs=[industry_dropdown, template_dropdown, template_content, new_template_row, new_template_content, save_btn], queue=False)

        save_btn.click(fn=save_with_confirmation, inputs=[new_industry_input, new_template_input, new_template_content], outputs=[confirm_box, confirm_text], queue=False)

        confirm_yes.click(fn=confirm_save, inputs=[new_industry_input, new_template_input, new_template_content, gr.Textbox(value=True, visible=False)], outputs=[confirm_box, confirm_text], queue=False)

        confirm_no.click(fn=confirm_save, inputs=[new_industry_input, new_template_input, new_template_content, gr.Textbox(value=False, visible=False)], outputs=[confirm_box, confirm_text], queue=False)

demo1.launch(server_name="0.0.0.0", server_port=7880)
