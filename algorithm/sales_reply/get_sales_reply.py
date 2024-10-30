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
    你的任务是尽你所能推销你所在行业的产品，并且在合适的时机主动提出请求引导客户留下他们的个人信息，比如姓名，联系方式，和需求。记住你的最终任务是让客户自愿留下他们的个人信息，你的任何行为都应该为达成这个任务而努力。请你首先思考客户最新的信息所包含的意图是什么，然后给出你的回复。
      -- <历史对话>中是你和客户的多轮对话记录，你可以从中了解到客户的交流习惯，以及你们交流的进度，你的回答应该参考你们最新的历史对话记录，让你们的交流处于一个连续的状态。
      -- <销售话术模版>中是一种特定的场景下你和客户的交流记录，你可以从中了解到你这次与客户交流应该使用的语气和方式。
    客户最新的信息为：{user_input}
    以json格式输出,例如{{"customer_intention": "", "reply": ""}}。
    你的回答是：
    """
    message = [
        {"role": "system", "content": system_prompt_dict(industry_id)},
        {"role": "user", "content": prompt}]
    model_reply, input_tokens, output_tokens = get_llm_res(message, model_name, temperature)
    return model_reply, input_tokens, output_tokens