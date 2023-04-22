import json
import random
from . import project_path

responses = json.load(open(f"{project_path}/config/documents/quotes.json"))
messages = json.load(open(f"{project_path}/config/documents/messages.json"))

def quote(group="hello"):
    return random.choice(responses[group])

def error_message(type="undefined",command="undefined"): # Add error header
    error_string = f"*\'{quote('nok')}\'*\n"
    error_string += f"*{messages['type'][type]}*\n" # Add error type
    error_string += f"```yaml\n{messages['sample'][command]}\n```" # Add help sample Add help sample
    return error_string