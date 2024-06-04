import datetime
import os
import sys
import subprocess
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

    # 정보 불러오기
    # icids = ['3500006301']
    # icids = ['3500006301', '3500006700', '3500007500', '3500007900', '3500008000', '3510000200', '3510000250',
    #          '3510000300', '3510000400', '3510000450', '3510021700', '3510021750', '3510021500', '3510021400',
    #          '3500065800', '3500065850', '3500062500', '3500062550', '3510021350', '3510021300', '3510021200',
    #          '3510021250', '3500062100', '3500060600', '3500060650', '3500060660', '3500062400', '3500060100',
    #          '3500060800', '3500058900', '3500060850', '3500060860', '3500059350', '3500058550', '3500302300',
    #          '3500051804', '3500051802', '3500007400', '3500007100', '3500006900', '3500058700', '3500006901',
    #          '3500058500', '3500006600', '3500006650', '3500006660', '3500006800', '3500007300', '3500007350',
    #          '3500059300', '3500059800', '3500059850', '3500007700', '3500302500']
    # icids = ['3500007500', '3500007400', '3500007900', '3500060100', '3500058900', '3500007100']
    icids = ['3500007500', '3500007400', '3500007100']

    # 형산 교차로는 문제가 있어 제외 3500007700
    # 교통섬 X, 직진이 우회전 방해 가능
    ics = dbm.read_intersection(icids)

    tlids = set([ic.tlLogic for ic in ics])
    if '-1' in tlids:
        tlids.remove('-1')
    tlids = tuple(tlids)
    tls = dbm.read_tllight(tlids)

    roads = dbm.read_road_from_ic(icids)

    outputs = dbm.read_output('test')

    # 원래라면 generator 내에서 처리하는 것이 맞지만, 흐름 확인을 위해 따로 처리
    leafs, sources, sinks = dbm.read_virtual_ic_road(icids)

    road_ids = []
    source_ids = []
    sink_ids = []
    for road in roads:
        road_ids.append(road.id)
    for source in sources:
        source_ids.append(source.id)
    for sink in sinks:
        sink_ids.append(sink.id)

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

    # 원래라면 생성 버튼을 누름과 동시에 뒤에서 처리되는 것이 맞지만, 흐름 확인을 위해 따로 처리
    sumogen.add_leaf_element(leafs, sources, sinks)

    # sumogen.generate_addition_file('C:/Users/FILAB/Desktop/arrange/5_code/SUMO/sumo_DT/test_folder/test_1.add.xml',
    #                                'test_1')

    test_file = 'test3_full'

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
    # sumogen.generate_random_route_file(f'{test_file}.net.xml', f'{test_file}.rou.xml', end=110,
    #                             seed=77, period=0.1, fringe_factor=2)

    simul_run = 2

    for tt in range(10, 12, 1):
        for td in range(5, 31, 1):
            if td in [1, 2, 3, 10, 24]:
                continue

            base_time = datetime.datetime(2023, 4, td, tt, 0, 0)
            t_step = 1
            if road_ids:
                road_traffic = dbm.read_road_traffic(road_ids, base_time=base_time, time_step=t_step)
            else:
                road_traffic = []
            source_traffic = dbm.read_road_traffic(source_ids, base_time=base_time, time_step=t_step)
            sink_traffic = dbm.read_road_traffic(sink_ids, base_time=base_time, time_step=t_step)

            if road_traffic:
                sumogen.set_road_traffic(road_traffic, 'between')
            sumogen.set_road_traffic(source_traffic, 'source')
            sumogen.set_road_traffic(sink_traffic, 'sink')

            fb = 0
            bb = 0
            interval = 3600  # 사용은 분단위로 변경됨
            sumogen.generate_route_file(f'result_3_full_folder/{test_file}_{td}_{tt}_route.rou.xml',
                                        f'result_3_full_folder/{test_file}_{td}_{tt}_flow.rou.xml',
                                        f'{test_file}_detector.xml',
                                        f'result_3_full_folder/{test_file}_{td}_{tt}_traffic.txt',
                                        front_buffer=fb, back_buffer=bb, interval=interval, repeat=500)

            # sumocfg 구성
            # sumogen.make_sumocfg(f'{test_file}.sumocfg', 0, 10000)
            sumogen.make_sumocfg(f'{test_file}_{td}_{tt}.sumocfg',
                                0, (t_step+fb+bb)*interval+1,
                                summary_path=f'result_3_full_folder/{test_file}_{td}_{tt}_summary.xml', summary_period=3600,
                                edge_path=f'result_3_full_folder/{test_file}_{td}_{tt}.add.xml', edge_period=3600)

            result = subprocess.call(f'python C:/Users/FILAB/anaconda3/envs/sumo/Lib/site-packages/sumo/tools/runSeeds.py -a sumo -k {test_file}_{td}_{tt}.sumocfg --seeds 1:101 --threads 12')
            # sumogen.run_sumo(f'{test_file}_{td}_{tt}_{i}.sumocfg')

    print('finish')
