<center><font size=6>BackEnd</center></font>

### backEnd.py是onos北向接口与前端衔接的后端代码，主要接口如下：
- 接口1--/basictopo， 返回包含了基本拓扑信息的json数据；
- 接口2--/bestpath，接收前端发送的主机选择信息，返回Dijkstra算法的选路结果。

### basicShell.py是调用北向接口并生成前端和选路算法所需数据，主要方法如下：
-   get_delay()——获取时延信息
-   get_graph()——获取端口关系的拓扑
-   get_host()——获取主机和交换机关系的拓扑
-   for_path()——生成选路所用的拓扑
-   basicTopoDisplay()——生成前端所需的拓扑格式
-   chooseBestPath()——利用获取的时延信息生成最优路径
-   addSingnalFlow(src_ip, dst_ip, deviceId, sw_port_src, sw_port_dst)——为单个交换机下发流表
-   addFlows()——为最优路径上所有交换机下发流表
-   deleteFlows()——删除之前下发的流表
