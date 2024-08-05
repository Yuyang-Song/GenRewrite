# correct_module/__init__.py
import sys
import os

# Obtain the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Obtain the parent directory
parent_dir = os.path.dirname(current_dir)

# Make the sys path into the parent directory
sys.path.append(parent_dir)