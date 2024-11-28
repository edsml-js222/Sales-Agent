import os
import sys
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
from utils.connect_mongo import _init_mongo_connect
from utils.data_structure import nodes_to_vets, DirectGraphAdjList

def base_directed_graph():
    nodes = [
        [1, "您好，这里是深圳艺星医疗整形医院。请问您之前有打过瘦脸针吗？"],
        [2, "请问您是男士还是女士，今年多大年龄呢？"],
        [3, "瘦脸针是针对咬肌肥大的医美技术，非常安全，一周见效，效果很好的，可以放心。您微信多少我加您，给您详细介绍下，我们现在瘦脸针做活动的"],
        [4, "那可以给您预约过来实际面诊医生看看呢，可以吗？"],
        [5, "您是有什么顾虑么？我们现在特价580，预约来院还送一次光子嫩肤的"],
        [6, "我们现在特价580，预约来院还送一次光子嫩肤的"],
        [7, "您是在深圳哪个区呢，您今天有空的话在市区可以申请一次免费打车接您过来面诊医生实际了解下。面诊咨询都是免费的，可以评估下您咬肌情况，您对方案和价格都满意再考虑做"],
        [8, "好的，那留个联系方式n可以先加个您的微信 我把具体定位发给您 还有我们医院介绍, 我帮您预约下时间"],
        [9, " 好的那您时间方便的话，过来之前可以拨打0755-12345678预约面诊医生时间，然后按预约时间过来就好。到时候见"],
        [10, "好的，再见"],
    ]
    vets = nodes_to_vets(nodes=nodes)
    # check vets
    # for vet in vets:
    #     print(vet.index)
    #     print(vet.content)
    #     print(vet)
    edges = [
        [vets[0], vets[1], "肯定"],
        [vets[0], vets[2], "否定"],
        [vets[0], vets[9], "拒绝"],
        [vets[1], vets[3], "all"],
        [vets[2], vets[3], "all"],
        [vets[3], vets[4], "拒绝"],
        [vets[3], vets[5], "肯定"],
        [vets[4], vets[6], "all"],
        [vets[5], vets[6], "all"],
        [vets[6], vets[7], "肯定"],
        [vets[6], vets[8], "拒绝"],
        [vets[6], vets[8], "其他"],
        [vets[7], vets[8], "拒绝"],
        [vets[7], vets[8], "其他"],
        [vets[7], vets[9], "留资"],
        [vets[8], vets[9], "all"]
    ]

    graph = DirectGraphAdjList(edges)
    project_name = "smart_salesman"
    industry_id = "医美"
    brand_id = "美丽人生"
    template_id = "美丽人生经典模版1"
    db = _init_mongo_connect(project_name)
    reply_nodes_graph_db = db['reply_nodes_graph_db']
    reply_nodes_graph_db.insert_one({
        "industry_id": industry_id,
        "brand_id": brand_id,
        "template_id": template_id,
        "reply_nodes_graph": graph
    })


def base_tree():
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
    # run()
    base_directed_graph()
