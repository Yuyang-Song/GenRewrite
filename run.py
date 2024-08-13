import time
import os
import sys
from pipeline_module.gpt import GPT
from pipeline_module.pipeline import GenRewrite
import logging


if __name__ == "__main__":
    print(
        f"-----------------------------------------------------------------\n"
        f"Start initializing configuration...\n"        
    )
    try:
        gpt = GPT()
        print("GPT connection test ...\n  Prompt: What is the capital of France?")
        prompt = "What is the capital of France?"
        response = gpt.get_GPT_response(prompt)
        print(f"  {response}\n")
        print("GPT connection sucessfully!")
        
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
    print(
        f"-----------------------------------------------------------------\n"      
    )
    
    hints = """
    Pre-calculate aggregates in subqueries
    Remove unnecessary UNION ALL operation
    Avoid using arithmetic operations in WHERE clause
    Replace implicit JOINs with explicit JOINs
    """
    json_path = "./data/reportory.json"
    # def __init__(self, queries, budget, min_speedup,reportory_path):
    candidate_queries = ["SELECT * FROM table WHERE column = value"]
    pipline = GenRewrite(queries = candidate_queries, budget = 10, min_speedup = 0.2, reportory_path = json_path)
    res = pipline.run(hints)
    
    print(
        f"-----------------------------------------------------------------\n"
        f"End of the program.\n"
        f"-----------------------------------------------------------------\n"
    )
    print(f"Result: {res}")
    