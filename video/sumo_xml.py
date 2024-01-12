import sumolib
import json
import random
import subprocess
import os
import xml.etree.ElementTree as ET
from db_manager import DBManager
from element import SideNode, TLPhase, ICNode, Road, TLLogic


class SUMOGenerator:
    def __init__(self):
        self.icnodes = dict()
        self.connection = dict()
        self.road = dict()
        self.tllogic = dict()
        self.tl_ic = dict()

        # 다른 부분에서 사용해야하는 정보
        # - 각 side의 route의 총량 (RSL의 총 개수)

        # 이후 사용을 위한 저장용/ 아직 안함
        self.node = dict()
        self.edge = dict()
        self.con = dict()
        self.tll = dict()

        # 생성 파일 연결
        self.file_paths = dict()

    def __del__(self):
        pass

    def add_intersection_by_node(self, icnode, sides=None):
        if sides:
            for side in sides:
                icnode.add_side_info(side)
        self.icnodes[icnode.id] = icnode
        self.tl_ic[icnode.tlLogic] = icnode

    def add_intersection_by_info(self, icid, x, y, shape, name, ictype, tlLogic, sides):
        ic = ICNode(icid, x, y, shape, name, ictype, tlLogic)
        for side in sides:
            ic.add_side_info(side)
        self.icnodes[icid] = ic
        self.tl_ic[tlLogic] = ic

    def add_road_by_edge(self, road):
        self.connection[(road.side1, road.side2)] = road
        self.road[road.id] = road

    def add_road_by_info(self, rid, name, side1, side2, laneNum12, laneNum21, speed, length):
        rd = Road(rid, name, side1, side2, laneNum12, laneNum21, speed, length)
        self.connection[(side1, side2)] = rd
        self.road[rid] = rd

    def add_tllogic_by_tl(self, tllogic):
        self.tllogic[tllogic.id] = tllogic

    def add_tllogic_by_info(self, tid, programID, tltype, offset, shape, phases):
        self.tllogic[tid] = TLLogic(tid, programID, tltype, offset, shape, phases)

    def generate_sumo_xml(self):
        pass

    def generate_node_file(self, node_path):
        with open(node_path, "w") as nod:
            nod.write(f'<nodes>\n')
            for icid, ic in self.icnodes.items():
                # ic node 추가
                if "traffic" in ic.type:
                    nod.write(f'   <node id="{icid}" x="{ic.x}" y="{ic.y}" type="{ic.type}" tl="{ic.tlLogic}"/>\n')
                else:
                    nod.write(f'   <node id="{icid}" x="{ic.x}" y="{ic.y}" type="{ic.type}"/>\n')

                # side node 추가
                for sid, side in ic.sides.items():
                    nod.write(f'   <node id="{icid}_{sid}" x="{ic.x+side.x}" y="{ic.y+side.y}" type="priority"/>\n')
                nod.write(f'\n')
            nod.write(f'</nodes>')
        print(f'nod.xml - {node_path} 생성 완료')
        self.file_paths['node'] = node_path

    def generate_edge_file(self, edge_path):
        with open(edge_path, "w") as edg:
            edg.write(f'<edges>\n')
            # side road 생성
            for icid, ic in self.icnodes.items():
                for sid, side in ic.sides.items():
                    edg.write(f'   <edge id="{icid}_{sid}i" from="{icid}_{sid}" to="{icid}" '
                              f'numLanes="{side.entryLaneNum}" speed="{side.speed}" length="{side.length}"/>\n')
                    edg.write(f'   <edge id="{icid}_{sid}o" from="{icid}" to="{icid}_{sid}" '
                              f'numLanes="{side.exitLaneNum}" speed="{side.speed}" length="{side.length}"/>\n')
                    edg.write(f'\n')
            # road 생성
            for i2i, road in self.connection.items():
                edg.write(f'   <edge id="{road.id}_{i2i[0][0]}_{i2i[1][0]}" from="{i2i[0][0]}_{i2i[0][1]}" '
                          f'to="{i2i[1][0]}_{i2i[1][1]}" numLanes="{road.laneNum12}" speed="{road.speed}" '
                          f'length="{road.length}"/>\n')
                edg.write(f'   <edge id="{road.id}_{i2i[1][0]}_{i2i[0][0]}" from="{i2i[1][0]}_{i2i[1][1]}" '
                          f'to="{i2i[0][0]}_{i2i[0][1]}" numLanes="{road.laneNum12}" speed="{road.speed}" '
                          f'length="{road.length}"/>\n')
                edg.write(f'\n')
            edg.write(f'</edges>')
        print(f'edg.xml - {edge_path} 생성 완료')
        self.file_paths['edge'] = edge_path

    def generate_connection_file(self, connection_path):
        rdic = dict(zip(['R', 'S', 'L', 'U'], [0, 1, 2, 3]))
        with open(connection_path, "w") as conn:
            conn.write(f'<connections>\n')
            for icid, ic in self.icnodes.items():
                rsl_num = dict()
                right = dict() # key로 우회전해서 오는 side의 우회전 개수 key: (sid, num)
                for sid, side in ic.sides.items():
                    rsl = side.rslu.split(',')
                    right[rsl[0]] = (sid, side.route.count('R'))

                for sid, side in ic.sides.items():
                    rsl = side.rslu.split(',')
                    s_count = right[rsl[1]][1] if rsl[1] in right else 0
                    l_count = ic.sides[rsl[2]].exitLaneNum-1 if rsl[2] in ic.sides.keys() else 0
                    rsl_num[sid] = {'r': 0, 's': s_count, 'l': l_count}
                    for i, rs in enumerate(side.route.split(',')):
                        for r in rs:
                            if r == 'R':
                                conn.write(f'   <connection from="{icid}_{sid}i" to="{icid}_{rsl[rdic[r]]}o" '
                                           f'fromLane="{i}" toLane="{rsl_num[sid]["r"]}"/>\n')
                                rsl_num[sid]["r"] += 1
                            elif r == 'S':
                                conn.write(f'   <connection from="{icid}_{sid}i" to="{icid}_{rsl[rdic[r]]}o" '
                                           f'fromLane="{i}" toLane="{rsl_num[sid]["s"]}"/>\n')
                                rsl_num[sid]["s"] += 1
                            elif r == 'L':
                                conn.write(f'   <connection from="{icid}_{sid}i" to="{icid}_{rsl[rdic[r]]}o" '
                                           f'fromLane="{i}" toLane="{rsl_num[sid]["l"]}"/>\n')
                                rsl_num[sid]["l"] -= 1
                conn.write(f'   \n')
            conn.write(f'</connections>\n')
        print(f'con.xml - {connection_path} 생성 완료')
        self.file_paths['connection'] = connection_path

    def generate_tll_file(self, tll_path):
        with open(tll_path, "w") as tll:
            tll.write(f'<tlLogics>\n')
            for tlid, tl in self.tllogic.items():
                tll.write(f'   <tlLogic id="{tlid}" type="{tl.type}" programID="{tl.programID}" offset="{tl.offset}">\n')

                con_targets = []
                for sid, side in self.tl_ic[tlid].sides.items():
                    con_targets.append(side.route.replace(',', ''))

                for idx, phase in tl.phases.items():
                    phase_state = ''
                    for s, rs in zip(phase['state'], con_targets):
                        for r in rs:
                            if r == "R":
                                phase_state += 's'
                            elif s == 'R':
                                phase_state += 'r'
                            elif s == 'Y':
                                phase_state += 'y'
                            elif s == 'G':
                                phase_state += 'G'
                            elif s == 'r' and r == 'S':
                                phase_state += 'r'
                            elif s == 'r' and r == 'L':
                                phase_state += 'y'
                            elif s == 'L' and r == 'S':
                                phase_state += 'r'
                            elif s == 'L' and r == 'L':
                                phase_state += 'G'
                            elif s == 'g' and r == 'S':
                                phase_state += 'G'
                            elif s == 'g' and r == 'L':
                                phase_state += 'r'
                            elif s == 'y' and r == 'S':
                                phase_state += 'y'
                            elif s == 'y' and r == 'L':
                                phase_state += 'r'
                    tll.write(f'      <phase duration="{phase["duration"]}" state="{phase_state}"/>\n')
                tll.write(f'   </tlLogic>\n')
            tll.write(f'</tlLogics>')
        print(f'tll.xml - {tll_path} 생성 완료')
        self.file_paths['tllogic'] = tll_path

    def generate_route_file(self, route_path):
        pass

    def generate_net_file(self):
        result = subprocess.call(f'netconvert {self.file_paths["netccfg"]}')
        return result

    def make_netccfg(self, netccfg_path, network_path):
        with open(netccfg_path, "w") as net:
            net.write(f'<configuration>\n')
            net.write(f'   <input>\n')
            net.write(f'      <node-files value="{self.file_paths["node"]}"/>\n')
            net.write(f'      <edge-files value="{self.file_paths["edge"]}"/>\n')
            net.write(f'      <connection-files value="{self.file_paths["connection"]}"/>\n')
            net.write(f'      <tllogic-files value="{self.file_paths["tllogic"]}"/>\n')
            net.write(f'   </input>\n\n')
            net.write(f'   <output>\n')
            net.write(f'      <output-file value="{network_path}"/>\n')
            net.write(f'   </output>\n\n')
            net.write(f'   <report>\n')
            net.write(f'      <verbose value="true"/>\n')
            net.write(f'   </report>\n')
            net.write(f'</configuration>')
        self.file_paths['netccfg'] = netccfg_path
        self.file_paths['network'] = network_path

    def make_sumocfg(self, sumocfg_path, route_path, time_begin, time_end, **file_paths):
        with open(sumocfg_path, "w") as net:
            net.write(f'<configuration>\n')
            net.write(f'   <input>\n')
            net.write(f'      <net-file value="{self.file_paths["network"]}"/>\n')
            net.write(f'      <route-files value="{route_path}"/>\n')
            net.write(f'   </input>\n')
            net.write(f'   <time>\n')
            net.write(f'      <begin value="{time_begin}"/>\n')
            net.write(f'      <end value="{time_end}"/>\n')
            net.write(f'   </time>\n')
            net.write(f'</configuration>')
        self.file_paths['sumocfg'] = sumocfg_path
        self.file_paths['route'] = route_path


