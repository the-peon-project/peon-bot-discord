# IMPORT
import logging
import requests
from modules import getPeonOrchestrators
from modules.messaging import *


def getServersAll(peon_orchestrators):
    response = f"*\'{quote('hello')}\'*\n"
    for orchestrator in peon_orchestrators:
        response += f"{orchestrator['name']}\n```yaml"
        for server in getServers(orchestrator['url'], orchestrator['key'])["servers"]:
            server_uid = f"{server['game_uid']}.{server['servername']}"
            response += "\n{0:<25} : {1}".format(server_uid,server['container_state'])
        response += "\n```"
    return response

# Services Get users in a certain group
def getServers(url, api_key):
    logging.debug('[getAllServers]')
    url = f"{url}/api/1.0/servers"
    headers = { 'Accept': 'application/json', 'X-Api-Key': api_key }
    return (requests.get(url, headers=headers)).json()

def serverAction(url, api_key, server_uid, action):
    logging.debug(f'[serverAction - {action}]')
    url = f"{url}/api/1.0/server/{action}/{server_uid}"
    headers = { 'Accept': 'application/json', 'X-Api-Key': api_key }
    if action == "get":
        return (requests.get(url, headers=headers)).json()
    return (requests.put(url, headers=headers)).json()

def serverActions(action,args):
    peon_orchestrators = getPeonOrchestrators()
    if len(args) != 2:
        response = errorMessage('parameterCount',action)
    elif peon_orchestrators == "EMPTY":
        response = errorMessage('none','register')
    elif not ([orchestrator for orchestrator in peon_orchestrators if args[0] == orchestrator['name']]):
        response = errorMessage('orc.dne', action)
    else:
        orchestrator = ([orchestrator for orchestrator in peon_orchestrators if args[0] == orchestrator['name']])[0]
        apiresponse = serverAction(orchestrator['url'],orchestrator['key'],args[1],'get')
        if "error" in apiresponse:
            response = errorMessage('srv.dne', 'get')
        else:
            response =f"*{quote('ok')}\nOrc ``{action.upper()}`` warcamp ``{args[1]}`` in ``{args[0]}``.*"
            if action == 'get':
                data = apiresponse['server']
                response += "```yaml\n{0:<25} : {1}\n{2:<25} : {3}\n{4:<25} : {5}\n---\n".format("Game ID",data['game_uid'],"Warcamp Name",data["servername"],"State",data["server_state"].lower())
                try:
                    config_dict = json.loads(data['server_config'])
                    for key,value in config_dict.items():
                        response += "{0:<25} : {1}\n".format(key,value)
                    response += "```"
                except:
                    response += f"{data['server_config']}\n```"
            else:
                serverAction(orchestrator['url'],orchestrator['key'],args[1],action)
    return response

######## MAIN - FOR TEST PURPOSES

if __name__ == "__main__":
    print(getServers("http://dockerdev.za.cloudlet.cloud:5000","my-super-secret-api-key"))
