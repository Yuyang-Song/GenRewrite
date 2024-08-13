import sys
import os
import re
import textwrap
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from pipeline_module.gpt import GPT

class suggest_candidate_rewrite:
    def __init__(self, gpt, query_pool, hints_pool):
        self.gpt = GPT()
        self.query_pool = query_pool
        self.hints_pool = hints_pool

    def suggest_and_explain(self, query, hints):
        response = textwrap.dedent(f"""
            <description>
            Input:{query}
            
            <target>        
            Rewrite this query to improve performance. Describe the rewrite rules you are using (you must not include any specific query details in the rules, e.g., table names, column names, etc). Be concise.
            Here are some hints that you might consider when rewriting the query:(And also you can use another rewirte rules based on your thought)
            {hints}
            
            <demand>
            JSON RESULT TEMPLATE:
            {{
                "Candidate rewrite": , // return the candidate rewrite based on rewrite rules the prompt provided or your thought
                "total_number": ,     // return the total number of NLR2s actually applied
                "rewrite_rule_1": ,      // return the rewrite rule 1. Only return the single rewrite rule, do not contain any other information.
                "rewrite_rule_1_explanation": ,      // return the rewrite rule 1 explanation
                "rewrite_rule_2": ,      // return the rewrite rule 2. Only return the single rewrite rule, do not contain any other information.
                "rewrite_rule 2_explanation": ,      // return the rewrite rule 2 explanation
                ........   //if any other rewrite rules applied, return them in the same format
            }}
        """    
        )
        answer = self.gpt.get_GPT_response(response, json_format=True)
        nlr2_number = answer["total_number"]
        candidate_rewrite = []
        explanation = []
        for i in range(nlr2_number):
            rewrite_rule = answer[f"rewrite_rule_{i + 1}"]
            rewrite_rule_explanation = answer[f"rewrite_rule_{i + 1}_explanation"]
            # print(f"rewrite rule: {rewrite_rule}")
            # print(f"rewrite rule explanation: {rewrite_rule_explanation}")
            candidate_rewrite.append(rewrite_rule)
            explanation.append(rewrite_rule_explanation)
        
        return candidate_rewrite, explanation


# query = "SELECT COUNT(DISTINCT 'contacts'.'id') FROM 'contacts' LEFT OUTER JOIN 'people' ON 'people'.'id' = 'contacts'.'person_id' LEFT OUTER JOIN 'profiles' ON 'profiles'.'person_id' = 'people'.'id' WHERE 'contacts'.'user_id' = 1945"

# hints = """
# Pre-calculate aggregates in subqueries
# Remove unnecessary UNION ALL operation
# Avoid using arithmetic operations in WHERE clause
# Replace implicit JOINs with explicit JOINs
# """

# gpt = GPT()
# suggest = suggest_candidate_rewrite(gpt, query, hints)
# candidate_rewrite, explanation = suggest.suggest_and_explain(query, hints)


# print(f"Candidate Rewrite:\n{candidate_rewrite}")
# print(f"Explanation:\n{explanation}")



