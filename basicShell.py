import requests
import json
import networkx as nx
from flask import request
from requests import auth
from requests.auth import HTTPBasicAuth


srcHost = ''
desHost = ''
path = []

controller_ip = "127.0.0.1"
auth = HTTPBasicAuth("karaf", "karaf")


# 获取时延信息，返回json
def get_delay():
    delay_url = "http://{}:8181/onos/get-link-delay/GetDelay".format(
        controller_ip)
    headers = {
        "Accept": "application/json"
    }

    resp = requests.get(url=delay_url, headers=headers, auth=auth)

    return resp.status_code, resp.text


# 获取端口关系的拓扑
def get_graph():
    graph_url = "http://{}:8181/onos/choice-best-path/graph".format(
        controller_ip)
    headers = {
        "Accept": "application/json"
    }

    resp = requests.get(url=graph_url, headers=headers, auth=auth)

    return resp.status_code, resp.text


# 获取主机和交换机关系的拓扑
def get_host():
    host_url = "http://{}:8181/onos/device-and-host/devicehost".format(
        controller_ip)
    headers = {
        "Accept": "application/json"
    }

    resp = requests.get(url=host_url, headers=headers, auth=auth)

    return resp.status_code, resp.text


# 生成选路所用的拓扑
def for_path():
    status1, de_resp = get_delay()
    status2, gr_resp = get_graph()
    if status1 == 200 and status2 == 200:
        delay_info = json.loads(de_resp)
        graph_info = json.loads(gr_resp)

        for key in graph_info:
            neig = graph_info[key]
            for i in range(len(neig)):
                if key[:-2] != neig[i][:-2]:
                    neig[i] += ":"+str((delay_info[key[:-2]+' '+neig[i]
                                                   [: -2]]+delay_info[neig[i][: -2]+' '+key[:-2]])/2)

                else:
                    neig[i] += ":"+str(10000000)

    list = []
    for port in graph_info:
        tempList = graph_info[port]
        for i in tempList:
            temp = i.split(':')
            tempTuple = (port, temp[0]+':'+temp[1], float(temp[2]))
            list.append(tempTuple)

    return list


# 生成前端所需的拓扑格式
def basicTopoDisplay():
    status1, de_resp = get_delay()

    status3, ho_resp = get_host()
    graph_show = {
        "nodes": [],
        "links": []
    }
    if status1 == 200 and status3 == 200:
        delay_info = json.loads(de_resp)
        host_info = json.loads(ho_resp)

        for key in host_info:
            node = {"id": key}
            graph_show["nodes"].append(node)
            host = host_info[key]
            for i in range(len(host)):
                node = {"id": host[i]}
                graph_show["nodes"].append(node)
                link = {
                    "source": key,
                    "target": host[i],
                    "value": "100000"
                }
                graph_show["links"].append(link)

        for key in delay_info:
            link = {
                "source": key[:19],
                "target": key[-19:],
                "value": str((delay_info[key]+delay_info[key[-19:]+" "+key[:19]])/2)
            }
            graph_show["links"].append(link)

    return graph_show


# 
def chooseBestPath():
    
    
    headers = {'Accept': 'application/json'}
    get_device_url = 'http://{}:8181/onos/v1/hosts'.format(controller_ip)
    resp = requests.get(url=get_device_url, headers=headers, auth=auth)

    hostData = json.loads(resp.text)
    hostColumn = hostData.get("hosts")
    hostDict = {}
    for host in hostColumn:
        temp1 = host.get("ipAddresses")
        key = temp1[0]
        temp2 = host.get("locations")
        dict = temp2[0]
        value = dict.get("elementId") + '/' + dict.get("port")
        hostDict[key] = value

    hostChoice = request.json
     
    srcHost = hostChoice.get('ip1')
    
    desHost = hostChoice.get('ip2')
    
    for ip in hostDict.keys():
        if(srcHost == ip):
            srcPort = hostDict[ip]
        if(desHost == ip):
            desPort = hostDict[ip]

    list = for_path()
    G = nx.DiGraph()
    G.add_weighted_edges_from(list)
    path=nx.dijkstra_path(G,srcPort,desPort)


    path.insert(0, srcHost)
    path.append(desHost)

    graph_bestPath = {
        "nodes": [],
        "links": []
    }


    for i in path:
        node = {"id": i}
        graph_bestPath["nodes"].append(node)
    
    i=0
    while(i+1<len(path)):
        link = {
            "source": path[i],
            "target": path[i+1],
            "value": "0"
        }
        graph_bestPath["links"].append(link)
        i = i+1
        
    return graph_bestPath


def addSingnalFlow(src_ip, dst_ip, deviceId, sw_port_src, sw_port_dst):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        params = {"appId": "choicepath"}

        data = {
            "priority": 12,
            "timeout": 0,
            "isPermanent": True,
            "deviceId": deviceId,
            "treatment": {
                "instructions": [
                    {
                        "type": "OUTPUT",
                        "port": sw_port_dst
                    }
                ]
            },
            "selector": {
                "criteria": [
                        {
                            "type": "IPV4_DST",
                            "ip": dst_ip
                        },

                    {
                            "type": "IPV4_SRC",
                            "ip": src_ip
                            },

                    {
                            "type": "ETH_TYPE",
                            "ethType": "0x800"
                            },

                    {
                            "type": "IN_PORT",
                            "port": sw_port_src
                            }
                ]
            }
        }

        add_flows_url = "http://{}:8181/onos/v1/flows/{}".format(
            controller_ip, deviceId)

        resp = requests.post(url=add_flows_url, params=params,
                             headers=headers, auth=auth, data=json.dumps(data))

        return resp.status_code


def addFlows():
    
    src_ip = srcHost
    dst_ip = desHost

    for i in range(1, len(path)-1, 2):
      
        if i < len(path) - 1:
            addSingnalFlow(src_ip, dst_ip, path[i][:-2], path[i][-1:], path[i + 1][-1:])
            addSingnalFlow(dst_ip, src_ip, path[i + 1][:-2], path[i + 1][-1:], path[i][-1:])

    return True


def deleteFlows():
    headers = {"Accept": "application/json"}
    appId = "myApp"
    
    delete_device_url = 'http://{}:8181/onos/v1/flows/application/{}'.format(controller_ip, appId)

    resp = requests.delete(url=delete_device_url, headers=headers, auth=auth)

    return resp.status_code


# 测试
if __name__ == "__main__":
    # graph_path = for_path()
    # graph_show = basicTopoDisplay()
    # print(json.dumps(graph_path, indent=2))
    # print(json.dumps(graph_show, indent=2))
    # print(chooseBestPath())
    # print(getDevicesNum())
    print(deleteFlows())
    # print(get_host(controller_ip))
    # print(for_path())