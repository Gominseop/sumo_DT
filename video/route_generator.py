import numpy as np
import random
import pickle
import math
import copy
from collections import deque
from xml.etree.ElementTree import Element, parse, ElementTree
from scipy.optimize import minimize

# ========전처리 부분========

## 도로에 대한 그래프 얻음
edge_file_path = "test2.edg.xml"
def create_graph_from_xml_file(file_path):
    tree = parse(file_path)
    root = tree.getroot()
    graph = {}

    for edge in root.findall("edge"):
        from_node = edge.get("from")
        to_node = edge.get("to")

        if from_node not in graph:
            graph[from_node] = [to_node]
        else:
            graph[from_node].append(to_node)

    return graph

## 위치 좌표 얻음
node_file_path = "test2.nod.xml"
def extract_positions_from_xml_file(file_path):
    tree = parse(file_path)
    root = tree.getroot()
    position = {}

    for node in root.findall("node"):
        node_id = node.get("id")
        x = float(node.get("x"))
        y = float(node.get("y"))
        position[node_id] = [x, y]

    return position

## 경로 정보 얻음
def extract_edge_from_xml_file(file_path):
    tree= parse(file_path)
    root = tree.getroot()
    edges = {}
    
    for edge in root.findall("edge"):
        edge_id = edge.get("id")
        from_node = edge.get("from")
        to_node = edge.get("to")
        
        if edge_id not in edges:
            edges[edge_id] = [from_node, to_node]
    return edges

"""
{'0_0i': ['0_0', '0'],
 '0_0o': ['0', '0_0'],
 '0_1i': ['0_1', '0'],
 '0_1o': ['0', '0_1'],
 '0_2i': ['0_2', '0'],
 '0_2o': ['0', '0_2'],
 '1_0i': ['1_0', '1'],
 '1_0o': ['1', '1_0'],
 '1_1i': ['1_1', '1'],
 '1_1o': ['1', '1_1'],
 '1_2i': ['1_2', '1'],
 '1_2o': ['1', '1_2'],
 '1_3i': ['1_3', '1'],
 '1_3o': ['1', '1_3'],
 '2_0i': ['2_0', '2'],
 '2_0o': ['2', '2_0'],
 '2_1i': ['2_1', '2'],
 '2_1o': ['2', '2_1'],
 '2_2i': ['2_2', '2'],
 '2_2o': ['2', '2_2'],
 '3_0i': ['3_0', '3'],
 '3_0o': ['3', '3_0'],
 '3_1i': ['3_1', '3'],
 '3_1o': ['3', '3_1'],
 '3_2i': ['3_2', '3'],
 '3_2o': ['3', '3_2'],
 '3_3i': ['3_3', '3'],
 '3_3o': ['3', '3_3'],
 '4_0i': ['4_0', '4'],
 '4_0o': ['4', '4_0'],
 '4_1i': ['4_1', '4'],
 '4_1o': ['4', '4_1'],
 '4_2i': ['4_2', '4'],
 '4_2o': ['4', '4_2'],
 '4_3i': ['4_3', '4'],
 '4_3o': ['4', '4_3'],
 'r1_0_1': ['0_1', '1_0'],
 'r1_1_0': ['1_0', '0_1'],
 'r2_1_2': ['1_2', '2_0'],
 'r2_2_1': ['2_0', '1_2'],
 'r3_2_3': ['2_1', '3_3'],
 'r3_3_2': ['3_3', '2_1'],
 'r4_3_4': ['3_0', '4_2'],
 'r4_4_3': ['4_2', '3_0'],
 'r5_4_1': ['4_3', '1_1'],
 'r5_1_4': ['1_1', '4_3']}
"""

main_edges_route_number = ['r1_0_1', 'r1_1_0', 'r2_1_2', 'r2_2_1', 'r3_2_3', 'r3_3_2', 'r4_3_4', 'r4_4_3', 'r5_4_1', 'r5_1_4']

graph = create_graph_from_xml_file(edge_file_path)
position = extract_positions_from_xml_file(node_file_path)
edges = extract_edge_from_xml_file(edge_file_path)
nodes = ["0_0", "0_2", "1_3", "2_2", "4_0", "4_1", "3_1", "3_2"] # 교통량을 input할 노드들만 적음
# position = {
#     "a" : [-530, 2300],
#     "b" : [-1030, 1800],
#     "c" : [0, 1275],
#     "d" : [-530, -500],
#     "e" : [0, -500],
#     "n1" : [-530, 800],
#     "n2" : [0, 775],
#     "n3" : [-530, 0],
#     "n4" : [0, 0],
#     "n5" : [-530, 1800]
# }

