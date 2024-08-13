import sys
import os
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
import random
from pipeline_module.gpt import GPT
from correct_module.correct_candidate_rewrite import Nlr2Correction
from evaluate_module.evaluate_rewrite import Evaluate_rewrite_model
from suggest_module.suggest_candidate_rewrite import suggest_candidate_rewrite
from suggest_module.suggest_group_rewrite import sugget_group_rewrite
from suggest_module.suggest_select_rewrite import suggest_select_rewrite

class GenRewrite:
    def __init__(self, queries, budget, min_speedup,reportory_path):
        self.queries = queries
        self.gpt = GPT()
        # self.tester = tester # what is tester ?? to be reconsidered.
        self.budget = budget
        self.min_speedup = min_speedup
        self.json_path = reportory_path
        self.res = []
        self.rewrite_rules = []

    # done
    def suggest_and_explain(self, query,hints):
        # Placeholder for suggesting and explaining rewrites using LLM and rewrite rules
        suggest = suggest_candidate_rewrite(self.gpt, query, hints)
        candidate_rewrite, explanation = suggest.suggest_and_explain(query, hints)
        return candidate_rewrite, explanation

    # done
    def suggest_group_rewrite(self,rewrite_rule, query, k = 3):
        # Placeholder for suggesting group rewrites
        group_model = sugget_group_rewrite(self.json_path,k)
        group_model.add_rule_in_group(rewrite_rule,query)

    # done
    def suggest_select_rewrite(self, input_query):
        # Placeholder for suggesting select rewrites
        selector = suggest_select_rewrite(self.json_path)
        best_nlr2s = selector.select_best_nlr2(input_query)[::-1] 
        return best_nlr2s
        

    # done
    def correct_for_equivalence(self, original_query, rewritten_query):
        # Placeholder for correcting the rewrite to ensure semantic equivalence
        correction = Nlr2Correction(original_query, rewritten_query)
        corrected_query = correction.correct_query()
        return corrected_query

    # done 
    def evaluate_rewrite(self, original_query, rewritten_query):
        # Placeholder for evaluating the rewrite
        evalute_model = Evaluate_rewrite_model(self.json_path)
        is_equiv = evalute_model.check_if_equiv(original_query, rewritten_query)
        speedup = evalute_model.evalutate(original_query, rewritten_query)
        return is_equiv, speedup
    
    def update_rules(self, explanation, speedup):
        # Placeholder for updating rewrite rules based on explanations and speedups
        self.rewrite_rules.append((explanation, speedup))



    def run(self,hints):
        while self.queries:
            for query in self.queries:
                rewritten_query, explanation = self.suggest_and_explain(query,hints)
                corrected_query = self.correct_for_equivalence(query, rewritten_query)
                is_equiv, speedup = self.evaluate_rewrite(query,query,corrected_query)

                if is_equiv:
                    self.update_rules(explanation, speedup)
                    if speedup > self.min_speedup:
                        self.res.append((query, corrected_query, explanation,speedup))

            # Check termination condition
            if not self.queries: # len(self.res) >= self.budget:
                return self.res

            # Remove optimized queries from the original set
            self.queries = [q for q in self.queries if q not in [r[0] for r in self.res]]

        return self.res

