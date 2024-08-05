from configparser import ConfigParser
import time
import os
import sys
from pipeline_module.gpt import GPT
from pipeline_module.pipeline import GenRewrite
import logging


if __name__ == "__main__":
    # initialization part

    # print("Start initializing configuration...")
    # logging.basicConfig(filename='error.log', level=logging.ERROR)
    # config = ConfigParser()
    # config.read("./config_file/config.ini")
    print(
        f"-----------------------------------------------------------------\n"
        f"Start initializing configuration...\n"        
    )
    try:
        # budget = int(config.get("parameters", "budget"))
        # min_speedup = float(config.get("parameters", "min_speedup"))
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
    
    
    
    
    # gen_rewrite = GenRewrite(queries, gpt, budget, min_speedup)
    # optimized_queries = gen_rewrite.run()
    # print("Optimized Queries:", optimized_queries)

