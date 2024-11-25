from triton_inference.get_llm_res import get_llm_res
import json

def get_intention_level(user_history, model_name="Doubao-pro-128k", temperature=0.1) -> dict:
    prompt = f"""
    需要你根据用户跟智能客服沟通过程中的所有输入的文本内容，判断这个用户留下个人信息的意向等级为高或者低。如果用户输入的文本内容中有姓名和联系方式，则认为用户的意向等级为高，否则认为用户的意向等级为低。请你先思考你做出判断的原因，然后给出你的判断。
    用户输入的文本内容为：{user_history}
    输出格式为: {{"intention_level": "高" or "低", "intention_level_clue": "判断依据"}}

    示例:
    用户输入: [{{"user": "你好"}}, {{"user": "有没有瘦脸相关的"}}, {{"user": "行吧，你们哪里有店？"}}, {{"user": "我姓张, 12383295731"}}]
    输出: {{"intention_level": "高", "intention_level_clue": "用户在最后输入了姓名和联系方式"}}

    用户输入: [{{"user": "你好啊"}}, {{"user": "想问问皮肤有关的项目"}}, {{"user": "我能约个线下来体验一下吗"}}, {{"user": "姓李"}}]
    输出: {{"intention_level": "低", "intention_level_clue": "用户只提供了姓氏，没有提供联系方式"}}

    用户输入: [{{"user": "你们这里有什么项目"}}, {{"user": "我第一次做医美，没什么经验，主要想体验一下"}}, {{"user": "行，那你先加下我微信，微信聊"}}, {{"user": "1823754182"}}]
    输出: {{"intention_level": "低", "intention_level_clue": "用户只提供了联系方式, 没有提供姓名"}}
    """
    messages = [{"role": "user", "content": prompt}]
    intention_result, _, _ = get_llm_res(messages, model_name, temperature)
    return json.loads(intention_result)