if __name__=="__main__":
    # db 연결
    dbm = DBManager()
    dbm.initialize_db('localhost', 3306, 'root', 'filab1020', 'brl', 'utf8')

    # 정보 불러오기
    icids = [f'{i}' for i in range(5)]
    ics = dbm.read_intersection(icids)

    tlids = tuple(set([ic.tlLogic for ic in ics]))
    tls = dbm.read_tllight(tlids)

    roads = dbm.read_road_from_ic(icids)

    # generator 구성
    sumogen = SUMOGenerator()
    for ic in ics:
        sumogen.add_intersection_by_node(ic)
    for tl in tls:
        sumogen.add_tllogic_by_tl(tl)
    for road in roads:
        sumogen.add_road_by_edge(road)

    test_file = 'test2'

    # node 구성
    sumogen.generate_node_file(f'{test_file}.nod.xml')
    # edge 구성
    sumogen.generate_edge_file(f'{test_file}.edg.xml')
    # connection 구성
    sumogen.generate_connection_file(f'{test_file}.con.xml')
    # tllight 구성
    sumogen.generate_tll_file(f'{test_file}.tll.xml')

    # netccfg 구성
    sumogen.make_netccfg(f'{test_file}.netccfg', f'{test_file}.net.xml')
    # net 구성
    sumogen.generate_net_file()
    # route 구성
    sumogen.file_paths['route'] = 'pangyo.rou.xml'
    # sumocfg 구성
    sumogen.make_sumocfg(f'{test_file}.sumocfg', 'pangyo.rou.xml', 0, 10000)
    print('finish')
