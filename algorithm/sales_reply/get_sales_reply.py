from triton_inference.get_llm_res import get_llm_res

def system_prompt_dict(industry_id):
    if industry_id == '默认':
        system_prompt = "你是一名资深的销售， 你很有亲和力，面对客户的咨询很有耐心"
    else:
        system_prompt = f"你是一名{industry_id}行业的资深销售，你既很熟悉{industry_id}业务，也很有亲和力，面对客户的咨询很有耐心。"
    return system_prompt


def get_sales_reply(industry_id, template_content, user_input, history, model_name="gpt-4o-mini", temperature=0.1):
    prompt = f"""
    <销售话术模版> {template_content} </销售话术模版>
    <客户咨询>: {user_input} </客户咨询>
    <历史对话>: {history} </历史对话>
    结合<历史对话>信息来回答<客户咨询>中客户的消息。<销售话术模版>中是你回答客户信息的时候可以参考的说话方式。
    以json格式输出,例如{{"customer_intention": "", "reply": ""}}
    你的回答是：
    """
    message = [
        {"role": "system", "content": system_prompt_dict(industry_id)},
        {"role": "user", "content": prompt}]
    model_reply, input_tokens, output_tokens = get_llm_res(message, model_name, temperature)
    return model_reply, input_tokens, output_tokens