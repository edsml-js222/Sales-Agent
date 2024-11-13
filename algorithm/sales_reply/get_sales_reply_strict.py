from triton_inference.get_llm_res import get_llm_res

template_intention = {"问好": 1, "询问项目": 2, "提供个人有效信息": 3, "结束对话": 4}

node_content_1 = '1'
node_content_12 = '12'
node_content_123 = '123'
node_content_1234 = '1234'
node_content_124 = '124'
node_content_1243 = '1243'
node_content_13 = '13'
node_content_132 = '132'
node_content_1324 = '1324'
node_content_134 = '134'
node_content_1342 = '1342'
node_content_14 = '14'
node_content_142 = '142'
node_content_1423 = '1423'
node_content_143 = '143'
node_content_1432 = '1432'

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

class GetSalesReplyStrict:
    def __init__(self, template_intention: dict, template_content: dict):
        self.template_intention = template_intention
        self.template_content = template_content
        self.template_up_limit = len(template_content) # 会话意图上限
        self.dialogue_count = 0 # 会话轮次
        self.user_intention = [] # 用户意图

    def intention_match_llm(self, user_input: str, model_name: str = "gpt-4o-mini", temperature: float = 0.1) -> str:
        """
        意图匹配
        """
        intention_list = list(self.template_intention.keys())
        prompt = f"""
        你需要根据用户输入的内容，判断用户的这个输入属于哪一个意图，请从以下列表中选择一个最合适的意图：{intention_list}
        用户输入的内容为：{user_input}
        请以json格式输出，例如{{"intention": ""}}。
        你可以参考的示例为：
            用户输入：您好
            你的返回：{{"intention": "问好"}}

            用户输入：我想了解一下你们瘦脸有什么项目吗
            你的返回：{{"intention": "询问项目"}}

            用户输入：我姓李，电话是18238518283
            你的返回：{{"intention": "提供个人有效信息"}}

            用户输入：拜拜
            你的返回：{{"intention": "结束对话"}}
        你的返回是：
        """
        message = [
            {"role": "system", "content": "你是一名意图识别的专家，擅长从用户的输入中判断用户当前的意图"},
            {"role": "user", "content": prompt}]
        model_reply, input_tokens, output_tokens = get_llm_res(message, model_name, temperature=temperature)
        return model_reply

    def get_sales_reply(self, user_intention: str) -> dict:
        """
        获取销售回复
        """
        self.dialogue_count += 1
        dialogue_circle = self.dialogue_count // self.template_up_limit
        # 如果当前轮次是第一个轮次，并且用户意图不是问好，则默认用户意图是问好
        if self.dialogue_count % self.template_up_limit == 1 and user_intention != "问好":
            self.user_intention.append("问好")
        self.user_intention.append(user_intention)
        template_key = (''.join(str(template_intention[intention] for intention in self.user_intention[dialogue_circle * self.template_up_limit: self.dialogue_count])))
        response = self.template_content[template_key]
        
        return response
