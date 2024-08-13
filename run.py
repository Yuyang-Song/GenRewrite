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