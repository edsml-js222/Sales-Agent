import os
import sys
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
from utils.connect_mongo import _init_mongo_connect


class SetTemplate:
    def __init__(self, project_name: str, industry_id: str, brand_id: str, template_id: str):
        self.db = _init_mongo_connect(project_name)
        self.sales_template_db = self.db["sales_template_db"]
        self.sales_template = self.sales_template_db.find_one({"industry_id": industry_id, "brand_id": brand_id, "template_id": template_id})
        self.sales_template_intention = self.sales_template['template_intention']
        self.sales_template_content = self.sales_template['template_content']
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