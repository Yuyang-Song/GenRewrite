import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from transformers import LongformerTokenizer, LongformerModel
from collections import defaultdict
import torch

class suggest_select_rewrite:
    def __init__(self, json_file,k = 3):
        # 读取JSON文件并解析所有规则
        with open(json_file, 'r') as f:
            self.data = json.load(f)
        self.rules_by_group = defaultdict(list) # key -> group_id, value -> list of rules
        self.rules_by_query = defaultdict(list) # key -> query, value -> list of rules
        self.k = k
        self.rules = []
        self.path = json_file
        self.hash = {}
        self.query = []
        # 本地加载Longformer模型和分词器
        self.tokenizer = LongformerTokenizer.from_pretrained('../config_file/longformer/')
        self.model = LongformerModel.from_pretrained('../config_file/longformer/')
        self.load_json() 
        # 初始化二维哈希列表

    def load_json(self):
        with open(self.path, 'r') as file:
            json_data = json.load(file)

        for key, value in json_data.items():
            if key.startswith("rules_"):
                for rule in value:
                    rewrite_rule = rule.get("rewrite_rule")
                    query = rule.get("query_list", {}).get("query_1", {}).get("query")
                    group_id = rule.get("group_id")
                    if query:
                        self.query.append(query)
                        self.rules_by_query[query].append(rule)
                        if rewrite_rule:
                            self.rules.append(rewrite_rule)
                            if group_id:
                                self.hash[rewrite_rule] = group_id  # 将rewrite_rule与group_id关联
                                self.rules_by_group[group_id].append(rule)  # 关联group_id与rule


    def embed_query(self, query):
        # 将查询转为Longformer模型的输入
        inputs = self.tokenizer(query, return_tensors="pt", max_length=512, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy()

    def get_top_k_similar_queries(self, input_query):
        input_embedding = self.embed_query(input_query)
        
        # 计算所有查询的嵌入并找出top-k相似查询
        # queries = [rule['query_list']['query_1']['query'] for rule in self.rules]
        queries = self.query
        embeddings = np.array([self.embed_query(query) for query in queries])
        
        # 将三维数组降为二维
        input_embedding = input_embedding.reshape(1, -1)
        embeddings = embeddings.reshape(embeddings.shape[0], -1)
        
        similarities = cosine_similarity(input_embedding, embeddings)[0]
        top_k_indices = np.argsort(similarities)[-self.k:]
        
        return [self.query[i] for i in top_k_indices], similarities[top_k_indices]

    def calculate_score(self, top_k_queries, similarities):
        # 计算每个group的分数
        group_scores = {}
        total_weight = sum([1/distance for distance in similarities])

        for i, query in enumerate(top_k_queries):
            weight = (1 / similarities[i]) / total_weight
            rules_for_query = self.rules_by_query[query]
            # 搞出query对应的所有rewrite_rule
            query_rule_set = set([rule['rewrite_rule'] for rule in rules_for_query])
            
            for group_id, group_rules in self.rules_by_group.items():
                # 搞出group对应的所有rewrite_rule
                group_rule_set = set([rule['rewrite_rule'] for rule in group_rules])
                indicator = 1 if query_rule_set & group_rule_set else 0  # 使用集合交集判断
                
                benefit = 1  # 先设置benefit默认值，值为1
                # 鲁棒性判断，其实没必要
                if group_id not in group_scores:
                    group_scores[group_id] = 0
                group_scores[group_id] += weight * indicator * benefit
                        
        return group_scores

    def select_best_nlr2(self, input_query):
        # 获取最相似的top-k查询
        top_k_queries, similarities = self.get_top_k_similar_queries(input_query)
        
        # 计算每个group的分数
        group_scores = self.calculate_score(top_k_queries, similarities)
        
        # 按分数排序并选出top-k个group中的最佳NLR2
        sorted_groups = sorted(group_scores.items(), key=lambda item: item[1], reverse=True)[:self.k]
        selected_nlr2s = []
        for group_id, score in sorted_groups:
            best_nlr2 = max(
                self.rules_by_group[group_id],
                key=lambda x: similarities[top_k_queries.index(x['query_list']['query_1']['query'])]
            )
            selected_nlr2s.append(best_nlr2['rewrite_rule'])
        
        return selected_nlr2s
    
# 使用示例：
# selector = NLR2Selector('../data/reportory.json')
# 注意列表倒序
# best_nlr2s = selector.select_best_nlr2("IMPORVE SELECT * FROM table3 WHERE condition3")[::-1]
# print(best_nlr2s)



# selector = NLR2Selector('../data/reportory.json')

# print(selector.rules)
# print(selector.query)
# print(selector.hash)

# # 获取最相似的top-k查询
# best_queries, similarities = selector.get_top_k_similar_queries("IMPORVE SELECT * FROM table3 WHERE condition3")

# # 打印结果
# print("Best Queries:", best_queries)
# print("Similarities:", similarities)

# group_scores = selector.calculate_score(best_queries, similarities)
# print(group_scores)

# best_nlr2s = selector.select_best_nlr2("example input query")
# print(best_nlr2s)