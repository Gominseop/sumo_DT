import sumolib
import json
import random
import subprocess
import os
import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, ElementTree
sys.path.append('utils')
if 'SUMO_HOME' in os.environ:
    sys.path.append(os.environ['SUMO_HOME'])
from utils.db_manager import DBManager
from utils.element import SideNode, TLPhase, ICNode, Road, TLLogic

from sumo.tools import randomTrips


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


class SUMOGenerator:
    def __init__(self):
        self.icnodes = dict()
        self.connection = dict()
        self.road = dict()
        self.tllogic = dict()
        self.addtion = dict()
        self.tl_ic = dict()

        # uturn 신호 처리용
        self.u_check = dict()

        # 출력용
        self.summary = -1
        self.queue = -1

        # 다른 부분에서 사용해야하는 정보
        # - 각 side의 route의 총량 (RSL의 총 개수)

        # 이후 사용을 위한 저장용/ 아직 안함
        self.node = dict()
        self.edge = dict()
        self.con = dict()
        self.tll = dict()

        # 생성 파일 연결
        self.output_id = ''
        self.file_paths = dict()
        self.result_paths = {'summary': '', 'queue': '', 'edge': '', 'lane': '', 'tls': ''}

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

    # 다른 확장이 생기게 되면, addition을 위한 class가 필요
    def add_addition_by_info(self):
        pass

    def add_addition_by_output(self, output):
        self.output_id = output.oid
        self.addtion[output.oid] = output

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
        return node_path

    def generate_edge_file(self, edge_path):
        with open(edge_path, "w") as edg:
            edg.write(f'<edges>\n')
            # side road 생성
            for icid, ic in self.icnodes.items():
                for sid, side in ic.sides.items():
                    if side.entryLaneNum != 0:
                        edg.write(f'   <edge id="{icid}_{sid}i" from="{icid}_{sid}" to="{icid}" '
                                  f'numLanes="{side.entryLaneNum}" speed="{side.speed}" length="{side.length}"/>\n')
                    if side.exitLaneNum != 0:
                        edg.write(f'   <edge id="{icid}_{sid}o" from="{icid}" to="{icid}_{sid}" '
                                  f'numLanes="{side.exitLaneNum}" speed="{side.speed}" length="{side.length}"/>\n')
                    edg.write(f'\n')
            # road 생성
            for i2i, road in self.connection.items():
                if road.laneNum12 != 0:
                    edg.write(f'   <edge id="{road.id}_{i2i[0][0]}_{i2i[1][0]}" from="{i2i[0][0]}_{i2i[0][1]}" '
                              f'to="{i2i[1][0]}_{i2i[1][1]}" numLanes="{road.laneNum12}" speed="{road.speed}" '
                              f'length="{road.length}"/>\n')
                if road.laneNum21 != 0:
                    edg.write(f'   <edge id="{road.id}_{i2i[1][0]}_{i2i[0][0]}" from="{i2i[1][0]}_{i2i[1][1]}" '
                              f'to="{i2i[0][0]}_{i2i[0][1]}" numLanes="{road.laneNum21}" speed="{road.speed}" '
                              f'length="{road.length}"/>\n')
                edg.write(f'\n')
            edg.write(f'</edges>')
        print(f'edg.xml - {edge_path} 생성 완료')
        self.file_paths['edge'] = edge_path
        return edge_path

    def generate_connection_file(self, connection_path):
        # u턴 추가 지역
        rdic = dict(zip(['R', 'S', 'L', 'U'], [0, 1, 2, 3]))
        with open(connection_path, "w") as conn:
            conn.write(f'<connections>\n')
            for icid, ic in self.icnodes.items():
                rsl_num = dict()
                right = dict() # key로 우회전해서 오는 side의 우회전 개수 key: (sid, num)
                straight = dict() # key로 직진해서 오는 side의 직진 개수 key: (sid, num)
                for sid, side in ic.sides.items():
                    rsl = side.rslu.split(',')
                    right[rsl[0]] = (sid, side.route.count('R'))
                    straight[rsl[1]] = (sid, side.route.count('S'))

                for sid, side in ic.sides.items():
                    if side.rslu == '':
                        continue
                    rsl = side.rslu.split(',')
                    s_count = right[rsl[1]][1] if rsl[1] in right else 0
                    l_count = ic.sides[rsl[2]].exitLaneNum-1 if rsl[2] in ic.sides.keys() else 0
                    
                    # 직진해야 하는 수 + 우회전에서 오는 수(s_count)가 exitLaneNum보다 크다면, 우회전을 공유
                    if rsl[1] != '-1' and side.route.count('S') + s_count > ic.sides[rsl[1]].exitLaneNum:
                        s_count = s_count - (side.route.count('S') + s_count - ic.sides[rsl[1]].exitLaneNum)

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
                            elif r == 'U':
                                # conn.write(f'   <connection from="{icid}_{sid}i" to="{icid}_{rsl[rdic[r]]}o" '
                                #            f'fromLane="{i}" toLane="0"/>\n')
                                conn.write(f'   <connection from="{icid}_{sid}i" to="{icid}_{rsl[rdic[r]]}o" '
                                           f'fromLane="{i}" toLane="{ic.sides[rsl[rdic[r]]].exitLaneNum-1}"/>\n')
                                # 자기 회전 여부
                                #if sid == rsl[rdic[r]]:
                                #    self.u_check[(icid, sid)] = True
                                #else:
                                #    self.u_check[(icid, sid)] = False
                                #conn.write(f'   <connection from="{icid}_{sid}i" to="{icid}_{sid}o" '
                                #           f'fromLane="{i}" toLane="0"/>\n')
                conn.write(f'   \n')
            conn.write(f'</connections>\n')
        print(f'con.xml - {connection_path} 생성 완료')
        self.file_paths['connection'] = connection_path
        return connection_path

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
                    # uturn 처리용 side id 구하기
                    sid = -1
                    for s, rs in zip(phase['state'], con_targets):
                        sid += 1
                        for r in rs:
                            # 우회전
                            if r == "R":
                                phase_state += 's'
                            # 유턴 무제한 단 같은 우선 순위로 u턴을 비현실적인 수준으로 진행 바로 옆 라인으로
                            elif r == "U":
                                # 같은 side u turn은 GG, 다른 side로의 u turn은 G
                                phase_state += 'G'
                                #if self.u_check[(self.tl_ic[tlid].id, str(sid))]:
                                #    phase_state += 'GG'
                                #else:
                                #    phase_state += 'G'
                            # 빨간
                            elif s == 'R':
                                phase_state += 'r'
                            # 노란불
                            elif s == 'Y':
                                phase_state += 'y'
                            # 초록불
                            elif s == 'G':
                                phase_state += 'G'
                            # 점멸등
                            elif s == 'B':
                                phase_state += 'o'
                            elif s == 'b':
                                phase_state += 'o'
                            # 노란불 + 빨깐불
                            elif s == 'r' and r == 'S':
                                phase_state += 'r'
                            elif s == 'r' and r == 'L':
                                phase_state += 'y'
                            # 좌회전 + 빨간불
                            elif s == 'L' and r == 'S':
                                phase_state += 'r'
                            elif s == 'L' and r == 'L':
                                phase_state += 'G'
                            # 직진
                            elif s == 'g' and r == 'S':
                                phase_state += 'G'
                            elif s == 'g' and r == 'L':
                                phase_state += 'r'
                            #직진용 노란불
                            elif s == 'y' and r == 'S':
                                phase_state += 'y'
                            elif s == 'y' and r == 'L':
                                phase_state += 'r'
                            # 직진 + 노란불
                            elif s == 'l' and r == 'S':
                                phase_state += 'G'
                            elif s == 'l' and r == 'L':
                                phase_state += 'y'
                    tll.write(f'      <phase duration="{phase["duration"]}" state="{phase_state}"/>\n')
                tll.write(f'   </tlLogic>\n')
            tll.write(f'</tlLogics>')
        print(f'tll.xml - {tll_path} 생성 완료')
        self.file_paths['tllogic'] = tll_path
        return tll_path

    def generate_addition_file(self, add_path, output_path_name):
        #output_path_name은 path에 base이름을 붙이고 확장자는 없는것 e.g) a/b/abc
        root = Element('additional')

        for oid, value in self.addtion.items():
            edge_params = value.edge_params.edgeParameter_to_dict()
            for cate in value.target:
                ff = ''
                if cate == 'summary' and self.summary == -1:
                    self.summary = value.period
                elif cate == 'queue' and self.queue == -1:
                    self.queue = value.period
                elif cate == 'edge':
                    element1 = SubElement(root, 'edgeData')
                    for n, v in edge_params.items():
                        # file의 경우 통일된 것에 추가로 붙이는 형식
                        if str(n) == 'file':
                            element1.set(n, f"{output_path_name}_edge_{str(v)}.xml")
                            ff = f"{output_path_name}_edge_{str(v)}.xml"
                        else:
                            element1.set(n, str(v))
                    self.result_paths['edge'] = ff
                elif cate == 'lane':
                    element2 = SubElement(root, 'laneData')
                    for n, v in edge_params.items():
                        # file의 경우 통일된 것에 추가로 붙이는 형식
                        if str(n) == 'file':
                            element2.set(n, f"{output_path_name}_lane_{str(v)}.xml")
                            ff = f"{output_path_name}_lane_{str(v)}.xml"
                        else:
                            element2.set(n, str(v))
                    self.result_paths['lane'] = ff
                elif cate == 'tllight':
                    self.result_paths['tls'] = {'state': {}, 'switch_time': {}, 'switch_state': {}, 'program': {}}
                    for t in value.tls_type:
                        element3 = SubElement(root, 'timedEvent')
                        element3.set('type', t)
                        element3.set('source', value.tllogics)
                        if t == 'SaveTLSStates':
                            element3.set('dest', f'{output_path_name}_tls_state_{value.tllogics}.xml')
                            self.result_paths['tls']['state'][value.tllogics] = f'{output_path_name}_tls_state_{value.tllogics}.xml'
                        if t == 'SaveTLSSwitchTimes':
                            element3.set('dest', f'{output_path_name}_tls_switch_time_{value.tllogics}.xml')
                            self.result_paths['tls']['switch_time'][value.tllogics] = f'{output_path_name}_tls_switch_time_{value.tllogics}.xml'
                        if t == 'SaveTLSSwitchStates':
                            element3.set('dest', f'{output_path_name}_tls_switch_state_{value.tllogics}.xml')
                            self.result_paths['tls']['switch_state'][value.tllogics] = f'{output_path_name}_tls_switch_state_{value.tllogics}.xml'
                        if t == 'SaveTLSProgram':
                            element3.set('dest', f'{output_path_name}_tls_program_{value.tllogics}.xml')
                            self.result_paths['tls']['program'][value.tllogics] = f'{output_path_name}_tls_program_{value.tllogics}.xml'

        indent(root)
        et = ElementTree(root)
        et.write(add_path, encoding='utf-8', xml_declaration=True)
        self.file_paths["addition"] = add_path
        return add_path

    # 생성후에 route 부분에서 namespace나 형식 부분은 제거야해 돌아감
    # 직접 생성하면 이것을 사용하지 않음 / 랜덤 생성
    def generate_route_file(self, net_path, route_path, begin=0, end=3600, rand=False, seed=-1, period=1, fringe_factor=1):
        ops = ['-n', net_path, '-o', route_path]
        if begin != 0:
            ops.append('-b')
            ops.append(begin)
        if end != 3600:
            ops.append('-e')
            ops.append(end)
        if rand:
            ops.append('--random')
        if seed != -1:
            ops.append('--seed')
            ops.append(seed)
        if period != 1:
            ops.append('--period')
            ops.append(period)
        if fringe_factor != 1:
            ops.append('--fringe-factor')
            ops.append(fringe_factor)
        randomTrips.main(randomTrips.get_options(['-n', net_path, '-o', route_path]))

        # #file_path = 'C:/Users/FILAB/anaconda3/envs/sumo/Lib/site-packages/sumo/tools/randomTrips.py'
        # file_path = os.environ['SUMO_HOME'] + '/randomTrips.py'
        # commend = f'python "{file_path}" -n {net_path} -o {route_path}'
        # if begin != 0:
        #     commend += f' -b {begin}'
        # if end != 3600:
        #     commend += f' -e {end}'
        # if rand:
        #     commend += ' --random'
        # if seed != -1:
        #     commend += f' --seed {seed}'
        # if period != 1:
        #     commend += f' --period {period}'
        # if fringe_factor != 1:
        #     commend += f' --fringe-factor {fringe_factor}'
        # result = subprocess.call(commend)

        et = ET.parse(route_path)
        rt = et.getroot()
        rt.attrib.clear()
        et.write(route_path, encoding="utf-8", xml_declaration=True)

        self.file_paths['route'] = route_path
        return route_path

    def generate_net_file(self):
        result = subprocess.call(f'netconvert {self.file_paths["netccfg"]}')
        return self.file_paths["netccfg"]

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
        return netccfg_path

    def make_sumocfg(self, sumocfg_path, time_begin, time_end, route_path='',
                     summary_path='', summary_period=100, queue_path='', queue_period=100,
                     edge_path='', lane_path='', **file_paths):
        with open(sumocfg_path, "w") as net:
            net.write(f'<configuration>\n')
            net.write(f'   <input>\n')
            net.write(f'      <net-file value="{self.file_paths["network"]}"/>\n')
            if route_path != '':
                net.write(f'      <route-files value="{route_path}"/>\n')
            if 'addition' in self.file_paths:
                net.write(f'      <additional-files value="{self.file_paths["addition"]}"/>\n')
            net.write(f'   </input>\n')
            net.write(f'   <output>\n')
            if self.summary != -1 and 'summary' in file_paths:
                net.write(f'''      <summary-output value="{file_paths['summary']}"/>\n''')
                net.write(f'''      <summary-output.period value="{self.summary}"/>\n''')
                self.result_paths['summary'] = file_paths['summary']
            if self.queue != -1 and 'queue' in file_paths:
                net.write(f'''      <queue-output value="{file_paths['queue']}"/>\n''')
                net.write(f'''      <queue-output.period value="{self.queue}"/>\n''')
                self.result_paths['queue'] = file_paths['queue']
            if summary_path != '':
                net.write(f'''      <summary-output value="{summary_path}"/>\n''')
                net.write(f'''      <summary-output.period value="{summary_period}"/>\n''')
            if queue_path != '':
                net.write(f'''      <queue-output value="{queue_path}"/>\n''')
                net.write(f'''      <queue-output.period value="{queue_period}"/>\n''')
            if edge_path != '':
                net.write(f'''      <edgedata-output value="{edge_path}"/>\n''')
            if lane_path != '':
                net.write(f'''      <lanedata-output value="{lane_path}"/>\n''')
            net.write(f'   </output>\n')
            net.write(f'   <time>\n')
            net.write(f'      <begin value="{time_begin}"/>\n')
            net.write(f'      <end value="{time_end}"/>\n')
            net.write(f'   </time>\n')
            net.write(f'</configuration>')
        self.file_paths['sumocfg'] = sumocfg_path
        return sumocfg_path

    def run_sumocfg(self, sumocfg_path=None, print_out=False):
        if sumocfg_path:
            commend = f"sumo {sumocfg_path}"
        else:
            commend = f"sumo {self.file_paths['sumocfg']}"

        if print_out:
            process = subprocess.Popen(commend, shell=True, stdout=subprocess.PIPE, encoding='utf-8')
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
        else:
            subprocess.call(commend)

    def run_sumo(self, sumocfg_path):
        result = subprocess.call(f'sumo {sumocfg_path}')

    def run_sumogui(self, sumocfg_path):
        result = subprocess.call(f'sumo-gui {sumocfg_path}')


