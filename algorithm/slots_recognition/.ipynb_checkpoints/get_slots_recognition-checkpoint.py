from triton_inference.get_llm_res import get_llm_res
import json

class SlotInfo:
    def __init__(self):
        self.slots = {
            "姓名": "",
            "联系方式": "",
            "需求": "",
        }
        self.confidence = {
            "姓名": 0.0,
            "联系方式": 0.0,
            "需求": 0.0,
        }
    def to_dict(self):
        return {
            "slots": self.slots,
            "confidence": self.confidence
        }

def extract_slot_info(user_input: str, current_slots: dict, model_name="gpt-4o-mini", temperature=0.1) -> dict:
    """
    使用llm分析文本并且提取槽位信息
    """
    prompt = f"""
    请分析以下文本, 提取用户的个人信息。如果发现新信息, 请以JSON格式返回。
    需要提取的字段：姓名、联系方式、需求
    当前已知槽位信息：{current_slots["slots"]}
    当前已知槽位置信度：{current_slots["confidence"]}
    
    用户文本：{user_input}
    
    你可以参考的示例：
    
      -- 用户："瘦脸相关的吧"
      -- 你：[{{"slot": "需求", "value": "瘦脸", "confidence": 0.8}},
      
      -- 用户："美白"
      -- 你：[{{"slot": "需求", "value": "美白", "confidence": 0.8}},
    
    请以如下格式返回（只返回有新发现的字段）：
    [{{"slot": "姓名", "value": "张三", "confidence": 0.9}}, {{"slot": "联系方式", "value": "1234567890", "confidence": 0.8}}]
    
    """
    system_prompt = "你是一名资深的销售， 你非常擅长洞察到用户对话中的个人信息，比如用户的姓名，联系方式，需求等。"
    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    model_reply, _, _ = get_llm_res(message, model_name, temperature)

    try:
        new_slots = json.loads(model_reply)
        for slot in new_slots:
            if slot['confidence'] >= current_slots["confidence"][slot['slot']]:
                current_slots["slots"][slot['slot']] = slot['value']
                current_slots["confidence"][slot['slot']] = slot['confidence']
    except Exception as e:
        print(f"Error in extract_slot_info: {str(e)}")
    return current_slots