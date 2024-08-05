from openai import OpenAI
import re
import json
import tiktoken
import json

import configparser

# # 创建 ConfigParser 对象
# config = configparser.ConfigParser()

# # 读取配置文件
# config.read('config.ini')

# # 读取 [parameters] 部分的变量
# budget = int(config['parameters']['budget'])
# min_speedup = float(config['parameters']['min_speedup'])

# # 读取 [gpt] 部分的变量
# api_base = config['gpt']['api_base']
# api_key = config['gpt']['api_key']

class GPT:
    # init function to initialize the GPT class using gpt-4o, ignoring the token and money cost termerarily
    def __init__(self):
        self.base_url = "https://one.aios123.com/v1"
        self.api_key = "sk-LR70O3o5qf5L9fIo62Da419a4bEd461bA7AcA3D3056a2310"
        self.model = "gpt-4o-mini"
        # self.api_key = "sk-Xmt8rI8NLSc9MUrm17C59c605b994f50Ab26Eb1d4f609423"
        # self.api_base = "https://api.f2gpt.com"
        # self.api_key = "sk-f2gpDc6IFUciFwkNfCJW6tNVyf45ef9RdkidGRXFZF6mnySj"
        # self.api_base = "https://api.openai.com/v1/"
        # self.api_key =  "sk-tMMrovQDfvGjWQIG5d6a4a2b3bEb4e3f919a578964Cf9319"
        

    def get_GPT_response(self, prompt,json_format = False):
        client = OpenAI(
            base_url = self.base_url,
            api_key = self.api_key
        )
        if(json_format == True):
            completion = client.chat.completions.create(
            temperature= 0.0,
            model = self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role":"system","content":"You should output JSON."},
                {"role": "user", "content": prompt},
            ]
            )
            answer = json.loads(completion.choices[0].message.content)

        else:
            completion = client.chat.completions.create(
            temperature= 0.0,
            model = self.model,
            messages=[
                {"role": "user", "content": prompt}
            ]
            )
            answer = completion.choices[0].message.content
        return answer
    
    def get_GPT_response_with_history(self, prompt1, prompt2, history):
        client = OpenAI(
            base_url = self.base_url,
            api_key = self.api_key
        )
        # 如果 history 是字典或列表，直接转换为字符串
        # print(type(history))
        if isinstance(history, (dict, list)):
            history_content = json.dumps(history)
        else:
            try:
                history_content = history # 
            except json.JSONDecodeError:
                history_content = history

        # 将 history 字符串格式化为所需的字典
        history_formatted = {"role": "assistant", "content": history_content}
        
        # print(history_formatted)
        # print(type(history_formatted))
        content = [
            {"role":"system","content":"You should output JSON."},
            {"role": "user", "content": prompt1},
            history_formatted,
            {"role": "user", "content": prompt2}
        ]
        completion = client.chat.completions.create(
        response_format={"type": "json_object"},
        temperature= 0.0,
        model = self.model,
        messages= content
        )
        answer = json.loads(completion.choices[0].message.content)
        return answer
#Example usage

# gpt = GPT()
# prompt = "What is the capital of France?"

# response = gpt.get_GPT_response(prompt,json_format=True)
# print(f"{response}")


# prompt1 = "What is the capital of France?"
# prompt2 = "重复一遍我的上一个问题？"
# reanswer = gpt.get_GPT_response(prompt1,json_format=True)
# reanswer = gpt.get_GPT_response(prompt1)
# print(f"{reanswer}\n")
# answer = gpt.get_GPT_response_with_history(prompt1, prompt2, reanswer)
# print(f"{answer}")
# print(f"{response2}")