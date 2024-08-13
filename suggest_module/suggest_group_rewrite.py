import sys
import os

# 将 pipeline_module 路径添加到系统路径中
module_path = os.path.abspath(os.path.join('..'))  # 根据实际路径调整
if module_path not in sys.path:
    sys.path.append(module_path)
import textwrap
from transformers import BertModel, BertTokenizer
from sklearn.metrics.pairwise import euclidean_distances
import numpy as np
from collections import defaultdict
from pipeline_module.gpt import GPT
import json

# BERT Embedding Model
class sugget_group_rewrite:
    def __init__(self,path,k=3):
        self.gpt = GPT()
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased')
        self.load_rewrite_rules = []
        self.hash = {}  # 初始化一个字典来保存rewrite_rule到group_id的映射
        self.path = path
        self.embeddings = None
        self.k = k

    def embed(self, text):
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True)
        outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).detach().numpy()
    
    def load_json(self):
        with open(self.path, 'r') as file:
            json_data = json.load(file)

        for key, value in json_data.items():
            if key.startswith("rules_"):
                for rule in value:
                    rewrite_rule = rule.get("rewrite_rule")
                    group_id = rule.get("group_id")
                    if rewrite_rule:
                        self.load_rewrite_rules.append(rewrite_rule)
                        if group_id:
                            self.hash[rewrite_rule] = group_id  # 将rewrite_rule与group_id关联
        
        # 在加载 rewrite rules 后预计算它们的嵌入向量
        self.embeddings = np.vstack([self.embed(rule) for rule in self.load_rewrite_rules])
        # return self.embeddings

    def knn(self, input_sentence):
        # 对输入句子进行编码
        input_embedding = self.embed(input_sentence)
        
        # 计算欧氏距离
        distances = euclidean_distances(input_embedding, self.embeddings)[0]
        
        # 获取距离最近的句子的索引，按照距离从小到大排序
        sorted_indices = np.argsort(distances)
        
        top_k_sentences = []
        seen_groups = set()
        
        # 遍历排序后的索引，选择属于不同group_id的句子
        for index in sorted_indices:
            rule = self.load_rewrite_rules[index]
            group_id = self.hash.get(rule)
            
            if group_id not in seen_groups:
                top_k_sentences.append(rule)
                seen_groups.add(group_id)
            
            # 当找到的句子数量达到k时停止
            if len(top_k_sentences) >= self.k:
                break
        
        return top_k_sentences

    
    def predict_group(self, input_query, candidates):
        options = "1. Unseen rule\n"
        for i, candidate in enumerate(candidates, start=2):
            options += f"{i}. {candidate}\n"
        
        prompt = textwrap.dedent(f"""
            <description>
            {input_query}
            Please select the rewrite rule that is strictly the same as the above rule and give your explanation (just give one answer). 
            If not, please select the first item “Unseen rule”.
            <Options>
            {options}

            <demand>
            JSON RESULT TEMPLATE:
            {{
                "option": , // the selected option(use the content of option, do not use the index
                "Explanation": ,      // give the Explanation of the selected option
            }}
            """
            
        )
        response = self.gpt.get_GPT_response(prompt,json_format=True)
        return response
    
        # 用于添加新的规则到JSON文件中
    def add_rule_to_json(self, group_id, rewrite_rule, query):
        # 读取 JSON 文件
        with open(self.path, 'r') as file:
            json_data = json.load(file)
        
        # 检查并初始化 rule_number
        rule_number = json_data['group_info'].get('rule_number')
        if rule_number is None:
            rule_number = 0
        
        # 检查并初始化 group_number
        group_number = json_data['group_info'].get('group_number')
        if group_number is None:
            group_number = 0
        
        # 更新group_info规则信息
        rule_number += 1
        json_data['group_info']['rule_number'] = rule_number
        
        json_data[f'rules_{rule_number}'] = []
        
        # 创建新的规则条目
        new_rule = {
            "rule_id": rule_number,
            "group_id": group_id,
            "rewrite_rule": rewrite_rule,
            "query_list": {
                "query_number": 1,
                "query_1": {
                    "id": 1,
                    "query": query
                }
            }
        }
        # 如果需要添加新组
        if int(group_id) > int(group_number):
            # 更新group_info的信息
            group_number += 1
            json_data['group_info']['group_number'] = group_number
            
        # 将新规则添加到 'rules' 列表中
        json_data[f'rules_{rule_number}'].append(new_rule)

        # 写回 JSON 文件
        with open(self.path, 'w') as file:
            json.dump(json_data, file, indent=3)

        print(f"Added rule with group_id: {group_id}: {rewrite_rule} to {self.path}")
    
    
    def add_rule_in_group(self,rewrite_rule,query):
        self.load_json()
        top_k_sentences = self.knn(rewrite_rule)
        response = self.predict_group(rewrite_rule, top_k_sentences)['option']
        group_id = self.hash.get(response)
        self.add_rule_to_json(group_id,rewrite_rule,query)


# 示例使用
# reportory_path = "../data/reportory.json"
# embedding_model = sugget_group_rewrite(reportory_path,k = 3)
# embedding_model.add_rule_in_group("SELECT * FROM table1 WHERE condition1.","This is a test query.")


# reportory_path = "../data/reportory.json"
# embedding_model = sugget_group_rewrite(reportory_path,k = 3)
# embedding_model.load_json()

# input_sentence = "SELECT * FROM table1 WHERE condition1."
# top_k_sentences = embedding_model.knn(input_sentence)

# print("Top-K most similar sentences:")
# for sentence in top_k_sentences:
#     print(sentence)


# response = embedding_model.predict_group(input_sentence, top_k_sentences)['option']
# # print(response)
# # 打印hash字典
# # print("Rewrite Rule to Group ID mapping:")
# # for rule, group_id in embedding_model.hash.items():
# #     print(f"Rule: {rule}, Group ID: {group_id}")
    
# group_id = embedding_model.hash.get(response)
# print(group_id)

# embedding_model.add_rule_to_json(group_id,input_sentence,"This is a test query.")

