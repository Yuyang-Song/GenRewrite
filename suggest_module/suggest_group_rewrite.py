import sys
import os
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from pipeline_module.knowledgebase import NLR2KnowledgeBase
from pipeline_module.gpt import GPT

class NLR2GroupEstimator:
    def __init__(self, csv_path='../config_file/nlr2s.csv', knn_model_path='../config_file/knn_model.pkl', k=5):
        self.knowledge_base = NLR2KnowledgeBase(csv_path=csv_path, knn_model_path=knn_model_path, k=k)
        self.gpt = GPT()

    def _llm_group_prediction(self, target_nlr2, candidates):
        prompt = f"Input: {target_nlr2}\n"
        prompt += "Please select the rewrite rule that is strictly the same as the above rule and give your explanation (just give one answer). If not, please select the first item 'Unseen rule'. Options:\n"
        prompt += "1. Unseen rule\n"
        for i, candidate in enumerate(candidates):
            prompt += f"{i + 2}. {candidate}\n"
        
        response = self.gpt.get_GPT_response(prompt)
        
        for candidate in candidates:
            if candidate in response:
                return candidate
        
        return "Unseen rule"

    def estimate_group(self, target_nlr2):
        target_embedding = self.knowledge_base._embed(target_nlr2)
        distances, indices = self.knowledge_base.find_neighbors(target_embedding)
        
        candidates = [self.knowledge_base.nlr2_texts[i] for i in indices[0]]
        chosen_group = self._llm_group_prediction(target_nlr2, candidates)
        
        if chosen_group == "Unseen rule":
            return "New Group"
        else:
            return chosen_group

# Example usage
# estimator = NLR2GroupEstimator(csv_path='nlr2s.csv', knn_model_path='knn_model.pkl', k=3)
# estimator.knowledge_base.add_nlr2("Remove unnecessary columns from the GROUP BY clause", "Group 1")
# estimator.knowledge_base.add_nlr2("Remove unnecessary table joins", "Group 2")
# estimator.knowledge_base.add_nlr2("Use explicit join syntax instead of comma-separated tables in the from clause", "Group 3")

# new_nlr2 = "Replace implicit joins with explicit joins"
# group = estimator.estimate_group(new_nlr2)
# print(f"The estimated group for the new NLR2 is: {group}")


import math
from collections import defaultdict

class NLR2BenefitEstimator:
    def __init__(self):
        self.query_rewrites = defaultdict(list)  # 存储查询及其重写规则的性能提升
        self.group_benefits = defaultdict(list)  # 存储每个组的规则性能提升

    def add_rewrite(self, query, rewritten_query, group, speedup):
        """
        添加一个重写规则及其性能提升。
        """
        self.query_rewrites[query].append((rewritten_query, group, speedup))
        self.group_benefits[group].append(speedup)

    def geometric_mean(self, nums):
        """
        计算几何平均值。
        """
        product = math.prod(nums)
        return product ** (1.0 / len(nums))

    def estimate_group_benefit(self, group):
        """
        估算一个组的总体效益评分。
        """
        if group not in self.group_benefits or not self.group_benefits[group]:
            return 0
        return self.geometric_mean(self.group_benefits[group])

    def estimate_all_group_benefits(self):
        """
        估算所有组的总体效益评分。
        """
        return {group: self.estimate_group_benefit(group) for group in self.group_benefits}

# 示例用法
# estimator = NLR2BenefitEstimator()
# estimator.add_rewrite("SELECT * FROM table1", "SELECT * FROM table1 WHERE id > 10", "Group 1", 5.0)
# estimator.add_rewrite("SELECT * FROM table1", "SELECT * FROM table1 JOIN table2 ON table1.id = table2.id", "Group 1", 10.0)
# estimator.add_rewrite("SELECT * FROM table1", "SELECT id, name FROM table1", "Group 2", 2.0)

# group_benefits = estimator.estimate_all_group_benefits()
# print(group_benefits)