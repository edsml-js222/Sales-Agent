import os
import sys
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
from utils.connect_mongo import _init_mongo_connect
from utils.data_structure import nodes_to_vets, DirectGraphAdjList

class SetTemplate:
    def __init__(self, project_name: str, industry_id: str, brand_id: str, template_id: str):
        # self.db = _init_mongo_connect(project_name)
        # # 基于有向图
        # self.reply_nodes_graph_db = self.db['reply_nodes_graph_db']
        # self.reply_nodes_graph_data = self.reply_nodes_graph_db.find_one({"industry_id": industry_id, "brand_id": brand_id, "template_id": template_id})
        # self.reply_nodes_graph = self.reply_nodes_graph_data['reply_nodes_graph']
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

        self.graph = DirectGraphAdjList(edges)

        # 初始实现方式 -- 基于树
        # self.sales_template_db = self.db["sales_template_db"]
        # self.sales_template = self.sales_template_db.find_one({"industry_id": industry_id, "brand_id": brand_id, "template_id": template_id})
        # self.sales_template_intention = self.sales_template['template_intention']
        # self.sales_template_content = self.sales_template['template_content']
        # self.template_intention = {"问好": 1, "询问项目": 2, "提供个人有效信息": 3, "结束对话": 4}

        # node_content_1 = '1'
        # node_content_12 = '12'
        # node_content_123 = '123'
        # node_content_1234 = '1234'
        # node_content_124 = '124'
        # node_content_1243 = '1243'
        # node_content_13 = '13'
        # node_content_132 = '132'
        # node_content_1324 = '1324'
        # node_content_134 = '134'
        # node_content_1342 = '1342'
        # node_content_14 = '14'
        # node_content_142 = '142'
        # node_content_1423 = '1423'
        # node_content_143 = '143'
        # node_content_1432 = '1432'

        # self.template_content = {
        #     "1": node_content_1,
        #     "12": node_content_12,
        #     "123": node_content_123,
        #     "1234": node_content_1234,
        #     "124": node_content_124,
        #     "1243": node_content_1243,
        #     "13": node_content_13,
        #     "132": node_content_132,
        #     "1324": node_content_1324,
        #     "134": node_content_134,
        #     "1342": node_content_1342,
        #     "14": node_content_14,
        #     "142": node_content_142,
        #     "1423": node_content_1423,
        #     "143": node_content_143,
        #     "1432": node_content_1432,
        # }