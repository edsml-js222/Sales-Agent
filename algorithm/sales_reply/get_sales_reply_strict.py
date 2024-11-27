import os
import sys
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
from triton_inference.get_llm_res import get_llm_res
from algorithm.sales_reply.set_template import SetTemplate
from utils.MilvusDB import Milvus
from utils.m3e_embedding import m3e_embedding
from utils.data_structure import nodes_to_vets, DirectGraphAdjList, Vertex

class GetSalesReplyStrict:
    def __init__(self, project_name: str, industry_id: str, brand_id: str, template_id: str):
        self.industry_dict = {"医美": "medical"}
        self.brand_dict = {"美丽人生": "beauty"}
        self.template_dict = {"美丽人生经典模版1": "classic_template1"}
        # 原版逻辑
        # self.template = SetTemplate(project_name, industry_id, brand_id, template_id)
        # self.template_intention = self.template.sales_template_intention
        # self.template_content = self.template.sales_template_content
        # self.template_up_limit = len(self.template_intention) # 会话意图上限
        # self.dialogue_count = 0 # 会话轮次
        # self.user_intention = [] # 用户意图
        # 修改后用有向图逻辑
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
        self.vets = nodes_to_vets(nodes=nodes)
        edges = [
            [self.vets[0], self.vets[1], "肯定"],
            [self.vets[0], self.vets[2], "否定"],
            [self.vets[0], self.vets[9], "拒绝"],
            [self.vets[1], self.vets[3], "all"],
            [self.vets[2], self.vets[3], "all"],
            [self.vets[3], self.vets[4], "拒绝"],
            [self.vets[3], self.vets[5], "肯定"],
            [self.vets[4], self.vets[6], "all"],
            [self.vets[5], self.vets[6], "all"],
            [self.vets[6], self.vets[7], "肯定"],
            [self.vets[6], self.vets[8], "拒绝"],
            [self.vets[6], self.vets[8], "其他"],
            [self.vets[7], self.vets[8], "拒绝"],
            [self.vets[7], self.vets[8], "其他"],
            [self.vets[7], self.vets[9], "提供个人信息"],
            [self.vets[8], self.vets[9], "all"]
        ]
        self.graph = DirectGraphAdjList(edges)
        self.reply_graph = self.graph.adj_list
        self.reply_intention = self.graph.intention_list
        self.dialogue_state = [self.vets[0]]
        self.dialogue_node_recording = [self.vets[0].index]

        self.industry_id = industry_id
        self.brand_id = brand_id
        self.template_id = template_id
        self.alias_name = project_name
        self.milvus_instance = Milvus(self.alias_name)
        self.collection_name = self.industry_dict[industry_id] + "_" + self.brand_dict[brand_id] + "_" + self.template_dict[template_id]
        self.collection_using = self.milvus_instance.link_collection(self.collection_name)

    def intention_match_llm(self, user_input: str, model_name: str = "Doubao-pro-128k", temperature: float = 0.1) -> str:
        """
        意图匹配
        """
        # intention_list = list(self.template_intention.keys())
        intention_list = self.reply_intention[self.dialogue_state[-1]]
        intention_list.append("询问项目")
        prompt = f"""
        你需要根据用户输入的内容，判断用户的这个输入属于哪一个意图，请从以下列表中选择一个最合适的意图：{intention_list}
        如果上述列表中有'all'出现，则直接返回{{"intention:" "all"}}
        用户输入的内容为：{user_input}
        请以json格式输出，例如{{"intention": ""}}。
        你可以参考的示例为：
            用户输入：打过瘦脸针
            你的返回：{{"intention": "肯定"}}

            用户输入：没打过瘦脸针
            你的返回：{{"intention": "否定"}}

            用户输入：想问问瘦脸针
            你的返回：{{"intention": "询问项目"}}

            用户输入：我姓李，电话是18238518283
            你的返回：{{"intention": "提供个人信息"}}

            用户输入：我不想回答你这个问题
            你的返回：{{"intention": "拒绝"}}
        你的返回是：
        """
        message = [
            {"role": "system", "content": "你是一名意图识别的专家，擅长从用户的输入中判断用户当前的意图"},
            {"role": "user", "content": prompt}]
        model_reply, input_tokens, output_tokens = get_llm_res(message, model_name, temperature=temperature)
        return model_reply
    
    def faq_reply(self, user_input: str) -> str:
        """
        问答回复
        """
        query_vector = m3e_embedding(user_input)
        search_res = self.milvus_instance.search(collection_using=self.collection_using, 
                                                 query=query_vector, topk=3, 
                                                 anns_field="faq_query", 
                                                 output_fields=["faq_answer"]
                                                 )
        search_res_top_content = search_res[0][0].entity.get("faq_answer")
        return search_res_top_content

    def get_sales_reply(self, user_intention: str, user_input: str) -> dict:
        """
        根据话术节点内定义的内容回复
        """
        # self.dialogue_count += 1
        # dialogue_circle = (self.dialogue_count - 1) // self.template_up_limit
        # # 如果当前轮次是第一个轮次，并且用户意图不是问好，则默认用户意图是问好
        # if self.dialogue_count % self.template_up_limit == 1 and user_intention != "问好":
        #     self.user_intention.append("问好")
        #     self.dialogue_count += 1
        # self.user_intention.append(user_intention)
        # template_key = ''.join(str(self.template_intention[intention]) for intention in self.user_intention[dialogue_circle * self.template_up_limit : self.dialogue_count])
        # print(f"template_key: {template_key}")
        # if user_intention == "询问项目":
        #     response = self.faq_reply(user_input)

        # else:
        #     response = self.template_content[template_key]
        
        # return response, template_key
        if user_intention == "询问项目":
            strict_reply_content = self.faq_reply(user_input)
            self.dialogue_node_recording.append("询问项目")
        else:
            latest_dialogue_state = self.reply_graph[self.dialogue_state[-1]][user_intention]
            self.dialogue_state.append(latest_dialogue_state)
            self.dialogue_node_recording.append(latest_dialogue_state.index)
            strict_reply_content = latest_dialogue_state.content
        return strict_reply_content, self.dialogue_node_recording
        
