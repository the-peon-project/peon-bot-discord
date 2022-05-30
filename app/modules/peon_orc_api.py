# IMPORT
import logging
import requests

# Services Get users in a certain group
def getServers(url, api_key):
    logging.debug('[getAllServers]')
    url = f"{url}/api/1.0/servers"
    headers = { 'Accept': 'application/json', 'X-Api-Key': api_key }
    return (requests.get(url, headers=headers)).json()

def getServer(url, api_key, server_uid):
    logging.debug('[getServer]')
    url = f"{url}/api/1.0/server/get/{server_uid}"
    headers = { 'Accept': 'application/json', 'X-Api-Key': api_key }
    return (requests.get(url, headers=headers)).json()

######## MAIN - FOR TEST PURPOSES

if __name__ == "__main__":
    print(getServers("http://dockerdev.za.cloudlet.cloud:5000","my-super-secret-api-key"))
