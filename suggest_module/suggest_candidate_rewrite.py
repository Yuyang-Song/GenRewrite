import sys
import os
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from pipeline_module.gpt import GPT
from suggest_module.suggest_candidate_rewrite import suggest_group_rewrite
from pipeline_module.knowledgebase import NLR2KnowledgeBase

class suggest_candidate_rewrite:
    def __init__(self, gpt, query_pool, hints_pool):
        self.gpt = gpt
        self.query_pool = query_pool
        self.hints_pool = hints_pool
        
    
    def generate_prompt(self, query, hints):
        prompt = (
            f"Input:\n{query}\n"
            "Rewrite this query to improve performance. Describe the rewrite rules you are using (you must not include any specific query details in the rules, e.g., table names, column names, etc). Be concise.\n"
            "Here are some hints that you might consider when rewriting the query:(And also you can use another rewirte rules based on your thought)\n"
            f"{hints}\n"
            "please return the answer in the following format:\n"
            "Candidate rewrite:{Candidate rewrite based on the rewrite rules}\n"
            "Expalnation:{a list of NLR2s actually applied}"
        )
        return prompt

    def suggest_and_explain(self, query, hints):
        """
        use LLM to suggest and help to rewrite, generating the NLR2 to explain the rewrite
        """
        response = self.generate_prompt(query, hints)
        answer = self.gpt.get_GPT_response(response)
        # response = self(prompt)  
        candidate_rewrite, explanation = self.parse_response(answer)
        return candidate_rewrite, explanation
    
    def parse_response(self, response):
        """
        解析LLM的响应以提取候选重写和NLR2解释
        """
        # 使用正则表达式提取候选重写和解释部分
        rewrite_match = re.search(r"Candidate rewrite:\s*```sql\s*(.*?)\s*```", response, re.DOTALL)
        explanation_match = re.search(r"Explanation:\s*(.*)", response, re.DOTALL)

        if rewrite_match and explanation_match:
            candidate_rewrite = rewrite_match.group(1).strip()
            explanation = explanation_match.group(1).strip()

            # 提取 Explanation 中 ** ** 的内容
            rules = re.findall(r"\*\*(.*?)\*\*", explanation)
            explanation = "\n".join(rules)
            
            return candidate_rewrite, explanation
        else:
            return None, None


class NLR2GroupEstimator:
    def __init__(self, csv_path='../nlr2_data/nlr2s.dataset.json', knn_model_path='../nlr2_data/knn.pkl', k=5):
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
estimator = NLR2GroupEstimator(csv_path='nlr2s.csv', knn_model_path='knn_model.pkl', k=3)
estimator.knowledge_base.add_nlr2("Remove unnecessary columns from the GROUP BY clause", "Group 1")
estimator.knowledge_base.add_nlr2("Remove unnecessary table joins", "Group 2")
estimator.knowledge_base.add_nlr2("Use explicit join syntax instead of comma-separated tables in the from clause", "Group 3")

new_nlr2 = "Replace implicit joins with explicit joins"
group = estimator.estimate_group(new_nlr2)
print(f"The estimated group for the new NLR2 is: {group}")



query = "SELECT COUNT(DISTINCT 'contacts'.'id') FROM 'contacts' LEFT OUTER JOIN 'people' ON 'people'.'id' = 'contacts'.'person_id' LEFT OUTER JOIN 'profiles' ON 'profiles'.'person_id' = 'people'.'id' WHERE 'contacts'.'user_id' = 1945"

hints = """
Pre-calculate aggregates in subqueries
Remove unnecessary UNION ALL operation
Avoid using arithmetic operations in WHERE clause
Replace implicit JOINs with explicit JOINs
"""



# gpt = GPT()
# suggest = suggest_candidate_rewrite(gpt, query, hints)
# candidate_rewrite, explanation = suggest.suggest_and_explain(query, hints)


# print(f"Candidate Rewrite:\n{candidate_rewrite}")
# print(f"Explanation:\n{explanation}")



