# IMPORT
import logging
from datetime import datetime
import pytz
import requests
import re
import json
import os
from . import *

# Load orchestrators from disk
def get_peon_orcs():
    try:
        config_file = "/app/config/peon.orchestrators.json"
        logging.debug("Loading orchestrators file")
        with open(config_file, 'r') as file:
            orchestrators = json.load(file)
        API_KEY = os.environ.get('LOCAL_API_KEY',None)
        if API_KEY:
            for entry in orchestrators:
                if entry["url"] == "http://peon.orc:5000":
                    if entry["key"] != API_KEY:
                        logging.debug("Updating orchestrator API key")
                        entry["key"] = f"'{API_KEY}'"
                        with open(config_file, 'w') as file:
                            json.dump(orchestrators, file, indent=4)
                        entry["key"] = API_KEY
                break
        return {"status": "success", "data": orchestrators}
    except FileNotFoundError:
        logging.debug("No orchestrators file found. Creating one.")
        default_data = []
        with open(config_file, 'w') as file:
            json.dump(default_data, file, indent=4)
        return {"status": "error", "info": "Orchestrators file not found. Created a new one."}
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"status": "error", "info": str(e)}

def register_peon_orc(orc_name, orc_url, orc_key):
    try:
        orchestrators = get_peon_orcs()
        if orchestrators["status"] == "error":
            return orchestrators
        orchestrators = orchestrators["data"]
        for entry in orchestrators:
            if entry["name"] == orc_name:
                return {"status": "error", "info": "Orchestrator already registered."}
        if (orc_responose := get_orchestrator_details(orc_url, orc_key))['status'] != "success": return {"status": "error", "info": "Orchestrator not available."}
        orchestrators.append({"name": orc_name, "url": orc_url, "key": orc_key})
        config_file = "/app/config/peon.orchestrators.json"
        with open(config_file, 'w') as file:
            json.dump(orchestrators, file, indent=4)
        return {"status": "success", "info": orc_responose['data']}
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"status": "error", "info": str(e)}

def get_orchestrator_details(url, api_key):
    url = f"{url}/api/v1/orchestrator"
    headers = { 'Accept': 'application/json', 'X-Api-Key': api_key }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return { "status" : "success", "data" : response.json() }
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching orchestrator details: {e}")
        return {"status": "error", "message": str(e)}

# Services Get users in a certain group
def get_servers(url, api_key):
    url = f"{url}/api/v1/servers"
    headers = { 'Accept': 'application/json', 'X-Api-Key': api_key }
    return (requests.get(url, headers=headers)).json()

def get_servers_all(peon_orchestrators):
    response=""
    for orchestrator in peon_orchestrators:
        response += f"The warcamp/s on {orchestrator['name'].upper()} are in the current state/s\n```yaml"
        for server in get_servers(orchestrator['url'], orchestrator['key']):
            server_uid = f"{server['game_uid']}.{server['servername']}"
            response += "\n{0:<25} : {1}".format(server_uid,server['container_state'])
        response += "\n```"
    return { "status" : "success", "data" : f"{response}" }

def import_warcamps(peon_orchestrators):
    logging.debug('Requesting import of unmanaged warcamps')
    warcamps={}
    for orchestrator in peon_orchestrators:
        url = f"{orchestrator['url']}/api/v1/servers"
        headers = { 'Accept': 'application/json', 'X-Api-Key': orchestrator['key'] }  
        response = requests.put(url, headers=headers)
        if response.status_code != 200:
            warcamps[orchestrator['name']] = {}
        else:
            warcamps[orchestrator['name']] = response.json()
    if not warcamps: return { "status" : "error", "err_code" : "orc.notavailable", "command" : "import"}
    reponse_warcamps = {}
    for orc, servers in warcamps.items():
        response_string = f"Orc {orc.upper()} now has the following warcamps.\n```yaml"
        for server in servers:
            response_string += "\n{0:<15} : {1}".format(server['game_uid'],server['servername'])
        response_string += "\n```"
        reponse_warcamps[orc] = response_string
    return { "status" : "success", "data" : reponse_warcamps }

def refresh_warplans(peon_orchestrators):
    logging.debug('Requesting an update to plans catalogue')
    url = f"{peon_orchestrators[0]['url']}/api/v1/plans"
    headers = { 'Accept': 'application/json', 'X-Api-Key': peon_orchestrators[0]['key'] }
    response = requests.put(url, headers=headers)
    if response.status_code != 200:
        return { "status" : "error", "err_code" : "plan.update", "command" : "refresh"}
    else:
        return { "status" : "success"}
    
