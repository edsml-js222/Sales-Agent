import os
import openai

class ChatGPT:
    def __init__(self, OPENAI_API_KEY, OPENAI_API_BASE) -> None:
        openai.api_key = OPENAI_API_KEY
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

        os.environ["OPENAI_API_BASE"] = OPENAI_API_BASE
        openai.api_base = os.getenv("OPENAI_API_BASE")

    def predict(self, msg, temperature=0.01):
        res = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            temperature=temperature,
            messages=[{
                "role": "user",
                "content": msg
            }
            ]
        )
        return res.choices[0].message["content"]
    
    def predict_v1(self, msg, model="gpt-4o-mini", temperature=0.01):
        completion = openai.chat.completions.create(
                            model=model,
                            temperature=temperature,
                            messages=[
                                {"role": "user", "content": msg}
                            ],
                            stream=False
                            )
        return completion.choices[0].message.content

    def predict_stream(self, msg, model="gpt-4o-mini", temperature=0.01):
        response = openai.ChatCompletion.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "user", "content": msg}
                ],
            stream = True
            )
        return response

    def predict_stream_v1(self, msg, model="gpt-4o-mini", temperature=0.01):
        import openai
        completion = openai.chat.completions.create(
                            temperature=temperature,
                            model=model,
                            messages=[
                                {"role": "user", "content": msg}
                            ],
                            stream=True
                            )
        return completion



def openai_predict(prompt, OPENAI_API_BASE, OPENAI_API_KEY, model, temperature=0.01, timeout=10):
    import openai
    openai.api_key = OPENAI_API_KEY
    openai.base_url = OPENAI_API_BASE
    completion = openai.chat.completions.create(
                        model=model,
                        temperature=temperature,
                        messages=[{"role": "user", "content": prompt}],
                        timeout=timeout
                        )
    # print(completion, flush=True)
    return completion.choices[0].message.content

def openai_predict_stream(prompt, OPENAI_API_BASE, OPENAI_API_KEY, model, temperature=0.01, timeout=10):
    import openai
    openai.api_key = OPENAI_API_KEY
    openai.base_url = OPENAI_API_BASE
    completion = openai.chat.completions.create(
                            temperature=temperature,
                            model=model,
                            messages=[
                                {"role": "user", "content": prompt}
                            ],
                            stream=True,
                            timeout=timeout
                            )
    return completion