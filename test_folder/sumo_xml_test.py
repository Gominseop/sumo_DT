import os
import sys
import time
import json
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.sumo_xml import SUMOGenerator
from utils.db_manager import DBManager

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, ElementTree

HOME_PATH = os.getcwd()
print(HOME_PATH)


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
    # db 연결
    dbm = DBManager()
    dbm.initialize_db('localhost', 3306, 'root', 'filab1020', 'filab_traffic', 'utf8')

    out = {}

    # 정보 불러오기
    # icids = ['3500007700']
    # icids = ['3500006301', '3500006700', '3500007500', '3500007900', '3500008000', '3510000200', '3510000250',
    #          '3510000300', '3510000400', '3510000450', '3510021700', '3510021750', '3510021500', '3510021400',
    #          '3500065800', '3500065850', '3500062500', '3500062550', '3510021350', '3510021300', '3510021200',
    #          '3510021250', '3500062100', '3500060600', '3500060650', '3500060660', '3500062400', '3500060100',
    #          '3500060800', '3500058900', '3500060850', '3500060860', '3500059350', '3500058550', '3500302300',
    #          '3500051804', '3500051802', '3500007400', '3500007100', '3500006900', '3500058700', '3500006901',
    #          '3500058500', '3500006600', '3500006650', '3500006660', '3500006800', '3500007300', '3500007350',
    #          '3500059300', '3500059800', '3500059850', '3500007700']
    icids = ['3510021350', '3510021300', '3500058900', '3500007100', '3500060860', '3500060800',
             '3500060850', '3510021200', '3510021250', '3500062100', '3500058700', '3500060600']

    out["target ic ids"] = icids
    out["node side"] = len(icids)

    # 형산 교차로는 문제가 있어 제외 3500007700
    # 교통섬 X, 직진이 우회전 방해 가능
    t = time.time()
    ics = dbm.read_intersection(icids)
    s = time.time() - t
    out["read intersection"] = s

    t = time.time()
    tlids = set([ic.tlLogic for ic in ics])
    if '-1' in tlids:
        tlids.remove('-1')
    tlids = tuple(tlids)
    tls = dbm.read_tllight(tlids)
    s = time.time() - t
    out["read traffic light"] = s

    t = time.time()
    roads = dbm.read_road_from_ic(icids)
    s = time.time() - t
    out["read road"] = s

    outputs = dbm.read_output('test')

    # 원래라면 generator 내에서 처리하는 것이 맞지만, 흐름 확인을 위해 따로 처리
    leafs, sources, sinks = dbm.read_virtual_ic_road(icids)

    t = time.time()
    road_ids = []
    source_ids = []
    sink_ids = []
    for road in roads:
        road_ids.append(road.id)
    for source in sources:
        source_ids.append(source.id)
    for sink in sinks:
        sink_ids.append(sink.id)
    road_traffic = dbm.read_road_traffic(road_ids)
    source_traffic = dbm.read_road_traffic(source_ids)
    sink_traffic = dbm.read_road_traffic(sink_ids)
    s = time.time() - t
    out["read traffic"] = s

    # generator 구성
    t = time.time()
    sumogen = SUMOGenerator()
    for ic in ics:
        sumogen.add_intersection_by_node(ic)
    for tl in tls:
        sumogen.add_tllogic_by_tl(tl)
    for road in roads:
        sumogen.add_road_by_edge(road)
    # for output in outputs:
    #     sumogen.add_addition_by_output(output)

    # 원래라면 생성 버튼을 누름과 동시에 뒤에서 처리되는 것이 맞지만, 흐름 확인을 위해 따로 처리
    sumogen.add_leaf_element(leafs, sources, sinks)
    sumogen.set_road_traffic(road_traffic, 'between')
    sumogen.set_road_traffic(source_traffic, 'source')
    sumogen.set_road_traffic(sink_traffic, 'sink')
    s = time.time() - t
    out["set generator"] = s

    # sumogen.generate_addition_file('C:/Users/FILAB/Desktop/arrange/5_code/SUMO/sumo_DT/test_folder/test_1.add.xml',
    #                                'test_1')

    test_file = 'test'

    # 경로는 절대 경로로
    # node 구성
    t = time.time()
    sumogen.generate_node_file(f'{test_file}.nod.xml')
    s = time.time() - t
    out["node file"] = f'{test_file}.nod.xml'
    out["generate node"] = s

    # edge 구성
    t = time.time()
    sumogen.generate_edge_file(f'{test_file}.edg.xml')
    s = time.time() - t
    out["edge file"] = f'{test_file}.edg.xml'
    out["generate edge"] = s

    # connection 구성
    t = time.time()
    sumogen.generate_connection_file(f'{test_file}.con.xml')
    s = time.time() - t
    out["connection file"] = f'{test_file}.con.xml'
    out["generate connection"] = s

    # tllight 구성
    t = time.time()
    sumogen.generate_tll_file(f'{test_file}.tll.xml')
    s = time.time() - t
    out["traffic light file"] = f'{test_file}.tll.xml'
    out["generate traffic light"] = s

    # netccfg 구성
    t = time.time()
    sumogen.make_netccfg(f'{test_file}.netccfg', f'{test_file}.net.xml')
    # net 구성
    sumogen.generate_net_file()
    s = time.time() - t
    out["network file"] = f'{test_file}.net.xml'
    out["generate network"] = s


    # route 구성
    # sumogen.generate_random_route_file(f'{test_file}.net.xml', f'{test_file}.rou.xml', end=110,
    #                             seed=77, period=0.1, fringe_factor=2)
    t = time.time()
    sumogen.generate_route_file(f'{test_file}_route.rou.xml', f'{test_file}_flow.rou.xml',
                                f'{test_file}_detector.xml', f'{test_file}_traffic.txt',
                                repeat=20)
    out["traffic file"] = f'{test_file}_detector.xml {test_file}_traffic.txt'
    out["route file"] = f'{test_file}_route.rou.xml {test_file}_flow.rou.xml'
    out["generate route"] = s

    # sumocfg 구성
    # sumogen.make_sumocfg(f'{test_file}.sumocfg', 0, 10000)
    sumogen.make_sumocfg(f'{test_file}.sumocfg', 0, 5000,
                         summary_path=f'{test_file}_summary.xml', edge_path=f'{test_file}_edge.xml')
    print('finish')

    with open(f'{test_file}_info.json', 'w') as f:
        json.dump(out, f, indent=2)