def get_warplans(peon_orchestrators):
    logging.debug('Requesting list of current plans')
    url = f"{peon_orchestrators[0]['url']}/api/v1/plans"
    headers = { 'Accept': 'application/json', 'X-Api-Key': peon_orchestrators[0]['key'] }
    plans = requests.get(url, headers=headers).json()
    response = f"*The currently available warplans for your ochestrators.*\n```yaml"
    response += "\n{0:<15} : {1}\n{2:<15} : {2}".format("game_uid","game","---")
    for plan in plans:
        response += "\n{0:<15} : {1}".format(plan['game_uid'],plan['title'])
    response += "\n```"
    return { "status" : "success", "data" : f"{response}" }

def get_warplan(peon_orchestrators,game_uid):
    logging.debug('Requesting details for the warplan related to {game_uid}')
    url = f"{peon_orchestrators[0]['url']}/api/v1/plan/{game_uid}"
    headers = { 'Accept': 'application/json', 'X-Api-Key': peon_orchestrators[0]['key'] }
    plan = requests.get(url, headers=headers)
    if (plan := requests.get(url, headers=headers)).status_code != 200: 
        return { "status" : "error", "err_code" : "plan.dne", "command" : "plan"}
    response = f"*Warplan takes the following settings.*\n```json"
    for key, value in plan.json().items():
        response += "\n{0:<15} : {1}".format(key,value)
    response += "\n```"
    return { "status" : "success", "data" : f"{response}" }

def server_backup(url, api_key, server_uid):
    logging.debug(f'[serverBackup] - {server_uid}]')
    url = f"{url}/api/v1/server/save/{server_uid}"
    headers = { 'Accept': 'application/json', 'X-Api-Key': api_key }
    return (requests.put(url, headers=headers)).json()

def server_action(url, api_key, server_uid, action, body={}):
    logging.debug(f'[server_action] - {action} requested for {server_uid}: body {body}')
    url = f"{url}/api/v1/server/{action}/{server_uid}"
    headers = { 'Accept': 'application/json', 'X-Api-Key': api_key }
    if action == "get":
        return (requests.get(url, headers=headers)).json()
    return (requests.put(url, headers=headers,json=body)).json()

