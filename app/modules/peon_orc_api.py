# IMPORT
import logging
import requests
from modules import getPeonOrchestrators
from modules.messaging import *


def getServersAll(peon_orchestrators):
    response = f"*\'{quote('hello')}\'*\n"
    for orchestrator in peon_orchestrators:
        response += f"**{orchestrator['name']}**\n```yaml"
        for server in getServers(orchestrator['url'], orchestrator['key'])["servers"]:
            response += f"\n{server['game_uid']}.{server['servername']} : [{server['container_state']}]"
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
        response=f"*\'{quote('ok')}\'*\n"
        apiresponse = serverAction(orchestrator['url'],orchestrator['key'],args[1],'get')
        if "error" in apiresponse:
            response = errorMessage('srv.dne', 'get')
        else:
            if action != 'get':
                apiresponse = serverAction(orchestrator['url'],orchestrator['key'],args[1],action)
            response += f"**{args[0]} {args[1]}**\n"
            data = apiresponse['server']
            response += f"```yaml\nGameUID        : {data['game_uid']}\nServerName     : {data['servername']}\nContainerState : {data['container_state']}\nServerState    : {data['server_state']}\nDescription    : {data['description']}\n```"
    return response

######## MAIN - FOR TEST PURPOSES

if __name__ == "__main__":
    print(getServers("http://dockerdev.za.cloudlet.cloud:5000","my-super-secret-api-key"))
