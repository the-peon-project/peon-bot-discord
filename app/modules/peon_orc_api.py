# IMPORT
from datetime import datetime
import pytz
import logging
import requests
from modules import getPeonOrchestrators, settings
from modules.messaging import *
import re

def get_servers_all(peon_orchestrators):
    response = f"*\'{quote('hello')}\'*\n"
    for orchestrator in peon_orchestrators:
        response += f"{orchestrator['name'].upper()}\n```yaml"
        for server in get_servers(orchestrator['url'], orchestrator['key'])["servers"]:
            server_uid = f"{server['game_uid']}.{server['servername']}"
            response += "\n{0:<25} : {1}".format(server_uid,server['container_state'])
        response += "\n```"
    return response

# Services Get users in a certain group
def get_servers(url, api_key):
    logging.debug('[getServers]')
    url = f"{url}/api/1.0/servers"
    headers = { 'Accept': 'application/json', 'X-Api-Key': api_key }
    return (requests.get(url, headers=headers)).json()

def look_for_regex_in_args(regex,args):
    try:
        for argument in args:
            match = re.search(regex, argument)
            if match:
                logging.debug(f"{match[0]}")
                return match[0]
    except:
        return None

def server_action(url, api_key, server_uid, action, timer={}):
    logging.debug(f'[serverAction - {action}]')
    url = f"{url}/api/1.0/server/{action}/{server_uid}"
    headers = { 'Accept': 'application/json', 'X-Api-Key': api_key }
    if action == "get":
        return (requests.get(url, headers=headers)).json()
    return (requests.put(url, headers=headers,json=timer)).json()

def server_actions(action,args):
    if len(args) == 0: return errorMessage('parameterCount',action)
    args_old = list(args)
    args = []
    for arg in args_old:
        args.append(arg.lower())
    # STEP 1: Check that there are some registered orchestrators
    peon_orchestrators = getPeonOrchestrators()
    if peon_orchestrators == "EMPTY": return errorMessage('orc.none',action)
    #STEP 2: Get argument informarion
    arg_datetime = look_for_regex_in_args("^(\d{4})\W(\d{2})\W(\d{2})\.(\d{2})[:h](\d{2})$",args)
    if arg_datetime: args.remove(arg_datetime)
    arg_time = look_for_regex_in_args("^(\d{2})[:h](\d{2})$",args)
    if arg_time: args.remove(arg_time)
    arg_interval = look_for_regex_in_args("^\d+\D$",args)
    if arg_interval: args.remove(arg_interval)
    if len(args) < 1: return errorMessage('parameterCount',action)
    # STEP 3: Get list of servers on orchestrators
    ## SCALE ISSUE: If there are lots of Orcs, it could take time (so, if people end up using this, rewrite). Then we need a local DB
    server_list = []
    server = {}
    for orchestrator in peon_orchestrators:
        try:
            servers = get_servers(orchestrator['url'], orchestrator['key'])['servers']
            for server in servers:
                server['orchestrator'] = orchestrator['name'].lower()
            server_list.extend(servers)
        except:
            logging.warn(f"Host {orchestrator} is unavailable.")
    if len(server_list) == 0: return errorMessage('orc.notavailable',action)
    # STEP 4: Try and find server with remaining arg/s
    matched_server_list = []
    for server in server_list:
        arg_servername = look_for_regex_in_args(server['servername'].lower(),args)
        if arg_servername:
            matched_server_list.append(server)
            break
    if len(matched_server_list) == 0: return errorMessage('srv.dne',action)
    elif len(matched_server_list) > 1:
        server_list = matched_server_list
        matched_server_list = []
        for server in server_list:
            arg_gameuid = look_for_regex_in_args(server['game_uid'].lower(),args)
            if arg_gameuid:
                matched_server_list.append(server)
                break
    if len(matched_server_list) == 0: return errorMessage('srv.dne',action)
    elif len(matched_server_list) > 1:
        server_list = matched_server_list
        matched_server_list = []
        for server in server_list:
            arg_orchestrator = look_for_regex_in_args(server['orchestrator'].lower(),args)
            if arg_orchestrator:
                matched_server_list.append(server)
                break
    if len(matched_server_list) == 0: return errorMessage('srv.dne',action)
    elif len(matched_server_list) > 1: return errorMessage('parameterCount',action)
    game_uid = matched_server_list[0]['game_uid']
    servername = matched_server_list[0]['servername']
    serveruid=f"{game_uid}.{servername}"
    orchestrator = next((orc for orc in peon_orchestrators if orc['name'] == matched_server_list[0]['orchestrator']), None)
    # STEP 5: Trigger action on server
    apiresponse = server_action(orchestrator['url'],orchestrator['key'],serveruid,'get')
    if "error" in apiresponse:
        response = errorMessage('srv.action.error','get')
    else:
        response =f"*{quote('ok')}\nOrc {action} ({game_uid}) warcamp ``{servername}`` in {orchestrator['name'].upper()}."
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
            timer = {}
            if arg_time:
                date_string = (datetime.now(pytz.timezone(settings["timezone"])).date().strftime('%Y-%m-%d'))
                timestring = re.match("^(\d{2})[:h](\d{2})$",arg_time)
                timestring = f"{date_string} {timestring[1]}:{timestring[2]}:00"
                time_tz = pytz.timezone(settings["timezone"]).localize(datetime.strptime(timestring, '%Y-%m-%d %H:%M:%S'))
                epoch = int(time_tz.timestamp())
                if epoch <= int(datetime.now(pytz.timezone(settings["timezone"])).timestamp()):
                    return errorMessage('schedule.past',action)
                timer = {"epoch_time" : f"{epoch}"}
                response += f"\n\tWarcamp will shut down at {timestring}.*"
            elif arg_datetime:
                timestring = re.match("^(\d{4})\W(\d{2})\W(\d{2})\.(\d{2})[:h](\d{2})$",arg_datetime)
                timestring = (f"{timestring[1]}-{timestring[2]}-{timestring[3]} {timestring[4]}:{timestring[5]}:00")
                time_tz = pytz.timezone(settings["timezone"]).localize(datetime.strptime(timestring, '%Y-%m-%d %H:%M:%S'))
                epoch = int(time_tz.timestamp())
                if epoch <= int(datetime.now(pytz.timezone(settings["timezone"])).timestamp()):
                    return errorMessage('schedule.past',action)
                timer = {"epoch_time" : f"{epoch}"}
                response += f"\n\tWarcamp will shut down at {timestring}.*"
            elif arg_interval:
                timer = { "interval" : f"{arg_interval}" }
                response += f"\n\tWarcamp will shut down in {arg_interval}.*"
            server_action(orchestrator['url'], orchestrator['key'], serveruid, action, timer)
        return response
    

######## MAIN - FOR TEST PURPOSES

if __name__ == "__main__":
    print(get_servers("http://dockerdev.za.cloudlet.cloud:5000","my-super-secret-api-key"))