# edges = {
#     # 출발 노드 , 도착 노드
#     1 : ['n5', 'n1'],
#     2 : ['n1', 'n5'],
#     3 : ['n1', 'n2'],
#     4 : ['n2', 'n1'],
#     5 : ['n1', 'n3'],
#     6 : ['n3', 'n1'],
#     7 : ['n2', 'n4'],
#     8 : ['n4', 'n2'],
#     9 : ['n3', 'n4'],
#     10 : ['n4', 'n3']
# }

type_vertex = {
    "직진-좌회전" : [0.7, 0.3],
    "직진-우회전" : [0.7, 0.3],
    "좌회전-우회전" : [0.5, 0.5], # 3개
    "좌회전-직진-우회전" : [0.3, 0.5, 0.2] # 4개
}

def bfs_shortest_paths(start, end, graph=graph):
    """
    graph와 시작 노드, 끝 노드가 있을때 모든 최단경로를 출력하는 함수
    """
    queue = deque()
    visited = set()
    dist = {start: 0}
    paths = {start: [[start]]}
    
    queue.append(start)
    visited.add(start)
    
    while queue:
        curr = queue.popleft()
        for neighbor in graph[curr]:
            if neighbor not in visited:
                visited.add(neighbor)
                dist[neighbor] = dist[curr] + 1
                paths[neighbor] = []
                for path in paths[curr]:
                    paths[neighbor].append(path + [neighbor])
                queue.append(neighbor)
            elif dist[neighbor] == dist[curr] + 1:
                for path in paths[curr]:
                    paths[neighbor].append(path + [neighbor])
    
    return paths[end]

