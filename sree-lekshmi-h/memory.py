import json
from textwrap import indent
MEMORY_FILE='memory.json'

def load_memory():
    with open(MEMORY_FILE,'r') as f:
        return json.load(f)
    
def save_memory(memory):
    with open(MEMORY_FILE,'w') as f:
        json.dump(memory,f,indent=4)
        

