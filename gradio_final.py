import gradio as gr
from utils.connect_mongo import _init_mongo_connect
from algorithm.slots_recognition.get_slots_recognition import SlotInfo
from algorithm.sales_reply.insert_faq import insert_faq
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
brand_id_saved = '默认'
template_id_saved = '默认'
chat_id_saved = ''
slotinfo_saved = ''
chat_history_saved = []
database_name = 'smart_salesman'

# model_options = [
#     "gpt-4o-mini",
#     "gpt-4o",
# ]
# model_using = ''

init_mess_store = [
    "您好，我是Beauty-OK公司的专属销售助手小H！我们专注于提供优质医美服务，很高兴能为您提供帮助，让我们一起找到最合适的解决方案吧！😊",  
    "嗨！我是Beauty-OK的小H，专注于医美服务的销售。您有什么需求，我非常乐意为您提供专业的建议哦！🤗", 
    "您好！我是来自Beauty-OK的小H，专业为您介绍优质医美服务。让我们一起探讨一下您的需求吧！🌟", 
    "您好！我是Beauty-OK的小H，您对我们的医美服务感兴趣吗？我随时准备为您提供更多信息！📞", 
    "嘿，您好！我是Beauty-OK的销售助手小H，期待与您交流一下我们的医美服务哦！🌈", 
    "您好，我是Beauty-OK的小H，期待帮助您找到理想的医美服务，随时乐意为您服务！😊"
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

def save_intention_level():
    global chat_id_saved
    global industry_id_saved
    global brand_id_saved
    global template_id_saved
    global chat_history_saved
    
    url = "http://localhost:30504/intention_level"
    data = {
        "chat_id": chat_id_saved,
        "industry_id": industry_id_saved,
        "brand_id": brand_id_saved,
        "template_id": template_id_saved,
        "user_history": chat_history_saved
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        res_status = response.json()['status']
        return res_status
    except Exception as e:
        print(f"请求失败: {str(e)}")
        return 500

# 绑定按钮点击事件
def start_chat():
    global chat_id_saved
    global industry_id_saved
    global brand_id_saved
    global template_id_saved
    global slotinfo_saved
    slotinfo_saved = SlotInfo().to_dict()
    chat_id_saved = generate_chat_id()
    print(f"当前对话chat_id: {chat_id_saved}")
    url = "http://localhost:30504/new_dialogue"
    data = {
        "industry_id": industry_id_saved,
        "brand_id": brand_id_saved,
        "template_id": template_id_saved
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        res_status = response.json()['status']
        if res_status == 200:
            print("新建对话成功")
        else:
            print("新建对话失败")
    except Exception as e:
        print(f"请求失败{str(e)}")
    return [gr.update(visible=True, interactive=True), gr.update(visible=True), gr.update(visible=False)] # 显示对话框

# 绑定结束对话按钮事件
def end_chat():
    res_status = save_intention_level()
    if res_status == 200:
        print("留资等级判断成功")
    else:
        print("留资等级判断失败")
    global chat_id_saved
    global chat_history_saved
    chat_id_saved = ''
    chat_history_saved = []
    print(f"检查对话chat_id是否已经重置为空: {chat_id_saved}\n检查对话chat_history是否已经重置为空: {chat_history_saved}")
    init_mess = init_mess_store[random.randint(0, len(init_mess_store)-1)]
    initial_message = [[None, init_mess]]
    return [gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), initial_message] # 隐藏对话框

# 绑定用户输入事件
def user_input_handler(user_input, history):
    global chat_id_saved
    global industry_id_saved
    global brand_id_saved
    global template_id_saved
    global chat_history_saved
    global slotinfo_saved
    #model_reply = get_model_reply(industry_id_saved, template_id_saved, user_input, chat_id_saved)
    strict_reply = get_strict_reply(user_input, chat_id_saved, industry_id_saved, brand_id_saved, template_id_saved)
    slots_recognition_res = slots_recognition(user_input, slotinfo_saved, chat_id_saved, industry_id_saved, brand_id_saved, template_id_saved)
    # 更新槽位信息
    slotinfo_saved = slots_recognition_res
    history.append([user_input, strict_reply])
    chat_history_saved.append({"user": user_input})
    return [history, ""]

# 获取严格回复
def get_strict_reply(user_input, chat_id, industry_id, brand_id, template_id):
    url = "http://localhost:30504/strict_reply"
    data = {
        "user_input": user_input,
        "chat_id": chat_id,
        "industry_id": industry_id,
        "brand_id": brand_id,
        "template_id": template_id
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        data = response.json()
        strict_reply = data.get("strict_reply", "")
        print(data.get("msg", "No strict reply message"))
        return strict_reply
    except Exception as e:
        print(f"请求失败{str(e)}")
        return "当前有些繁忙哦，请稍等一会"
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

# 槽位信息识别
def slots_recognition(user_input, current_slots, chat_id, industry_id, brand_id, template_id):
    url = "http://localhost:30504/slots_recognition"
    payload = {
        "user_input": user_input,
        "current_slots": current_slots,
        "chat_id": chat_id,
        "industry_id": industry_id,
        "brand_id": brand_id,
        "template_id": template_id


    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        slots_recognition = data.get("slots_recognition", "")
        return slots_recognition
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
        global industry_id_saved
        global template_id_saved
        industry_id_saved = '默认'
        template_id_saved = '默认'
        db = _init_mongo_connect(database_name=database_name)
        sales_template_db = db['sales_template_db']
        industry_ids = list(sales_template_db.distinct('industry_id'))
        return [
            gr.update(visible=True, choices=industry_ids, allow_custom_value=True, value=''), # show industry_ids options
            gr.update(visible=False), # hide template_ids options
            gr.update(visible=False), # hide template_content display
            gr.update(visible=False), # hide faq_content
            "数据库连接成功",
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False)
        ]
    except Exception as e:
        print(f"连接数据库失败: {str(e)}")
        return [
            gr.update(visible=False), # hide industry_ids options
            gr.update(visible=False), # hide template_ids options
            gr.update(visible=False), # hide template_content display
            "数据库连接失败",
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False)
        ]
        
def update_brands_choices(industry_id):
    """update brands_ids options according to industry_id"""
    if not industry_id:
        return [
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            "请先选择行业id"
        ]
    global industry_id_saved
    industry_id_saved = industry_id

    db = _init_mongo_connect(database_name=database_name)
    sales_template_db = db['sales_template_db']
    brand_ids = list(sales_template_db.find(
        {'industry_id': industry_id}
    ).distinct('brand_id'))
    return [
        gr.update(visible=True, choices=brand_ids, allow_custom_value=True, value=''), # show brand_ids options
        gr.update(visible=False), # hide template_ids options
        gr.update(visible=False), # hide template_content display
        gr.update(visible=False),
        f"已找到{len(brand_ids)}个品牌"
    ]

def update_template_choices(industry_id, brand_id):
    """update template_ids options according to industry_id and brand_id"""
    if not brand_id:
        return [
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            "请先选择品牌id"
        ]

    global brand_id_saved
    brand_id_saved = brand_id

    db = _init_mongo_connect(database_name=database_name)
    sales_template_db = db['sales_template_db']
    template_ids = list(sales_template_db.find(
        {'industry_id': industry_id, 'brand_id': brand_id}
    ).distinct('template_id'))
    return [
        gr.update(visible=True, choices=template_ids, allow_custom_value=True, value=''), # show template_ids options
        gr.update(visible=False), # hide template_content display
        gr.update(visible=False), # hide the faq_content
        f"已找到{len(template_ids)}个模板"
    ]

def show_template_content(industry_id, brand_id, template_id):
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
    faq_content_db = db['faq_template_db']
    template_content = sales_template_db.find_one(
        {'industry_id': industry_id, 'brand_id': brand_id, 'template_id': template_id}
    )
    faq_content = faq_content_db.find_one(
      {"industry_id": industry_id, "brand_id": brand_id, "template_id": template_id}
    )
    if template_content and 'template_content' in template_content and faq_content and "faq_content" in faq_content:
        return [
            gr.update(visible=True, value=template_content['template_content']), # show template_content
            gr.update(visible=True, value=faq_content['faq_content']),
          "话术模版加载成功"
        ]
    return [gr.update(visible=False), "没有找到对应的话术模版"]

def show_new_template_input():
    return [
        gr.update(visible=False), # industry_dropdown
        gr.update(visible=False), # brand_dropdown
        gr.update(visible=False), # tempalte_dropdown
        gr.update(visible=False), # template_content
        gr.update(visible=False),
        gr.update(visible=True, value=''), # new_template_row
        gr.update(visible=True, value=''), # new_template_content
        gr.update(visible=False), # new_faq_row
        gr.update(visible=False), # new_faq_content
        gr.update(visible=True), # save_button
        gr.update(visible=False) # save_faq_button
    ]

def save_template_to_db(industry_id, brand_id, template_id, template_content):
    """保存模版到数据库"""
    try:
        db = _init_mongo_connect(database_name=database_name)
        sales_template_db = db['sales_template_db']
        
        # 检查是否已存在相同的记录
        existing = sales_template_db.find_one({
            'industry_id': industry_id,
            'brand_id': brand_id,
            'template_id': template_id
        })
        
        if existing:
            sales_template_db.update_one(
                {'industry_id': industry_id, 'brand_id': brand_id, 'template_id': template_id},
                {'$set': {'template_content': template_content}}
            )
            return "模板内容已更新！"
        
        # 插入新记录
        sales_template_db.insert_one({
            'industry_id': industry_id,
            'brand_id': brand_id,
            'template_id': template_id,
            'template_content': template_content
        })
        return "模版内容已成功存入数据库！"
    except Exception as e:
        return f"保存失败：{str(e)}"
    
def show_new_faq_content():
    return [
        gr.update(visible=False), # industry_dropdown
        gr.update(visible=False), # brand_dropdown
        gr.update(visible=False), # tempalte_dropdown
        gr.update(visible=False), # template_content
        gr.update(visible=False),
        gr.update(visible=False), # new_template_row
        gr.update(visible=False), # new_template_content
        gr.update(visible=True, value=''), # new_faq_row
        gr.update(visible=True, value=''), # new_faq_content
        gr.update(visible=False), # save_button 
        gr.update(visible=True) # save_faq_button
    ]

def save_faq_to_db(industry_id, brand_id, template_id, faq_content, **kwargs):
    try:
        faq_res = insert_faq(industry_id, brand_id, template_id, faq_content)
        print(faq_res)
        db = _init_mongo_connect(database_name=database_name)
        faq_template_db = db['faq_template_db']
        
        # check if there is any same record
        existing = faq_template_db.find_one({
          "industry_id": industry_id,
          "brand_id": brand_id,
          "template_id": template_id
        })
        # update existing record
        if existing:
          faq_template_db.update_one(
          {"industry_id": industry_id, "brand_id": brand_id, "template_id": template_id},
          {"$set": {"faq_content": faq_content}}
          )
          return "FAQ has been updated!"
        # insert new record
        faq_template_db.insert_one({
          'industry_id': industry_id,
          "brand_id": brand_id,
          "template_id": template_id,
          "faq_content": faq_content
        })
        return "New FAQ has been inserted!"
    except Exception as e:
        print(f"faq插入失败: {str(e)}")

    pass
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

def save_with_confirmation(industry_id, brand_id, template_id):
    """带确认对话框的保存功能"""
    return [
        gr.update(visible=True),
        f"确定要保存话术模版到:\n行业id: {industry_id}\n品牌id: {brand_id}\n模板id: {template_id}吗？"
    ]

def confirm_save(industry_id, brand_id, template_id, template_content, confirmed):
    """确认保存后的处理"""
    if not confirmed:
        return [gr.update(visible=False), "已取消保存"]

    result = save_template_to_db(industry_id, brand_id, template_id, template_content)
    return [gr.update(visible=False), result]

def save_faq_with_confirmation(industry_id, brand_id, template_id):
    return [
        gr.update(visible=True),
        f"确认要保存FAQ知识到:\n行业id: {industry_id}\n品牌id: {brand_id}\n模版id: {template_id}吗？"
    ]

def confirm_faq_save(industry_id, brand_id, template_id, faq_content, confirmed):
    if not confirmed:
        return [gr.update(visible=False), '已取消保存']
    result = save_faq_to_db(industry_id, brand_id, template_id, faq_content)
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
        # init_mess = init_mess_store[random.randint(0, len(init_mess_store)-1)]
        init_mess = "您好，这里是深圳艺星医疗整形医院。请问您之前有打过瘦脸针吗？"
        initial_message = [[None, init_mess]]
        chatbot = gr.Chatbot(value=initial_message, height=600)

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
                    new_faq_btn = gr.Button("🙋插入新FAQ知识")

                industry_dropdown = gr.Dropdown(choices=[], label="选择行业ID", allow_custom_value=True, value='', visible=False)
                brands_dropdown = gr.Dropdown(choices=[], label="选择品牌ID", allow_custom_value=True, value='', visible=False)
                template_dropdown = gr.Dropdown(choices=[], label="选择模板ID", allow_custom_value=True, value='', visible=False)

                with gr.Row(visible=False) as new_template_row:
                    new_industry_input = gr.Textbox(label="行业ID输入", value='', scale=1)
                    new_brand_input = gr.Textbox(label="品牌ID输入", value='', scale=1)
                    new_template_input = gr.Textbox(label="模板ID输入", value='', scale=1)
                with gr.Row(visible=False) as new_faq_row:
                    new_faq_industry_input = gr.Textbox(label='行业ID输入', value='', scale=1)
                    new_faq_brand_input = gr.Textbox(label='品牌ID输入', value='', scale=1)
                    new_faq_template_input = gr.Textbox(label='模版ID输入', value='', scale=1)                    
                new_template_content = gr.TextArea(label="模板内容输入", lines=5, visible=False)
                new_faq_content = gr.TextArea(label='FAQ知识对输入', lines=5, placeholder="'query': 想问问瘦脸项目, 'answer': 我们的瘦脸项目有玻尿酸针", visible=False)
                save_faq_btn = gr.Button("💾存入FAQ数据库", visible=False)
                save_btn = gr.Button("💾存入数据库", visible=False)
                
                with gr.Group(visible=False) as confirm_box:
                    gr.Markdown("### 确认保存")
                    confirm_text = gr.Markdown("")
                    with gr.Row():
                        confirm_yes = gr.Button("确认")
                        confirm_no = gr.Button("取消")
                with gr.Group(visible=False) as confirm_faq_box:
                    gr.Markdown("### 确认保存")
                    confirm_faq_text = gr.Markdown("")
                    with gr.Row():
                        confirm_faq_yes = gr.Button("确认")
                        confirm_faq_no = gr.Button("取消")

                
            with gr.Column(scale=2):
                template_content = gr.TextArea(label="模版内容预览", interactive=False, visible=False, lines=10)
                faq_content_display = gr.TextArea(label="FAQ内容预览", interactive=False, visible=False, lines=10)  # New TextArea for FAQ content
        # 事件绑定
        connect_btn.click(fn=connect_database, inputs=None, outputs=[industry_dropdown, template_dropdown, template_content, faq_content_display, status_message, new_template_row, new_template_content, new_faq_row, new_faq_content, save_btn, save_faq_btn], queue=False)
        
        industry_dropdown.change(fn=update_brands_choices, inputs=industry_dropdown, outputs=[brands_dropdown, template_dropdown, template_content, faq_content_display, status_message], queue=False)

        brands_dropdown.change(fn=update_template_choices, inputs=[industry_dropdown, brands_dropdown], outputs=[template_dropdown, template_content, faq_content_display, status_message], queue=False)

        template_dropdown.change(fn=show_template_content, inputs=[industry_dropdown, brands_dropdown, template_dropdown], outputs=[template_content, faq_content_display, status_message], queue=False)

        new_template_btn.click(fn=show_new_template_input, inputs=None, outputs=[industry_dropdown, brands_dropdown, template_dropdown, template_content, faq_content_display, new_template_row, new_template_content, new_faq_row, new_faq_content, save_btn, save_faq_btn], queue=False)

        new_faq_btn.click(fn=show_new_faq_content, inputs=None, outputs=[industry_dropdown, brands_dropdown, template_dropdown, template_content, faq_content_display, new_template_row, new_template_content, new_faq_row, new_faq_content, save_btn, save_faq_btn], queue=False)
        
        save_btn.click(fn=save_with_confirmation, inputs=[new_industry_input, new_brand_input, new_template_input], outputs=[confirm_box, confirm_text], queue=False)

        confirm_yes.click(fn=confirm_save, inputs=[new_industry_input, new_brand_input, new_template_input, new_template_content, gr.Textbox(value=True, visible=False)], outputs=[confirm_box, confirm_text], queue=False)

        confirm_no.click(fn=confirm_save, inputs=[new_industry_input, new_brand_input, new_template_input, new_template_content, gr.Textbox(value=False, visible=False)], outputs=[confirm_box, confirm_text], queue=False)

        save_faq_btn.click(fn=save_faq_with_confirmation, inputs=[new_faq_industry_input, new_faq_brand_input, new_faq_template_input], outputs=[confirm_faq_box, confirm_faq_text], queue=False)

        confirm_faq_yes.click(fn=confirm_faq_save, inputs=[new_faq_industry_input, new_faq_brand_input, new_faq_template_input, new_faq_content, gr.Textbox(value=True, visible=False)], outputs=[confirm_faq_box, confirm_faq_text], queue=False)
        
        confirm_faq_no.click(fn=confirm_faq_save, inputs=[new_faq_industry_input, new_faq_brand_input, new_faq_template_input, new_faq_content, gr.Textbox(value=False, visible=False)], outputs=[confirm_faq_box, confirm_faq_text], queue=False)
demo1.launch(server_name="0.0.0.0", server_port=7880)
