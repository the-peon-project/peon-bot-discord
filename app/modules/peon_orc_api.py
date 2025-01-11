# IMPORT
import logging
from datetime import datetime
import pytz
import requests
from modules import get_peon_orcs, settings
import re

# Services Get users in a certain group
def get_servers(url, api_key):
    logging.debug('[get_servers]')
    url = f"{url}/api/v1/servers"
    headers = { 'Accept': 'application/json', 'X-Api-Key': api_key }
    return (requests.get(url, headers=headers)).json()

def get_servers_all(peon_orchestrators):
    response=""
    for orchestrator in peon_orchestrators:
        response += f"{orchestrator['name'].upper()}\n```yaml"
        for server in get_servers(orchestrator['url'], orchestrator['key']):
            server_uid = f"{server['game_uid']}.{server['servername']}"
            response += "\n{0:<25} : {1}".format(server_uid,server['container_state'])
        response += "\n```"
    return { "status" : "success", "data" : f"{response}" }

def get_warplans(peon_orchestrators):
    logging.debug('[get_plans]')
    url = f"{peon_orchestrators[0]['url']}/api/v1/plans"
    headers = { 'Accept': 'application/json', 'X-Api-Key': peon_orchestrators[0]['key'] }
    plans = requests.get(url, headers=headers).json()
    response = f"*The currently available warplans for your ochestrators.*\n```yaml"
    response += "\n{0:<15} : {1}\n{2:<15} : {2}".format("game_uid","game","---")
    for plan in plans:
        response += "\n{0:<15} : {1}".format(plan['game_uid'],plan['title'])
    response += "\n```"
    return { "status" : "success", "data" : f"{response}" }

def get_warplan(peon_orchestrators,args):
    logging.debug('[get_plans]')
    if len(args) < 1:
        return { "status" : "error", "err_code" : "plan.param", "command" : "plan"}
    url = f"{peon_orchestrators[0]['url']}/api/v1/plan/{args[0]}"
    headers = { 'Accept': 'application/json', 'X-Api-Key': peon_orchestrators[0]['key'] }
    response = requests.get(url, headers=headers)
    if response.status_code != 200: return { "status" : "error", "err_code" : "plan.dne", "command" : "plan"}
    plan = response.json()
    response += f"*Warplan takes the following settings.*\n```yaml"
    for key, value in plan.items():
        response += "\n{0:<15} : {1}".format(key,value)
    response += "\n```"
    return { "status" : "success", "data" : f"{response}" }

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
    logging.debug(f'[serverAction] - {action}]')
    url = f"{url}/api/v1/server/{action}/{server_uid}"
    headers = { 'Accept': 'application/json', 'X-Api-Key': api_key }
    if action == "get":
        return (requests.get(url, headers=headers)).json()
    return (requests.put(url, headers=headers,json=timer)).json()