def server_actions(action,args):
    logging.debug(f"Server action requested: {action}")
    logging.debug("STEP 1 - Check for active orchestrators")
    if len(args) == 0: return { "status" : "error", "err_code" : "srv.param", "command" : action}
    # STEP 1: Check that there are some registered orchestrators
    if 'error' in (result := get_peon_orcs())['status']: return { "status" : "error", "err_code" : "orc.none", "command" : action}
    peon_orchestrators = result['data']
    if action != 'get':
        #STEP 2: Get argument information
        logging.debug("STEP 2 - Check for arguments")
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
        arg_update_mode = look_for_regex_in_args("^(server|image|full)$", args)
        if arg_update_mode:
            args.remove(arg_update_mode)
        if len(args) < 1: return { "status" : "error", "err_code" : "srv.param", "command" : action}
    else: logging.debug("No arguments required for 'get' action. Skipping to STEP 3.")
    # STEP 3: Get list of servers on orchestrators
    logging.debug("STEP 3 - Collect all servers on all orchestrators")
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
            logging.warning(f"Host {orchestrator} is unavailable.")
    if len(server_list) == 0: return { "status" : "error", "err_code" : "orc.notavailable", "command" : action}
    # STEP 4: Try and find server with remaining arg/s
    logging.debug("STEP 4 - Filter by 'servername'")
    servers_matching_servername = []
    for server in server_list:
        arg_servername = look_for_regex_in_args(server['servername'].lower(),args)
        if arg_servername:
            servers_matching_servername.append(server)
    server_list = servers_matching_servername
    if len(server_list) == 0: 
        logging.error('Server not found')
        return { "status" : "error", "err_code" : "srv.dne", "command" : action}
    elif len(server_list) > 1:
        logging.debug("STEP 5 - Filter by 'game_uid'")
        servers_matching_gameuid = []
        for server in server_list:
            arg_gameuid = look_for_regex_in_args(server['game_uid'].lower(),args)
            if arg_gameuid:
                servers_matching_gameuid.append(server)
        server_list = servers_matching_gameuid
        logging.debug("STEP 6 - Filter by Orchestrator")
        if len(server_list) == 0: return { "status" : "error", "err_code" : "srv.dne", "command" : action}
        elif len(server_list) > 1:
            matched_orchestrator_list = []
            for server in server_list:
                arg_orchestrator = look_for_regex_in_args(server['orchestrator'].lower(),args)
                if arg_orchestrator:
                    matched_orchestrator_list.append(server)
                    break
            server_list = matched_orchestrator_list
            if len(server_list) > 1: return { "status" : "error", "err_code" : "srv.notexplicit", "command" : action}
            else:
                logging.debug("Server found, skipping to STEP 7")
    else:
        logging.debug("Server found, skipping to STEP 7")
    server = server_list[0]
    args.remove(server['servername'])
    if server['game_uid'] in args: args.remove(server['game_uid'])
    logging.debug(f"STEP 7 - Trigger [{action}] action on server")
    serveruid=f"{server['game_uid']}.{server['servername']}"
    orchestrator = next((orc for orc in peon_orchestrators if orc['name'] == server['orchestrator']), None)
    data = server_action(orchestrator['url'],orchestrator['key'],serveruid,'get')
    if "error" in data:
        response = { "status" : "error", "err_code" : "srv.action.error", "command" : action}
    else:
        response = ""
        if action == 'get':
            if "time" not in args:
                response = "```yaml\n{0:<15}: {1}\n{2:<15}: {3}\n{4:<15}: {5}\n{6:<15}: {7}\n{8:<15}: {9}\n".format(
                    "Warcamp",data["servername"],
                    "Type",data['game_uid'],
                    "Peon State",(data["server_state"].lower()),
                    "Server Type",f"{data['container_type']}:{data['build_version']}",
                    "Description",data["description"]
                    )
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
                if data["server_state"].lower() == 'running':
                    if data["time"] is not None:
                        today = pytz.utc.localize(datetime.today()).astimezone(pytz.timezone(settings["timezone"]))
                        stoptime = pytz.utc.localize(datetime.fromtimestamp(int(data["time"]))).astimezone(pytz.timezone(settings["timezone"]))
                        response += "\n\t:alarm_clock: Orc will turn off server at ``"
                        if str(today.date()) == str(stoptime.date()): response += stoptime.strftime("%X %Z")
                        else: response += stoptime.strftime("%X %Z [%x]")
                        response += "``"
                    else:
                        if "time" in args: response += "\n\t:alarm_clock: Server has no shutdown schedule."
                else:
                    if "time" in args: response += "\n\t:alarm_clock: Server is not in running state."
        else:
            body = {}
            if arg_time:
                date_string = (datetime.now(pytz.timezone(settings["timezone"])).date().strftime('%Y-%m-%d'))
                timestring = re.match("^(\d{2})[:h](\d{2})$",arg_time)
                timestring = f"{date_string} {timestring[1]}:{timestring[2]}:00"
                time_tz = pytz.timezone(settings["timezone"]).localize(datetime.strptime(timestring, '%Y-%m-%d %H:%M:%S'))
                epoch = int(time_tz.timestamp())
                if epoch <= int(datetime.now(pytz.timezone(settings["timezone"])).timestamp()):
                    return { "status" : "error", "err_code" : "schedule.past", "command" : action}
                body = {"epoch_time" : f"{epoch}"}
                response += f"\n\n\t:alarm_clock: Warcamp will shut down at ``{timestring}``."
            elif arg_datetime:
                timestring = re.match("^(\d{4})\W(\d{2})\W(\d{2})\.(\d{2})[:h](\d{2})$",arg_datetime)
                timestring = (f"{timestring[1]}-{timestring[2]}-{timestring[3]} {timestring[4]}:{timestring[5]}:00")
                time_tz = pytz.timezone(settings["timezone"]).localize(datetime.strptime(timestring, '%Y-%m-%d %H:%M:%S'))
                epoch = int(time_tz.timestamp())
                if epoch <= int(datetime.now(pytz.timezone(settings["timezone"])).timestamp()):
                    return { "status" : "error", "err_code" : "schedule.past", "command" : action}
                body = {"epoch_time" : f"{epoch}"}
                response += f"\n\n\t:alarm_clock: Warcamp will shut down at ``{timestring}``."
            elif arg_interval:
                body = { "interval" : f"{arg_interval}" }
                response += f"\n\n\t:alarm_clock: Warcamp will shut down in ``{arg_interval}``."
            elif arg_update_mode:
                body = { "mode" : f"{arg_update_mode}" }
                response += f"\n\n\t:arrows_counterclockwise: Warcamp will do a ``{arg_update_mode}`` update."
            # logging.debug("STEP 8 - Permissions check")
            data = server_action(orchestrator['url'], orchestrator['key'], serveruid, action, body)
            if "error" in data:
                return { "status" : "error", "err_code" : "srv.action.error", "command" : action}
            else:
                response += str(data)
        return { "status" : "success", "data" : f"{response}" }
