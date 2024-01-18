import time
import json
from datetime import datetime
from utils.db_client import DBClient
from utils.element import SideNode, TLPhase, ICNode, Road, TLLogic, EdgeParameter, Output


def check_db_setting(func):
    def inner(*args, **kwargs):
        if args[0].conn:
            return func(*args, **kwargs)
        else:
            print('db 연결 필요')
    return inner


class DBManager(DBClient):
    def __init__(self):
        super().__init__()

    def initialize_db(self, host, port, user, password, db, charset):
        self.initialize(host, port, user, password, db, charset)

    @check_db_setting
    def set_db(self):
        self._create_intersection()
        self._create_intersection_side()
        self._create_road()
        self._create_traffic()
        self._create_traffic_light()

    def _create_intersection(self):
        col = dict()
        col['id'] = ['string', 'NOT NULL']
        col['name'] = ['string', 'NOT NULL']
        col['x'] = ['float', 'NULL']
        col['y'] = ['float', 'NULL']
        col['type'] = ['string', 'NOT NULL']
        col['shape'] = ['int', 'NOT NULL']
        col['tlLogic'] = ['string', 'NULL']
        key = dict()
        key['id'] = 'primary'
        self.create_table('intersection', col, key)

    def _create_intersection_side(self):
        col = dict()
        col['ic_id'] = ['string', 'NOT NULL']
        col['side_id'] = ['string', 'NOT NULL']
        col['x'] = ['float', 'NULL']
        col['y'] = ['float', 'NULL']
        col['entryLaneNum'] = ['int', 'NULL']
        col['exitLaneNum'] = ['int', 'NULL']
        col['speed'] = ['float', 'NULL']
        col['length'] = ['float', 'NULL']
        col['route'] = ['string', 'NULL']
        key = dict()
        key['ic_id'] = 'primary'
        key['side_id'] = 'primary'
        self.create_table('intersection_side', col, key)

    def _create_road(self):
        col = dict()
        col['id'] = ['string', 'NOT NULL']
        col['name'] = ['string', 'NULL']
        col['node1_id'] = ['string', 'NOT NULL']
        col['node1_index'] = ['string', 'NOT NULL']
        col['node2_id'] = ['string', 'NULL']
        col['node2_index'] = ['string', 'NULL']
        col['laneNum12'] = ['int', 'NOT NULL']
        col['laneNum21'] = ['int', 'NOT NULL']
        col['speed'] = ['float', 'NOT NULL']
        col['length'] = ['float', 'NOT NULL']
        key = dict()
        key['ic_id'] = 'primary'
        self.create_table('intersection_side', col, key)

    def _create_traffic(self):
        pass

    def _create_traffic_light(self):
        sql = """
        CREATE TABLE `traffic_light` (
        `id` VARCHAR(50) NOT NULL DEFAULT '' COLLATE 'utf8mb4_general_ci',
        `programID` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
        `type` VARCHAR(50) NOT NULL DEFAULT '0' COLLATE 'utf8mb4_general_ci',
        `offset` INT(11) NOT NULL DEFAULT '0',
        `shape` INT(11) NOT NULL,
        `phases` LONGTEXT NOT NULL COLLATE 'utf8mb4_bin',
        PRIMARY KEY (`id`) USING BTREE,
        CONSTRAINT `phases` CHECK (json_valid(`phases`))
        )
        COLLATE='utf8mb4_general_ci'
        ENGINE=InnoDB;
        """
        self.write_query(sql, True)

    @check_db_setting
    def read_tllight(self, tlid):
        """
        read_tllight
        :param tlid: (str) or (tuple:str) or (list:str)
        :return:
        """
        if type(tlid) == str:
            re = self.read_query(f"SELECT * FROM traffic_light WHERE id = '{tlid}'")
        elif type(tlid) == tuple or type(tlid) == list:
            if len(tlid) == 1:
                re = self.read_query(f"SELECT * FROM traffic_light WHERE id = '{tlid[0]}'")
            else:
                re = self.read_query(f'SELECT * FROM traffic_light WHERE id in {tuple(tlid)}')
        else:
            raise TypeError('type of id must be str or tuple:str or tuple:str')
        # 받은 정보를 위의 변수 class에 맞게 변경하여 return하는 것이 좋을 듯

        tllogics = []
        for r in re:
            tllogics.append(TLLogic(r[0], r[1], r[2], r[3], r[4], json.loads(r[5])))
        print(f'tllight - traffic logic {tlid} 읽어오기 성공')
        return tllogics

    @check_db_setting
    def add_tllight(self, tlID=None, programID='tll_id', tl_type='static', offset=0, shape=None, phases=None):
        """
        add_tllight
        :param tlID: (str) tllight id
        :param programID: (str) tllight program id
        :param tl_type: (enum) static, actuated, delay_based
        :param offset: (int) offset from origin traffic light
        :param shape: (int) traffic light shape and structure (beta)
        :param phases: (TLPhase) traffic logic
        :return:
        """
        if shape != phases.shape:
            raise ValueError("shape != phases length")
        if type(phases) != TLPhase:
            raise TypeError("phases's type is not TLPhase")

        sql = f"""
        INSERT INTO traffic_light(`id`, `programID`, `type`, `offset`, `shape`, `phases`) 
        VALUES ('{str(tlID)}', '{str(programID)}', '{str(tl_type)}', {int(offset)}, {int(shape)}, '{phases.tlphase}')
        """
        self.write_query(sql, True)
        print(f'tllight - traffic logic {tlID} 추가 성공')
        return True

    @check_db_setting
    def read_intersection(self, icid):
        """
        read_tllight
        :param icid: (str) or (tuple:str) or (list:str)
        :return:
        """
        if type(icid) == str:
            re = self.read_query(f"SELECT * FROM intersection WHERE id = '{icid}'")
        elif type(icid) == tuple or type(icid) == list:
            if len(icid) == 1:
                re = self.read_query(f"SELECT * FROM intersection WHERE id = '{icid[0]}'")
            else:
                re = self.read_query(f'SELECT * FROM intersection WHERE id in {tuple(icid)}')
        else:
            raise TypeError('type of id must be str or tuple:str or tuple:str')
        # 받은 정보를 위의 변수 class에 맞게 변경하여 return하는 것이 좋을 듯

        icnodes = []
        for r in re:
            icnode = ICNode(r[0], r[2], r[3], r[5], r[1], r[4], r[6])
            sides = self.read_query(f"SELECT * FROM intersection_side WHERE ic_id = '{icnode.id}'")
            for s in sides:
                icnode.add_side_info(SideNode(s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8], s[9]))
            icnodes.append(icnode)
        print(f'intersection - intersection node {icid}와 그 side 읽어오기 성공')
        return tuple(icnodes)

    @check_db_setting
    def add_intersection(self, icID=None, name='ic_name', x=0.0, y=0.0, type='traffic_light_right_on_red',
                         shape=4, side_points=None, tlLogic=None):
        self._add_intersection_node(icID, name, x, y, type, shape)
        self._add_intersection_side(icID, shape, side_points)
        if tlLogic:
            self.set_tl_in_intersection(icID, tlLogic, shape)
        # self.commit()

    def _add_intersection_node(self, icID, name, x, y, type, shape):
        if type not in ['priority', 'traffic_light', 'traffic_light_right_on_red']:
            raise ValueError("type value must be in ['priority', 'traffic_light', 'traffic_light_right_on_red']")

        sql = f"""
        INSERT INTO intersection(`id`, `name`, `x`, `y`, `type`, `shape`)
        VALUES('{icID}', '{name}', {x}, {y}, '{type}', {shape})
        """
        self.write_query(sql)
        print(f"intersection - intersection node '{icID}' 추가 성공")

    def _add_intersection_side(self, icID, side_num, side_points):
        """
        _add_intersection_side
        :param icID: (str) id
        :param side_num: (int)
        :param side_points: (list:Side_Node)
        :return:
        """
        if side_num != len(side_points):
            raise ValueError('way_num != way_points')

        side_ids = []
        values = []
        for point in side_points:
            values.append(f"('{icID}', '{point.id}', {point.x}, {point.y}, {point.entryLaneNum}, "
                          f"{point.exitLaneNum}, {point.speed}, {point.length}, '{point.route}', '{point.rslu}')")
            side_ids.append((icID, point.id))
        sql = f"""
        INSERT INTO intersection_side(`ic_id`, `side_id`, `x`, `y`, `entryLaneNum`, `exitLaneNum`, `speed`, 
        `length`, `route`, `rslu`) 
        VALUES {", ".join(values)}
        """
        self.write_query(sql)
        print(f"intersection_side - intersection '{icID}'의 intersection_side 추가 성공")
        return side_ids

    def _shape_check(self, table, id):
        sql = f"SELECT shape FROM {table} WHERE `id`='{id}'"
        rsp = self.read_query(sql)
        if rsp:
            rsp = rsp[0][0]
        else:
            rsp = 0
        return rsp

    def _ic_shape_check(self, icID):
        return self._shape_check('intersection', icID)

    def _tl_shape_check(self, tlID):
        return self._shape_check('traffic_light', tlID)

    @check_db_setting
    def set_tl_in_intersection(self, icID, tlID, icshape=0):
        # ic shape == tl shape 가 중요
        tl_shape = self._tl_shape_check(tlID)
        if not tl_shape:
            raise ValueError('Unregistered tlID')

        ic_shape = icshape if icshape else self._ic_shape_check(icID)
        if not ic_shape:
            raise ValueError('Unregistered icID')
        if tl_shape != ic_shape:
            raise ValueError('ic shape != tl shape')

        sql = f"UPDATE intersection SET `tlLogic`='{tlID}' WHERE `id`='{icID}'"
        self.write_query(sql)
        return ic_shape, icID, tlID

    @check_db_setting
    def read_road_from_id(self, rid):
        """
        read_tllight
        :param rid: (str) or (tuple:str) or (list:str)
        :return:
        """
        if type(rid) == str:
            re = self.read_query(f"SELECT * FROM road WHERE id = '{rid}'")
        elif type(rid) == tuple or type(rid) == list:
            if len(rid) == 1:
                re = self.read_query(f"SELECT * FROM road WHERE id = '{rid[0]}'")
            else:
                re = self.read_query(f'SELECT * FROM road WHERE id in {tuple(rid)}')
        else:
            raise TypeError('type of id must be str or tuple:str or tuple:str')
        # 받은 정보를 위의 변수 class에 맞게 변경하여 return하는 것이 좋을 듯

        roads = []
        for r in re:
            roads.append(Road(r[0], r[1], (r[2], r[3]), (r[4], r[5]), r[6], r[7], r[8], r[9]))
        print(f'road - road edge {rid} 읽어오기 성공')
        return roads

    @check_db_setting
    def read_road_from_ic(self, icid):
        """
        read_tllight
        :param icid: (tuple:str) or (list:str)
        :return:
        """
        if type(icid) == tuple or type(icid) == list:
            if len(icid) == 1:
                re = self.read_query(
                    f"SELECT * FROM road WHERE `node1_id` IN ('{icid[0]}') AND `node2_id` IN ('{icid[0]}')")
            else:
                re = self.read_query(
                    f"SELECT * FROM road WHERE `node1_id` IN {tuple(icid)} AND `node2_id` IN {tuple(icid)}")
        else:
            raise TypeError('type of id must be tuple:str or tuple:str')
        # 받은 정보를 위의 변수 class에 맞게 변경하여 return하는 것이 좋을 듯

        roads = []
        for r in re:
            roads.append(Road(r[0], r[1], (r[2], r[3]), (r[4], r[5]), r[6], r[7], r[8], r[9]))
        print(f'road - {icid}를 연결하는 road edge 읽어오기 성공')
        return roads

    @check_db_setting
    def add_road(self, road_id, name, ic1, ic1_side, ic2, ic2_side, laneNum12, laneNum21, speed, length):
        """
        add load
        :param road_id: (str)
        :param name: (str)
        :param ic1: (str) way랑 합칠지 말지?
        :param ic1_side: (str)
        :param ic2: (str)
        :param ic2_side: (str)
        :param laneNum12:
        :param laneNum21:
        :param speed:
        :param length:
        :return:
        """
        road = Road(road_id, name, (ic1, ic1_side), (ic2, ic2_side), laneNum12, laneNum21, speed, length)
        self._add_road(road)

    @check_db_setting
    def add_road(self, road):
        """
        add load
        :param road: (Road)
        :return:
        """
        self._add_road(road)

    def _side_exist_check(self, side):
        sql = f"""
        SELECT EXISTS (SELECT 1 FROM intersection_side WHERE `ic_id`='{side[0]}' AND `side_id`='{side[1]}') AS CNT
        """
        return self.read_query(sql)

    def _add_road(self, road):
        # side node에 icid도 들어가야 관리가 쉬울것 같다
        # ic node 만들면 내부에 변수로 side node도 넣자
        
        # side는 1대1 대응이고 한번 사용한 것을 사용할 수 없으므로 road에 해당 side가 존재하는 확인이 필요하다
        
        if not self._side_exist_check(road.side1):
            raise ValueError('side1 is not exist')

        if None in road.side2:
            sql = f"""
            INSERT INTO road(`id`, `name`, `node1_id`, `node1_index`, `laneNum12`, `laneNum21`, `speed`, `length`) 
            VALUES('{road.id}', '{road.name}', '{road.side1[0]}', '{road.side1[1]}', {road.laneNum12}, {road.laneNum21},
            {road.speed}, {road.length})
            """
        else:
            if not self._side_exist_check(road.side2):
                raise ValueError('side2 is not exist')
            sql = f"""
            INSERT INTO road(`id`, `name`, `node1_id`, `node1_index`, `node2_id`, `node2_index`, 
            `laneNum12`, `laneNum21`, `speed`, `length`)
             VALUES('{road.id}', '{road.name}', '{road.side1[0]}', '{road.side1[1]}', '{road.side2[0]}', 
            '{road.side2[1]}', {road.laneNum12}, {road.laneNum21}, {road.speed}, {road.length})
            """
        self.write_query(sql, True)
        print(f"road - road relation '{road.id}' 추가 성공")
        return road.id

    @check_db_setting
    def add_traffic(self):
        # 내용물이 정해지는 대로 설정
        pass

    @check_db_setting
    def read_output(self, oid):
        """
        read_output
        :param oid: (str) or (tuple:str) or (list:str)
        :return:
        """
        if type(oid) == str:
            re = self.read_query(f"SELECT * FROM output WHERE `id` = '{oid}'")
        elif type(oid) == tuple or type(oid) == list:
            if len(oid) == 1:
                re = self.read_query(f"SELECT * FROM output WHERE `id` = '{oid[0]}'")
            else:
                re = self.read_query(f'SELECT * FROM output WHERE `id` in {tuple(oid)}')
        else:
            raise TypeError('type of id must be str or tuple:str or tuple:str')
        # 받은 정보를 위의 변수 class에 맞게 변경하여 return하는 것이 좋을 듯

        outputs = []
        for r in re:
            tmp_ep = EdgeParameter('tmp', 'tmp')
            tmp_ep.dict_to_edgeParameter(json.loads(r[4]))
            outputs.append(Output(r[0], r[1], set(r[2].split(',')), r[3], tmp_ep, r[5], set(r[6].split(','))))
            # outputs.append()
        print(f'output - output setting {oid} 읽어오기 성공')
        return outputs

    @check_db_setting
    def add_output(self, oid, file_based_name, target, period=None, edge_params=None, tllogics=None, tls_type=None):
        """
        add output
        :param oid: (str)
        :param file_based_name: (str)
        :param target: (set:str) {'summary','queue','edge','lane','tllight'}
        :param period: (int)
        :param edge_params: (EdgeParameter)
        :param tllogics: (str)
        :param tls_type: (set:str) {'SaveTLLStates','SaveTLLSwitchTimes','SaveTLLSwitchStates','SaveTLLProgram'}
        :return:
        """
        output = Output(oid, file_based_name, target, period, edge_params, tllogics, tls_type)
        self._add_output(output)

    @check_db_setting
    def add_output(self, output):
        """
        add output
        :param output: (Output)
        :return:
        """
        self._add_output(output)

    def _add_output(self, output):
        # none이면 안넣고 아니면 넣고

        target = str(output.target).replace(' ', '').replace("'", '')[1:-1]

        p = ['', '']
        if output.period is not None:
            p[0] = f', `period`'
            p[1] = f', {output.period}'
        ep = ['', '']
        if output.edge_params is not None:
            ep[0] = f', `edge_params`'
            edge_dict = output.edge_params.edgeParameter_to_dict()
            edge_json = json.dumps(edge_dict)
            ep[1] = f", '{edge_json}'"
        t = ['', '']
        if output.tllogics is not None:
            t[0] = f', `tllogics`'
            t[1] = f", '{output.tllogics}'"
        tt = ['', '']
        if output.tls_type is not None:
            tt[0] = f', `tls_type`'
            tt[1] = f""", '{str(output.tls_type).replace(' ', '').replace("'", '')[1:-1]}'"""

        sql = f"""
        INSERT INTO output(`id`, `file_base_name`, `target`{p[0]}{ep[0]}{t[0]}{tt[0]}) 
        VALUES('{output.oid}', '{output.file_base_name}', '{target}'{p[1]}{ep[1]}{t[1]}{tt[1]})
        """

        self.write_query(sql)
        print(f"output - output setting '{output.oid}' 추가 성공")
        return output.oid

    @check_db_setting
    def add_result(self, oid, results):
        """
        add result
        :param oid: (str)
        :param outputs: (dict) from SUMOGenerator's output_paths
        :return:
        """
        t = datetime.now()
        self._add_result(t, oid, results['summary'], results['queue'], results['edge'],
                         results['lane'], results['tls'])
        return oid

    def _add_result(self, timestamp, oid, summary, queue, edge, lane, tllight):
        """
        add result
        :param timestamp: (datetime)
        :param oid: (str)
        :param summary: (str) path
        :param queue: (str) path
        :param edge: (str) path
        :param lane: (str) path
        :param tllight: (dict:str:str) path
        :return:
        """

        s = ['', '']
        if summary != '':
            s[0] = f', `summary`'
            s[1] = f", '{summary}'"
        q = ['', '']
        if queue != '':
            q[0] = f', `queue`'
            q[1] = f", '{queue}'"
        e = ['', '']
        if edge != '':
            e[0] = f', `edge`'
            e[1] = f", '{edge}'"
        l = ['', '']
        if lane != '':
            l[0] = f', `lane`'
            l[1] = f", '{lane}'"
        tl = ['', '']
        if type(tllight) == dict:
            tl[0] = f', `tllight`'
            tl[1] = f", '{json.dumps(tllight)}'"

        sql = f"""
        INSERT INTO result(`timestamp`, `output_id`{s[0]}{q[0]}{e[0]}{l[0]}{tl[0]}) 
        VALUES('{timestamp}', '{oid}'{s[1]}{q[1]}{e[1]}{l[1]}{tl[1]})
        """
        self.write_query(sql)
        print(f"result - '{oid}' result 추가 성공")


