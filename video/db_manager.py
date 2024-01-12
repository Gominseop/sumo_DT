import time
import json
from datetime import datetime
from db_client import DBClient
from element import SideNode, TLPhase, ICNode, Road, TLLogic


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
            re = self.read_query(f'SELECT * FROM traffic_light WHERE id = {tlid}')
        elif type(tlid) == tuple or type(tlid) == list:
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
            re = self.read_query(f'SELECT * FROM intersection WHERE id = {icid}')
        elif type(icid) == tuple or type(icid) == list:
            re = self.read_query(f'SELECT * FROM intersection WHERE id in {tuple(icid)}')
        else:
            raise TypeError('type of id must be str or tuple:str or tuple:str')
        # 받은 정보를 위의 변수 class에 맞게 변경하여 return하는 것이 좋을 듯

        icnodes = []
        for r in re:
            icnode = ICNode(r[0], r[2], r[3], r[5], r[1], r[4], r[6])
            sides = self.read_query(f'SELECT * FROM intersection_side WHERE ic_id = {icnode.id}')
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
        self.commit()

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
            re = self.read_query(f'SELECT * FROM road WHERE id = {rid}')
        elif type(rid) == tuple or type(rid) == list:
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
            re = self.read_query(f'SELECT * FROM road WHERE `node1_id` IN {tuple(icid)} AND `node2_id` IN {tuple(icid)}')
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


if __name__ == '__main__':
    dbm = DBManager()
    dbm.initialize_db(
        'localhost',
        3306,
        'root',
        'filab1020',
        'brl',
        'utf8'
    )

    phases = TLPhase(3)
    phases.append(60, "GGR")
    phases.append(6, "YYR")
    phases.append(30, "RRG")
    phases.append(6, "RRY")
    dbm.add_tllight('0', 'tll1', 'static', 0, 3, phases)

    phases = TLPhase(4)
    phases.append(45, "GRRR")
    phases.append(6, "YRRR")
    phases.append(45, "RGRR")
    phases.append(6, "RYRR")
    phases.append(45, "RRGR")
    phases.append(6, "RRYR")
    phases.append(45, "RRRG")
    phases.append(6, "RRRY")
    dbm.add_tllight('1', 'tll1', 'static', 0, 4, phases)

    phases = TLPhase(3)
    phases.append(60, "GRG")
    phases.append(6, "YRY")
    phases.append(30, "RGR")
    phases.append(6, "RYR")
    dbm.add_tllight('2', 'tll2', 'static', 0, 3, phases)

    phases = TLPhase(4)
    phases.append(45, "RRRG")
    phases.append(6, "RRRY")
    phases.append(45, "GRRR")
    phases.append(6, "YRRR")
    phases.append(45, "RGRR")
    phases.append(6, "RYRR")
    phases.append(45, "RRGR")
    phases.append(6, "RRYR")
    dbm.add_tllight('3', 'tll3', 'static', 0, 4, phases)

    phases = TLPhase(4)
    phases.append(45, "RRRG")
    phases.append(6, "RRRY")
    phases.append(45, "GRRR")
    phases.append(6, "YRRR")
    phases.append(45, "RGRR")
    phases.append(6, "RYRR")
    phases.append(45, "RRGR")
    phases.append(6, "RRYR")
    dbm.add_tllight('4', 'tll4', 'static', 0, 4, phases)

    #phases.show()
    #print(phases.tlphase)

    #dbm.add_tllight('6', 'tll1', 'static', 0, 3, phases)
    #dbm.read_tllight('0')
    #dbm.add_intersection()
    #dbm._add_intersection_side('0', 1, [a])
    side = []
    side.append(SideNode('0', 50.0, 100.0, 2, 2, 50, 'RS,SL'))
    side.append(SideNode('1', 100.0, 50.0, 2, 2, 50, 'RS,SL'))
    side.append(SideNode('2', 0.0, 50.0, 2, 2, 50, 'RS,SL'))
    #dbm.add_intersection('1', 'sub', 50.0, 50.0, shape=3, side_points=side, tlLogic='5')
    #dbm.set_tl_in_intersection('0', '0')
    r = Road('r2', 'road1', ('0', '1'), ('1', '2'), 2, 2, 50.0, 100.0)
    # dbm.add_road(r)
    # 'priority', 'traffic_light', 'traffic_light_right_on_red' node type
