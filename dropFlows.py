import requests
import json
from requests import auth
from requests.auth import HTTPBasicAuth


controller_ip = "127.0.0.1"
auth = HTTPBasicAuth("karaf", "karaf")

def dropSingnalFlow(deviceId):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    params = {"appId": 'myApp'}

    data = {
        "priority": 10,
        "timeout": 0,
        "isPermanent": True,
        "deviceId": deviceId,
        "treatment": {
            "instructions": [

            ]
        },
        "selector": {
            "criteria": [
                {
                    "type": "ETH_TYPE",
                    "ethType": "0x0800"
                },

            ]
        }
    }

    add_flows_url = "http://{}:8181/onos/v1/flows/{}".format(controller_ip, deviceId)

    resp = requests.post(url=add_flows_url, params=params, headers=headers, auth=auth, data=json.dumps(data))

    return resp.status_code            


def getDevicesNum():
    
    host_url = "http://{}:8181/onos/v1/devices".format(
        controller_ip)
    headers = {
        "Accept": "application/json"
    }
    resp = requests.get(url=host_url, headers=headers, auth=auth)

    hostData = json.loads(resp.content)
    num = len(hostData['devices'])

    return num


def dropFlows():

    deviceNum = getDevicesNum()
    for i in range(1,deviceNum+1):

        if(i<10):
            id_device = "of:000000000000000" + (hex(int(str(i), 10))[2:])
        else:
            id_device = "of:00000000000000" + (hex(int(str(i), 10))[2:])
        statusCode = dropSingnalFlow(id_device)

    return '200'

    

if __name__ == '__main__':
    if dropFlows() == '200':
        print('Drop Flows Success')
    else:
        print('Drop Flows Failed')
