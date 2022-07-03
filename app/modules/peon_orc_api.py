# IMPORT
from datetime import datetime
import pytz
import logging
import requests
from modules import getPeonOrchestrators, settings
from modules.messaging import *
import re


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
    logging.debug('[getServers]')
    url = f"{url}/api/1.0/servers"
    headers = { 'Accept': 'application/json', 'X-Api-Key': api_key }
    return (requests.get(url, headers=headers)).json()

def lookForRegexInArgs(regex,args):
    try:
        for argument in args:
            match = re.search(regex, argument)
            if match:
                logging.debug(f"{match[0]}")
                return match[0]
    except:
        return None

def serverAction(url, api_key, server_uid, action):
    logging.debug(f'[serverAction - {action}]')
    url = f"{url}/api/1.0/server/{action}/{server_uid}"
    headers = { 'Accept': 'application/json', 'X-Api-Key': api_key }
    if action == "get":
        return (requests.get(url, headers=headers)).json()
    return (requests.put(url, headers=headers)).json()

def serverActions(action,args):
    if len(args) == 0: return errorMessage('parameterCount',action)
    # STEP 1: Check that there are some registered orchestrators
    peon_orchestrators = getPeonOrchestrators()
    if peon_orchestrators == "EMPTY": return errorMessage('orc.none',action)
    #STEP 2: Get argument informarion
    arg_datetime = lookForRegexInArgs("^(\d{4})\W(\d{2})\W(\d{2})\.(\d{2})[:h](\d{2})$",args)
    if arg_datetime: args.remove(arg_datetime)
    arg_time = lookForRegexInArgs("^(\d{4})\W(\d{2})\W(\d{2})\.(\d{2})[:h](\d{2})$",args)
    if arg_time: args.remove(arg_time)
    arg_interval = lookForRegexInArgs("^\d+\D$",args)
    if arg_interval: args.remove(arg_interval)
    if len(args) < 1: return errorMessage('parameterCount',action)
    # STEP 3: Get list of servers on orchestrators
    ## SCALE ISSUE: If there are lots of Orcs, it could take time (so, if people end up using this, rewrite). Then we need a local DB
    server_list = []
    server = {}
    for orchestrator in peon_orchestrators:
        try:
            servers = getServers(orchestrator['url'], orchestrator['key'])['servers']
            for server in servers:
                server['orchestrator'] = orchestrator['name']
            server_list.extend(servers)
        except:
            logging.warn(f"Host {orchestrator} is unavailable.")
    if len(server_list) == 0: return errorMessage('orc.notavailable',action)
    # STEP 4: Try and find server with remaining arg/s
    matched_server_list = []
    for server in server_list:
        arg_servername = lookForRegexInArgs(server['servername'],args)
        if arg_servername:
            matched_server_list.append(server)
            break
    if len(matched_server_list) == 0: return errorMessage('srv.dne',action)
    elif len(matched_server_list) > 1:
        server_list = matched_server_list
        matched_server_list = []
        for server in server_list:
            arg_gameuid = lookForRegexInArgs(server['game_uid'],args)
            if arg_gameuid:
                matched_server_list.append(server)
                break
    if len(matched_server_list) == 0: return errorMessage('srv.dne',action)
    elif len(matched_server_list) > 1:
        server_list = matched_server_list
        matched_server_list = []
        for server in server_list:
            arg_orchestrator = lookForRegexInArgs(server['orchestrator'],args)
            if arg_orchestrator:
                matched_server_list.append(server)
                break
    if len(matched_server_list) == 0: return errorMessage('srv.dne',action)
    elif len(matched_server_list) > 1: return errorMessage('parameterCount',action)
    # STEP 5: Trigger action on server
    serveruid=f"{arg_gameuid}.{arg_servername}"
    apiresponse = serverAction(arg_orchestrator['url'],arg_orchestrator['key'],serveruid,'get')
    if "error" in apiresponse:
        response = errorMessage('srv.action.error','get')
    else:
        response =f"*{quote('ok')}\nOrc ``{action.upper()}`` warcamp ``{serveruid}`` in ``{arg_orchestrator}``.*"
        if action == 'get':
            data = apiresponse['server']
            response += "```yaml\n{0:<25} : {1}\n{2:<25} : {3}\n{4:<25} : {5}\n".format("Game ID",data['game_uid'],"Warcamp Name",data["servername"],"State",data["server_state"].lower())
            if data["time"] != None:
                today = pytz.utc.localize(datetime.today()).astimezone(pytz.timezone(settings["timezone"]))
                stoptime = pytz.utc.localize(datetime.fromtimestamp(int(data["time"]))).astimezone(pytz.timezone(settings["timezone"]))
                if str(today.date()) == str(stoptime.date()):
                    response += "{0:<25} : {1}\n".format("Server Shutdown",stoptime.strftime("%X %Z"))
                else:
                    response += "{0:<25} : {1}\n".format("Server Shutdown",stoptime.strftime("%X %Z [%x]"))
            response += "---\n"
            try:
                config_dict = json.loads(data['server_config'])
                for key,value in config_dict.items():
                    response += "{0:<25} : {1}\n".format(key,value)
                response += "```"
            except:
                response += f"{data['server_config']}\n```"
        else:
            serverAction(orchestrator['url'],orchestrator['key'],serveruid,action)
        return response
    

######## MAIN - FOR TEST PURPOSES

if __name__ == "__main__":
    print(getServers("http://dockerdev.za.cloudlet.cloud:5000","my-super-secret-api-key"))