def server_actions(action,args):
    if len(args) == 0: return { "status" : "error", "err_code" : "srv.param", "command" : action}
    args_old = list(args)
    args = []
    for arg in args_old:
        args.append(arg.lower())
    # STEP 1: Check that there are some registered orchestrators
    if 'error' in (result := get_peon_orcs())['status']: return { "status" : "error", "err_code" : "orc.none", "command" : action}
    peon_orchestrators = result['data']
    #STEP 2: Get argument information
    arg_datetime = look_for_regex_in_args("^(\d{4})\W(\d{2})\W(\d{2})\.(\d{2})[:h](\d{2})$",args)
    if arg_datetime: args.remove(arg_datetime)
    arg_time = look_for_regex_in_args("^(\d{2})[:h](\d{2})$",args)
    if arg_time: args.remove(arg_time)
    
    arg_interval = look_for_regex_in_args("^\d+.?$",args) # Look for a string of type D..DC (e.g. 5m, 20h, 3d)
    time_unit=""
    if not arg_interval:
        if (arg_interval := look_for_regex_in_args("^\d+$",args)): time_unit = 'm' # If several digits are provided then assume it is a minute count
    if arg_interval: 
        args.remove(arg_interval)
        arg_interval += time_unit
    
    if len(args) < 1: return { "status" : "error", "err_code" : "srv.param", "command" : action}
    # STEP 3: Get list of servers on orchestrators
    ## SCALE ISSUE: If there are lots of Orcs, it could take time (so, if people end up using this, rewrite). Then we need a local DB
    server_list = []
    server = {}
    for orchestrator in peon_orchestrators:
        try:
            servers = get_servers(orchestrator['url'], orchestrator['key'])
            for server in servers:
                server['orchestrator'] = orchestrator['name'].lower()
            server_list.extend(servers)
        except:
            logging.warn(f"Host {orchestrator} is unavailable.")
    if len(server_list) == 0: return { "status" : "error", "err_code" : "orc.notavailable", "command" : action}
    # STEP 4: Try and find server with remaining arg/s
    matched_server_list = []
    for server in server_list:
        arg_servername = look_for_regex_in_args(server['servername'].lower(),args)
        if arg_servername:
            matched_server_list.append(server)
            break
    if len(matched_server_list) == 0: return { "status" : "error", "err_code" : "srv.dne", "command" : action}
    elif len(matched_server_list) > 1:
        server_list = matched_server_list
        matched_server_list = []
        for server in server_list:
            arg_gameuid = look_for_regex_in_args(server['game_uid'].lower(),args)
            if arg_gameuid:
                matched_server_list.append(server)
                break
    if len(matched_server_list) == 0: return { "status" : "error", "err_code" : "srv.dne", "command" : action}
    elif len(matched_server_list) > 1:
        server_list = matched_server_list
        matched_server_list = []
        for server in server_list:
            arg_orchestrator = look_for_regex_in_args(server['orchestrator'].lower(),args)
            if arg_orchestrator:
                matched_server_list.append(server)
                break
    if len(matched_server_list) == 0: return { "status" : "error", "err_code" : "srv.dne", "command" : action}
    elif len(matched_server_list) > 1: return { "status" : "error", "err_code" : "srv.param", "command" : action}
    game_uid = matched_server_list[0]['game_uid']
    servername = matched_server_list[0]['servername']
    serveruid=f"{game_uid}.{servername}"
    
    orchestrator = next((orc for orc in peon_orchestrators if orc['name'] == matched_server_list[0]['orchestrator']), None)
    # STEP 5: Trigger action on server
    data = server_action(orchestrator['url'],orchestrator['key'],serveruid,'get')
    if "error" in data:
        response = { "status" : "error", "err_code" : "srv.action.error", "command" : action}
    else:
        response =f"Orc **{action}** warcamp **{servername}** in {orchestrator['name'].upper()}."
        if action == 'get':
            response += "```yaml\n{0:<15}: {1}\n{2:<15}: {3}\n{4:<15}: {5}\n{6:<15}: {7}\n".format("Warcamp",data["servername"],"Type",data['game_uid'],"Peon State",(data["server_state"].lower()),"Description",data["description"])
            try:
                if data['server_config']:
                    response += "---\n"
                    config_dict = data['server_config']
                    for key,value in config_dict.items():
                        response += "{0:<15}: {1}\n".format(key.title(),value)
            except:
                response += f"---\n{data['server_config']}\n"
            response += "```"
            if data["time"]:
                today = pytz.utc.localize(datetime.today()).astimezone(pytz.timezone(settings["timezone"]))
                stoptime = pytz.utc.localize(datetime.fromtimestamp(int(data["time"]))).astimezone(pytz.timezone(settings["timezone"]))
                response += "\n\t:alarm_clock: Orc will turn off server at ``"
                if str(today.date()) == str(stoptime.date()): response += stoptime.strftime("%X %Z")
                else: response += stoptime.strftime("%X %Z [%x]")
                response += "``"
        else:
            timer = {}
            if arg_time:
                date_string = (datetime.now(pytz.timezone(settings["timezone"])).date().strftime('%Y-%m-%d'))
                timestring = re.match("^(\d{2})[:h](\d{2})$",arg_time)
                timestring = f"{date_string} {timestring[1]}:{timestring[2]}:00"
                time_tz = pytz.timezone(settings["timezone"]).localize(datetime.strptime(timestring, '%Y-%m-%d %H:%M:%S'))
                epoch = int(time_tz.timestamp())
                if epoch <= int(datetime.now(pytz.timezone(settings["timezone"])).timestamp()):
                    return { "status" : "error", "err_code" : "schedule.past", "command" : action}
                timer = {"epoch_time" : f"{epoch}"}
                response += f"\n\n\t:alarm_clock: Warcamp will shut down at ``{timestring}``."
            elif arg_datetime:
                timestring = re.match("^(\d{4})\W(\d{2})\W(\d{2})\.(\d{2})[:h](\d{2})$",arg_datetime)
                timestring = (f"{timestring[1]}-{timestring[2]}-{timestring[3]} {timestring[4]}:{timestring[5]}:00")
                time_tz = pytz.timezone(settings["timezone"]).localize(datetime.strptime(timestring, '%Y-%m-%d %H:%M:%S'))
                epoch = int(time_tz.timestamp())
                if epoch <= int(datetime.now(pytz.timezone(settings["timezone"])).timestamp()):
                    return { "status" : "error", "err_code" : "schedule.past", "command" : action}
                timer = {"epoch_time" : f"{epoch}"}
                response += f"\n\n\t:alarm_clock: Warcamp will shut down at ``{timestring}``."
            elif arg_interval:
                timer = { "interval" : f"{arg_interval}" }
                response += f"\n\n\t:alarm_clock: Warcamp will shut down in ``{arg_interval}``."
            server_action(orchestrator['url'], orchestrator['key'], serveruid, action, timer)
        return { "status" : "success", "data" : f"{response}" }
