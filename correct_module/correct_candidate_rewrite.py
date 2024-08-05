#########################################
# This module is used to correct the rewritten query to ensure semantic equivalence with the original query.
# running checked successfully
#########################################
# correct_module/__init__.py
import sys
import os
import re

# Obtain the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Obtain the parent directory
parent_dir = os.path.dirname(current_dir)

# Make the sys path into the parent directory
sys.path.append(parent_dir)

from pipeline_module.gpt import GPT


class Nlr2Correction:
    def __init__(self, q1, q2):
        self.q1 = q1
        self.q2 = q2
        self.gpt = GPT()
        
    def extract_modified_version(self,prompt):
        # defination of regular match pattern of sql queries
        sql_pattern = re.compile(
            r"```sql(.*?)```|"
            r"\*\*Modified version:\*\*\s*```sql(.*?)```|"
            r"\*\*Modified version:\*\*\s*(.*?)(?=(\n\*\*|$))",
            re.DOTALL
        )
        # searching for mathch patterns in prompt
        match = sql_pattern.search(prompt)
        
        if match:
            # return the matched SQL queries
            return match.group(1) or match.group(2) or match.group(3)
        else:
            return None
    
    def perform_semantic_correction(self):
        prompt = (
            f"q1:{self.q1} q2:{self.q2}\n"
            f"q1 is the original query, q2 is the rewritten query of q1.\n"
            "For q1, break it down step by step and then describe what it does in one sentence. Do the same for q2.\n"
            "Give an example, using tables, to show that these two queries are not equivalent if there's any such case. Otherwise, just say they are equivalent.\n"
            "please return the answer in the following format:\n"
            "Not equivalent(or equivalent).\n" 
            "{Breakdown and analysis} \n"
            "{A counterexample} \n"
        )
        analysis = self.gpt.get_GPT_response(prompt)
        #### print(analysis)

        # Assume the GPT response includes both q1_analysis and q2_analysis
        if "Not equivalent" in analysis:
            prompt_improve = (
            "Based on your analysis, which part of q2 should be modified so that it becomes equivalent to q1? Show the modified version of q2.\n"
            "please return the answer in the following format and note that do not add any other word after modified version query:\n"
            "{analysis this problem} \n" 
            "{Modified version:} \n"
            
        )
            self.q2 = self.gpt.get_GPT_response_with_history(prompt,prompt_improve,analysis)
            #### print(self.q2)
            self.q2 = self.extract_modified_version(self.q2)
        #     self.q2 = self.gpt.get_GPT_response(prompt)
        #     print(f"correct CoT correction : {self.q2}\n")
        
            print(
                f"Not Equivalent\n"
                f"CoT correction based on semantic correction: {self.q2}"
            )
            return False  # Not equivalent yet
        print(
            f"Equivalent\n"
            f"Origin query: {self.q2}"
        )
        
        return True  # Equivalent

    def perform_syntax_correction(self):
        # Perform syntax correction based on feedback from EXPLAIN command using GPT
        prompt = (
            f"Perform syntax correction for the following SQL query:\n{self.q2}\n Is this query has any syntax error? If it hasn't, return the origin query. If it has, return the corrected query."
            "please return the answer in the following format and note that do not add any other word after sql format query:\n"
            "```sql {return query}```\n" 
        )
        return self.gpt.get_GPT_response(prompt)

    def correct_query(self):
        iterations = 0
        # Perform semantic correction until the queries are equivalent using LLM
        print(
            f"-----------------------------------------------------------------\n"
            f"running semantic correction............\n"
        )
        while not self.perform_semantic_correction():
            iterations += 1
            if iterations > 3:  # Avoid infinite loops
                return None
        self.q2 = self.perform_syntax_correction()
        self.q2 = self.extract_modified_version(self.q2)
        print(
            f"running syntax correction............\n"
            f"CoT correction  based on syntax correction: {self.q2}"
            f"-----------------------------------------------------------------\n"
        )
        return self.q2


# Example debug:
# q1 = "SELECT COUNT(*) FROM 'contacts'INNER JOIN 'aspect_memberships' ON 'contacts'.'id' = 'aspect_memberships'.'contact_id' WHERE 'aspect_memberships'.'aspect_id' = 3;"
# q2 = "SELECT COUNT(*) FROM 'aspect_memberships' AS 'aspect_memberships' WHERE 'aspect_memberships'.'aspect_id' = 3;"
# q3 = "SELECT COUNT(*) FROM 'tag_followings' AS 'tag_followings' WHERE 'tag_followings'.'user_id' = 1"
# correction = Nlr2Correction(q1, q2)
# corrected_query = correction.correct_query()
# print("Corrected Query:", corrected_query)