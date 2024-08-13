#########################################
# This module is used to correct the rewritten query to ensure semantic equivalence with the original query.
# running checked successfully
#########################################
# correct_module/__init__.py
import sys
import os
import re
import textwrap
import json
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
    
    def perform_semantic_correction(self):
        prompt = textwrap.dedent(
        f"""
            <description>
            q1:{self.q1} q2:{self.q2}
            q1 is the original query, q2 is the rewritten query of q1.
            
            <target>
            For q1, break it down step by step and then describe what it does in one sentence. Do the same for q2.
            Give an example, using tables, to show that these two queries are not equivalent if there's any such case. Otherwise, just say they are equivalent.
            
            <demant>
            JSON RESULT TEMPLATE:
            {{
                "Equivalence": , // answer Equivalent or Not Equivalent
                "Break down and analysis": ,      // show wheather the two queries are equivalent or not
                "Counterexample":        // if the two queries are not equivalent, show the counterexample, else show "null"
            }}
        """
        )
        
        analysis = self.gpt.get_GPT_response(prompt,json_format = True)
        # analysis_dict = json.loads(analysis)
        flag = analysis["Equivalence"]
        # print(flag)
        # eturn analysis
        #### print(analysis)
        # # Assume the GPT response includes both q1_analysis and q2_analysis
        
        if flag == "Not Equivalent":
            print("Not Equivalent")
            
            prompt_improve = textwrap.dedent(f"""
                <target>
                Based on your analysis, which part of q2 should be modified so that it becomes equivalent to q1? Show the modified version of q2.
                
                <demand>
                JSON RESULT TEMPLATE:
                {{
                "Analysis": , // step by step analysis
                "Modified version": ,      // show the modified version of q2
                }}
        """    
        )
            cot_analysis = self.gpt.get_GPT_response_with_history(prompt,prompt_improve,analysis)
            self.q2 = cot_analysis["Modified version"]
            print(
                f"CoT correction based on semantic correction: {self.q2}\n"
            )
            return False  # Not equivalent yet
        else:
            print(
                f"Equivalent"
                f"Origin query: {self.q2}\n"
            )
            
            return True  # Equivalent

    def perform_syntax_correction(self):
        # Perform syntax correction based on feedback from EXPLAIN command using GPT
        prompt = textwrap.dedent(f"""
            <target>                    
            Perform syntax correction for the following SQL query:\n{self.q2}\n Is this query has any syntax error? If it hasn't, return the origin query. If it has, return the corrected query.
            
            <demand>
            JSON RESULT TEMPLATE:
            {{
                "Analysis": , // brief analysis
                "return query": ,      // return the non error query
            }}
        """
        )
        return self.gpt.get_GPT_response(prompt,json_format = True)

    def correct_query(self):
        iterations = 0
        # Perform semantic correction until the queries are equivalent using LLM
        print(
            f"-----------------------------------------------------------------\n"
            f"running semantic correction............\n"
        )
        while not self.perform_semantic_correction():
            iterations += 1
            if iterations > 4:  # Avoid infinite loops
                return None
            
        print("running syntax correction............\n")
        correct_answer = self.perform_syntax_correction()
        self.q2 = correct_answer["return query"]
        print(
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