if __name__ == '__main__':
    dbm = DBManager()
    dbm.initialize_db(
        '127.0.0.1',
        3306,
        'root',
        'filab1020',
        'filab_traffic',
        'utf8'
    )

    # u turn을 대상 차선의 가장 왼쪽으로 변경 할것
    # side = []
    # side.append(SideNode('0', 49.07469852, -9.574652225, 3, 2, 30, 50, 'S,S,L', '-1,2,1,0'))
    # side.append(SideNode('1', -9.574652225, -49.07469852, 1, 1, 30, 50, 'R', '0,-1,-1,1'))
    # side.append(SideNode('2', -49.07469852, 9.574652225, 2, 2, 30, 50, 'RS,S', '1,0,-1,2'))
    # dbm.add_intersection(f'3500059800', f'리라유치원앞교차로', 674.7659, -102.9688, shape=3, side_points=side)
    # dbm.commit()

    tlids = ['3500006301', '3500006600', '3500006650', '3500006660', '3500006700',
             '3500006901', '3500007100', '3500007300', '3500007350', '3500007500',
             '3500007700', '3500007900', '3500008000', '3500051802', '3500051804',
             '3500058500', '3500058550', '3500058700', '3500058900', '3500059300',
             '3500059350', '3500059800', '3500059850', '3500060100', '3500060600',
             '3500060650', '3500060660', '3500060800', '3500060850', '3500060860',
             '3500062100', '3500062500', '3500062550', '3500065800', '3500065850',
             '3500302300', '3510000200', '3510000250', '3510000300', '3510000400',
             '3510021200', '3510021250', '3510021300', '3510021350', '3510021400',
             '3510021500', '3510021700']

    case = 1
    for tlid in tlids:
        if case == 0:
            dbm.set_tl_in_intersection(tlid, tlid)
        elif case == 1:
            dbm.set_tl_in_intersection(tlid, tlid + '_1')
        elif case == 2:
            dbm.set_tl_in_intersection(tlid, tlid + '_2')
        elif case == 3:
            dbm.set_tl_in_intersection(tlid, tlid + '_3')
    dbm.commit()

    # node1 = 3500302300
    # node2 = 3500007100
    # road_id12 = 3500302300
    # road_id21 = 3500007100
    # road_name = '중흥로'
    # speed = 60
    # length = (308.2049065 - 100)*(1/1)
    # lanenum12 = 3
    # lanenum21 = 3
    # r = Road(f"{road_id12}-{road_id21}", road_name, (str(node1), 0), (str(node2), 2),
    #          lanenum12, lanenum21, speed, length)
    # dbm.add_road(r)

    #ep = EdgeParameter(mid='test', file_name='test_test', end=3600, period=100)
    #oo = Output('test', 'output_test', {'summary', 'queue', 'edge', 'tllight'}, period=100, edge_params=ep,
    #            tllogics='test_tll_00', tls_type={'SaveTLLSwitchTimes', 'SaveTLLSwitchStates'})
    # dbm.add_output(oo)
    # dbm.commit()
    #a = dbm.read_output('test')

    # tl light 추가
    # phases = TLPhase(5)
    # phases.append(40, "RRgRg")
    # phases.append(4, "RRYRY")
    # phases.append(25, "RRLRL")
    # phases.append(4, "RRrRr")
    # phases.append(25, "GRRRR")
    # phases.append(4, "YRRRR")
    # phases.append(25, "RGRRR")
    # phases.append(4, "RYRRR")
    # phases.append(25, "RRRGR")
    # phases.append(4, "RRRYR")

    # dbm.add_tllight('10', 'program_10', 'static', 0, 5, phases)
    # dbm.commit()

    """
    def test_case():
        phases = TLPhase(4)
        phases.append(40, "GRRR")
        phases.append(4, "YRRR")
        phases.append(40, "RGRR")
        phases.append(4, "RYRR")
        phases.append(40, "RRGR")
        phases.append(4, "RRYR")
        phases.append(40, "RRRG")
        phases.append(4, "RRRY")

        for i in range(10):
            for j in range(10):
                x_center = (i+1)*100.0
                y_center = (j+1)*100.0

                dbm.add_tllight(f'test_tll_{i}{j}', f'tll_test_{i}{j}', 'static', 4*(i+j), 4, phases)

                side = []
                side.append(SideNode('0', 0, 25.0, 2, 2, 25, 50, 'RS,SL', '3,2,1,0'))
                side.append(SideNode('1', 25.0, 0, 2, 2, 25, 50, 'RS,SL', '0,3,2,1'))
                side.append(SideNode('2', 0, -25.0, 2, 2, 25, 50, 'RS,SL', '1,0,3,2'))
                side.append(SideNode('3', -25.0, 0, 2, 2, 25, 50, 'RS,SL', '2,1,0,3'))

                dbm.add_intersection(f'test_{i}{j}', f'intersection_{i}{j}', x_center, y_center, shape=4,
                                     side_points=side, tlLogic=f'test_tll_{i}{j}')

                if i-1 >= 0:
                    r = Road(f'r{i-1}{j}-{i}{j}', f'road{i-1}{j}-{i}{j}', (f'test_{i-1}{j}', 1), (f'test_{i}{j}', 3),
                             2, 2, 60.0, 100.0)
                    dbm.add_road(r)
                if j-1 >= 0:
                    r = Road(f'r{i}{j-1}-{i}{j}', f'road{i}{j-1}-{i}{j}', (f'test_{i}{j-1}', 0), (f'test_{i}{j}', 2),
                             2, 2, 60.0, 100.0)
                    dbm.add_road(r)
    """

    # 'priority', 'traffic_light', 'traffic_light_right_on_red' node type
