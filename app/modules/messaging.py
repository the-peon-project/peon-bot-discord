import json
import random

responses = json.load(open("/root/peon-bot-discord/app/documents/quotes.json"))
messages = json.load(open("/root/peon-bot-discord/app/documents/messages.json"))

def quote(group="hello"):
    return random.choice(responses[group])

def errorMessage(type="undefined",command="undefined"): # Add error header
    errorString = f"*\'{quote('nok')}\'*\n"
    errorString += f"*{messages['type'][type]}*\n" # Add error type
    errorString += f"```c\n{messages['sample'][command]}\n```" # Add help sample
    return errorString