if __name__=="__main__":
    # db 연결
    dbm = DBManager()
    dbm.initialize_db('localhost', 3306, 'root', 'filab1020', 'filab_traffic', 'utf8')

    # 정보 불러오기
    # icids = ['3500007700']
    icids = ['3500006301', '3500006700', '3500007500', '3500007900', '3500008000', '3510000200', '3510000250',
             '3510000300', '3510000400', '3510000450', '3510021700', '3510021750', '3510021500', '3510021400',
             '3500065800', '3500065850', '3500062500', '3500062550', '3510021350', '3510021300', '3510021200',
             '3510021250', '3500062100', '3500060600', '3500060650', '3500060660', '3500062400', '3500060100',
             '3500060800', '3500058900', '3500060850', '3500060860', '3500059350', '3500058550', '3500302300',
             '3500051804', '3500051802', '3500007400', '3500007100', '3500006900', '3500058700', '3500006901',
             '3500058500', '3500006600', '3500006650', '3500006660', '3500006800', '3500007300', '3500007350',
             '3500059300', '3500059800', '3500059850']
    # 형산 교차로는 문제가 있어 제외 3500007700
    # 교통섬 X, 직진이 우회전 방해 가능
    ics = dbm.read_intersection(icids)

    tlids = tuple(set([ic.tlLogic for ic in ics]))
    tls = dbm.read_tllight(tlids)

    roads = dbm.read_road_from_ic(icids)

    outputs = dbm.read_output('test')

    # generator 구성
    sumogen = SUMOGenerator()
    for ic in ics:
        sumogen.add_intersection_by_node(ic)
    for tl in tls:
        sumogen.add_tllogic_by_tl(tl)
    for road in roads:
        sumogen.add_road_by_edge(road)
    # for output in outputs:
    #     sumogen.add_addition_by_output(output)

    test_file = 'test_1'

    # sumogen.generate_addition_file('C:/Users/FILAB/Desktop/arrange/5_code/SUMO/sumo_DT/test_folder/test_1.add.xml',
    #                                'test_1')

    # 경로는 절대 경로로
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
    sumogen.generate_route_file(f'{test_file}.net.xml', f'{test_file}.rou.xml', end=3600,
                                seed=77, period=0.5, fringe_factor=100)
    # sumocfg 구성
    # sumogen.make_sumocfg(f'{test_file}.sumocfg', 0, 10000)
    sumogen.make_sumocfg(f'{test_file}.sumocfg', 0, 5000, route_path=f'{test_file}.rou.xml')
    print('finish')