def angle_between_points(p1, p2, p3):
    """
    세 점이 있을때 각도를 구해주는 함수
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3

    angle1 = math.atan2(y2-y1, x2-x1)
    angle2 = math.atan2(y3-y2, x3-x2)

    angle = angle2 - angle1
    angle = math.degrees(angle)

    return angle%360

def direction_from_angle(angle, straight_threshold=30, left_threshold=150):
    """
    angle_between_points로 부터 나온 각도값을 활용하여 직진, 우회전, 죄회전 하는 지 판단하는 함수
    """
    if straight_threshold <= angle <= 180 - straight_threshold:
        return "좌회전"
    elif 180 + straight_threshold <= angle <= 360 - straight_threshold:
        return "우회전"
    else:
        return "직진"

def get_directions(start, end, graph=graph):
    """
    최단경로를 출력해준다.
    예를들어 get_directions("a", "e")를 하는 경우
    > [['직진', '좌회전', '우회전', '직진'], ['직진', '직진', '좌회전', '우회전']]
    출력한다.
    """
    directions = []
    shortest_paths = bfs_shortest_paths(start=start, end=end)
    for path in shortest_paths:
        temp = []
        for j in range(len(path)-2):
            angle = angle_between_points(position[path[j]], position[path[j+1]], position[path[j+2]])
            temp.append(direction_from_angle(angle))
        directions.append(temp)
    return directions

def get_traffic_ratio(paths, directions):
    """
    위에 bfs_shortest_path 함수를 이용하여 최단경로들을 구하고,
    get_directions를 활용하여 진행방향을 구하는 경우
    최종값으로 sink node에서 input이 있을때 최단경로로 진행하는 비율을 구해준다.
    예를들어 
    paths = bfs_shortest_paths("d", "c") 
    > [['d', 'n3', 'n1', 'n2', 'c'], ['d', 'n3', 'n4', 'n2', 'c']]
    directions = get_directions("d", "c")
    > [['직진', '우회전', '좌회전'], ['우회전', '좌회전', '직진']]
    
    """
    ratio = [1]*len(paths)
    what_ratio = [[] for _ in range(len(paths))]
    for i in range(len(paths)):
        short_length = len(paths[i])
        for j in range(1, short_length-1): # 시작과 끝은 항상 그대로 들어간다고 생각하기
            temp = copy.deepcopy(graph[paths[i][j]])
            if len(temp) == 1:
                ratio[i] *= 1
                what_ratio[i].append(1)
            elif len(temp) == 2:
                ratio[i] *= 1
                what_ratio[i].append(1)
            elif len(temp) == 3:
                temp.remove(paths[i][j-1])
                temp.remove(paths[i][j+1])
                angle = angle_between_points(position[paths[i][j-1]], position[paths[i][j]], position[temp[0]])
                another_direction = direction_from_angle(angle)
                if directions[i][j-1] == "직진":
                    if another_direction == "좌회전":
                        ratio[i] *= type_vertex['직진-좌회전'][0]
                        what_ratio[i].append(type_vertex['직진-좌회전'][0])
                    else:
                        ratio[i] *= type_vertex['직진-우회전'][0]
                        what_ratio[i].append(type_vertex['직진-우회전'][0])
                elif directions[i][j-1] == "우회전":
                    if another_direction == "직진":
                        ratio[i] *= type_vertex['직진-우회전'][1]
                        what_ratio[i].append(type_vertex['직진-우회전'][1])
                    else:
                        ratio[i] *= type_vertex['좌회전-우회전'][1]
                        what_ratio[i].append(type_vertex['좌회전-우회전'][1])
                else: # 좌회전 케이스
                    if another_direction == "직진":
                        ratio[i] *= type_vertex['직진-좌회전'][1]
                        what_ratio[i].append(type_vertex['직진-좌회전'][1])
                    else: # 반대가 우회전 케이스
                        ratio[i] *= type_vertex['좌회전-우회전'][0]
                        what_ratio[i].append(type_vertex['좌회전-우회전'][0])
            elif len(temp) == 4:
                if directions[i][j-1] == "직진":
                    ratio[i] *= type_vertex['좌회전-직진-우회전'][1]
                    what_ratio[i].append(type_vertex['좌회전-직진-우회전'][1])
                elif directions[i][j-1] == "좌회전":
                    ratio[i] *= type_vertex['좌회전-직진-우회전'][0]
                    what_ratio[i].append(type_vertex['좌회전-직진-우회전'][0])
                elif directions[i][j-1] == "우회전":
                    ratio[i] *= type_vertex['좌회전-직진-우회전'][2]
                    what_ratio[i].append(type_vertex['좌회전-직진-우회전'][2])
                        
    return ratio, what_ratio

def return_all_routes(start_node, graph=graph, nodes=nodes):
    result = []
    temp = copy.deepcopy(nodes)
    temp.remove(start_node)
    for i in temp:
        routes = bfs_shortest_paths(start=start_node, end=i)
        for j in routes:
            result.append(j)
    return result

def check_sequence(input_list, start_node, end_node):
    check1 = start_node in input_list
    if check1 == False:
        return False
    else:
        index = input_list.index(start_node)+1
        if input_list[index] == end_node:
            return True
        else:
            return False

def filter_routes(routes_number, depart_node):
    """
    routes_number에 간선 번호(1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
    depart_node에 차량을 투입할 depart_node 입력(a, b, c, d, e)
    그러면 결과로 해당 routes를 포함하는 
    """
    vertex_start_node = edges[routes_number][0]
    vertex_end_node = edges[routes_number][1]
    all_routes = return_all_routes(depart_node)
    filtered_routes = []
    for route in all_routes:
        if check_sequence(route, vertex_start_node, vertex_end_node) == True:
            filtered_routes.append(route)
    return filtered_routes

def get_edge_include_routes(route_number, nodes=nodes):
    """
    route_number를 입력하면 그에 해당되는 vertex를 포함하는 최단경로를 전부 출력한다.
    예를들어 get_edge_include_routes(1)를 실행하면
    [['a', 'n5', 'n1', 'n2', 'c'],
     ['a', 'n5', 'n1', 'n3', 'd'],
     ['a', 'n5', 'n1', 'n2', 'n4', 'e'],
     ['a', 'n5', 'n1', 'n3', 'n4', 'e'],
     ['b', 'n5', 'n1', 'n2', 'c'],
     ['b', 'n5', 'n1', 'n3', 'd'],
     ['b', 'n5', 'n1', 'n2', 'n4', 'e'],
     ['b', 'n5', 'n1', 'n3', 'n4', 'e']] 가 나오는데, 전부 다 1번 vertex인 n5-n1을 포함한다.
    """
    results = []
    for node in nodes:
        all_routes = filter_routes(route_number, node)
        for j in all_routes:
            results.append(j)
    return results

all_routes = []
for i in main_edges_route_number:
    temp = get_edge_include_routes(i)
    for route in temp:
        all_routes.append(route)

unique_routes = []
for temp in all_routes:
    if temp not in unique_routes:
        unique_routes.append(temp)
        
def list_to_dict(input_list):
    result = {}
    for key, value in input_list:
        if key not in result:
            result[key] = 0
        result[key] += value
        if result[key] > 1:
            result[key] = 1
    return result

def get_eT():
    return np.random.randint(low=4000, high=5550, size=10) # 랜덤 변수 실행

e_T = get_eT()


def get_p_matrix():
    p_matrix = [[0] * len(unique_routes) for _ in range(len(main_edges_route_number))]
    for i in range(len(main_edges_route_number)):
        for j in range(len(unique_routes)):
            input_list = unique_routes[j]
            start_node, end_node = edges[main_edges_route_number[i]][0], edges[main_edges_route_number[i]][1]
            check = check_sequence(input_list=unique_routes[j], start_node=start_node, end_node=end_node)
            if check == True:
                p_matrix[i][j] = 1
    return np.array(p_matrix)

# 도로별 할당량을 구할때 쓰이는 목적함수
def objective_function_wrapper(p_matrix):
    def objective_function(x):
        e = np.dot(p_matrix, x)
        return np.sum(np.abs(e_T-e))
    return objective_function

def constraint_function(x, constraint_value):
    return constraint_value - np.sum(x)

def get_traffic_volume(objective_volume):
    p_matrix = get_p_matrix()
    bounds = [(int((objective_volume/66)*0.1), None) for _ in range(p_matrix.shape[1])]
    constraints = [{'type' : 'ineq', 'fun' : lambda x: constraint_function(x, objective_volume)}]
    obj_func = objective_function_wrapper(p_matrix)
    
    x0 = np.zeros(p_matrix.shape[1]) # 초기값
    result = minimize(obj_func, x0, constraints=constraints, bounds=bounds)
    
    return list(np.array(result.x).astype(int))

def get_how_much_ratio_get(route_number, graph=graph):
    """
    route_number를 입력하면 return으로 각 node에 해당하는 input이 얼마나 vertex에 기여하는 지 나온다.
    get_how_much_ratio_get(4)를 하는 경우 {'c': 0.51, 'e': 0.21}가 나오는데, c의 input의 51%, e의 input의 21%이 어느 다른 노드의 최단경로를 활용할때 4번 vertex를 지나간다.
    이는 
    """
    results = []
    routes = get_edge_include_routes(route_number)
    directions = []
    for route in routes:
        t = bfs_shortest_paths(start=route[0], end=route[-1])
        index = t.index(route)
        directions.append(get_directions(start=route[0], end=route[-1])[index])
    ratios, what_ratio = get_traffic_ratio(routes, directions)[0], get_traffic_ratio(routes, directions)[1]
    for i in range(len(ratios)):
        vertex_end_node_index = routes[i].index(edges[route_number][1])
        k = len(routes[i])-vertex_end_node_index-1
        product = ratios[i]
        for j in range(k):
            product /= what_ratio[i][-(j+1)]
        results.append([routes[i], product])
    return results

def sum_sublist_lengths(list_of_lists):
    result = {}
    for sublist in list_of_lists:
        first_element = sublist[0]
        if first_element not in result:
            result[first_element] = 0
        result[first_element] += len(sublist)
    return result

def calculate_routes(traffic_volume):
    """
    위에 함수들을 활용하여 특정 route_number와 그에 해당하는 traffic_volume이 주어졌을때
    최단경로에 몇대의 차들을 할당해야 하는 지 나온다.
    예를들어 calculate_routes(6, 1000)를 실행하면 다음과 같은 결과가 나온다.
    {('d', 'n3', 'n1', 'n5', 'a'): 166,
     ('d', 'n3', 'n1', 'n5', 'b'): 166,
     ('d', 'n3', 'n1', 'n2', 'c'): 166,
     ('e', 'n4', 'n3', 'n1', 'n5', 'a'): 1666,
     ('e', 'n4', 'n3', 'n1', 'n5', 'b'): 1666}
    """
    traffic_volumes = get_traffic_volume(objective_volume=traffic_volume)
    result = {}
    for i in range(len(unique_routes)):
        result[tuple(unique_routes[i])] = traffic_volumes[i]
    return result

# ==== 파일 생성 부분 ====
def find_input_list_index(index, input_list):
    cumulative_sum = 0
    for i, item in enumerate(input_list):
        cumulative_sum += item
        if index < cumulative_sum:
            return i
    return -1  # not found

def get_edge_id_from_value(value, edges=edges):
    for key, val in edges.items():
        if val == value:
            return key
    return False

def sorting_vehicle(root):
    vtypes = root.findall('vType')
    routes = root.findall('route')
    vehicles = root.findall('vehicle')
    
    sorted_vehicles = sorted(vehicles, key=lambda v: int(v.get('depart')))
    
    new_routes = Element('routes')
    
    for vtype in vtypes:
        new_routes.append(vtype)
    
    for route in routes:
        new_routes.append(route)
        
    for vehicle in sorted_vehicles:
        new_routes.append(vehicle)
    
    return new_routes

def make_route_xml(traffic_volume):
    """
    route_number : 모델링할 vertex 번호
    traffic_volume : 
    """
    root = Element("routes")
    vType_attrib = {
        "accel" : "1.0",
        "decel" : "5.0",
        "id" : "Car",
        "length" : "2.0",
        "maxSpeed" : "70.0",
        "sigma" : "0.0"
    }
    result = calculate_routes(traffic_volume)
    vType = Element("vType", attrib=vType_attrib)
    root.append(vType)
    temp = 0
    routes = [list(item) if isinstance(item, tuple) else item for item in list(result.keys())]
    volumes = list(result.values())
    for i in range(len(routes)):
        temp_edges = ''
        for j in range(len(routes[i])-1):
            edge_id = get_edge_id_from_value([routes[i][j], routes[i][j+1]])
            temp_edges += edge_id
            if j != len(routes[i])-2:
                temp_edges += " "
        route_attrib = {
            "id" : f"route{i}",
            "edges" : temp_edges
        }
        route_tag = Element("route", attrib=route_attrib)
        root.append(route_tag)
        # route 태그까지 추가 완료.
    indices = []
    index = 0
    for item in volumes:
        for _ in range(item):
            indices.append(index)
            index += 1
    for i in indices:
        depart = np.random.randint(0, 3600)
        route_index = find_input_list_index(i, volumes)
        vehicle_attrib = {
            "depart" : f"{depart}",
            "id" : f"veh{i}",
            "route" : f"route{route_index}",
            "type" : "Car"
        }
        vehicle = Element("vehicle", attrib=vehicle_attrib)
        root.append(vehicle)
    

    root = sorting_vehicle(root)
    indent(root)
    tree = ElementTree(root)
    file_name = "pangyo.rou.xml"
    tree.write(file_name, encoding="utf-8", xml_declaration=True)

# def make_route_xml(route_number, traffic_volumes):
#     """
#     input_node, output_node, 시작시간대 입력시 input_node에서 통계분포를 활용하여 교통량 생성후 그에 맞는 rou.xml 생성
#     """
#     input_volume = get_traffic_volume(transfer[input_node], begin_time)
#     paths = bfs_shortest_paths(input_node, output_node)
#     directions = get_directions(input_node, output_node)
#     ratios = get_traffic_ratio(paths, directions)[0]
#     traffic_volume = [int(input_volume*ratio) for ratio in ratios]
#     generate_route_xml(traffic_volume, paths)
    
### 교통량 생성
# transfer = {
#     "a" : 0,
#     "b" : 1,
#     "c" : 2,
#     "d" : 3,
#     "e" : 4,
# }

# def get_traffic_volume(vertex, time):
#     """
#     vertex : 간선 번호(1~6)
#     time : 시작 시간대(1~23)
#     """
#     lamd = lambds[vertex-1][time-1]
#     result = np.random.poisson(lamd, 1)
#     return result

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


if __name__=="__main__":
    edge_file_path = "test2.edg.xml"
    node_file_path = "test2.nod.xml"
    make_route_xml(3000)