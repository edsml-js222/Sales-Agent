import os
import sys
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
from utils.connect_mongo import _init_mongo_connect

def run():
    industry_id = "医美"
    brand_id = "美丽人生"
    template_id = "美丽人生经典模版1"
    template_intention = {"问好": 1, "询问项目": 2, "提供个人有效信息": 3, "结束对话": 4}

    node_content_1 = '你好呀，我是美丽人生的客服小美，很高兴为您服务。'
    node_content_12 = '根据faq知识库回答'
    node_content_123 = '好的呀，记下您的信息了～会尽快安排专业顾问与您联系！'
    node_content_1234 = '有什么不清楚的都可以和我们的顾问联系哦，祝您有个美好的一天！'
    node_content_124 = '诶，您这边好像还没有留下联系方式呢，方便留下您的联系方式和名字嘛？'
    node_content_1243 = '好的，记下您的信息了～会尽快安排专业顾问与您联系！'
    node_content_13 = '好的呀，记下您的信息了～会尽快安排专业顾问与您联系！不过您好像还没说对咱们什么项目感兴趣呀，方便说一下嘛？'
    node_content_132 = '根据faq知识库回答'
    node_content_1324 = '有什么不清楚的都可以和我们的顾问联系哦，祝您有个美好的一天！'
    node_content_134 = '诶，您这边好像还没有留下联系方式呢，方便留下您的联系方式和名字嘛？'
    node_content_1342 = '根据faq知识库回答'
    node_content_14 = '诶，您这边是对什么项目有兴趣嘛？方便留下您的姓名和联系方式嘛，我们会有专门的顾问给您答疑解惑哦。'
    node_content_142 = '根据faq知识库回答'
    node_content_1423 = '好的呀，记下您的信息了～会尽快安排专业顾问与您联系！'
    node_content_143 = '好的呀，记下您的信息了～会尽快安排专业顾问与您联系！不过您好像还没说对咱们什么项目感兴趣呀，方便说一下嘛？'
    node_content_1432 = '根据faq知识库回答'

    template_content = {
        "1": node_content_1,
        "12": node_content_12,
        "123": node_content_123,
        "1234": node_content_1234,
        "124": node_content_124,
        "1243": node_content_1243,
        "13": node_content_13,
        "132": node_content_132,
        "1324": node_content_1324,
        "134": node_content_134,
        "1342": node_content_1342,
        "14": node_content_14,
        "142": node_content_142,
        "1423": node_content_1423,
        "143": node_content_143,
        "1432": node_content_1432,
    }
    project_name = "smart_salesman"
    db = _init_mongo_connect(project_name)
    sales_template_db = db["sales_template_db"]
    sales_template = sales_template_db.insert_one(
        {"industry_id": industry_id, 
         "brand_id": brand_id, 
         "template_id": template_id,
         "template_intention": template_intention,
         "template_content": template_content}
    )
    print(sales_template)

if __name__ == "__main__":
    run()
