import json


class NodePoint:
    def __init__(self, id, x, y):
        self.id = id
        self.x = 0.0
        self.y = 0.0
        self.set_point(x, y)

    @property
    def point(self):
        return self.x, self.y

    def set_point(self, x, y):
        self.x = x
        self.y = y


class ICNode(NodePoint):
    def __init__(self, icid, x, y, shape, name="ic", ictype="traffic_light_right_on_red", tlLogic=None):
        self.id = icid
        self.name = name
        self.x = x
        self.y = y
        self.type = ictype
        self.shape = shape
        self.tlLogic = tlLogic if tlLogic else "-1"
        self.sides = dict()

    def show(self):
        print('name: ', self.name)
        print('x: ', self.x)
        print('y: ', self.y)
        print('type: ', self.type)
        print('shape: ', self.shape)
        print('tlLogic: ', self.tlLogic)
        print('sides: ', self.sides)

    def set_tlLogic(self, tlID):
        self.tlLogic = tlID

    def add_side_info(self, sidenode):
        self.sides[sidenode.id] = sidenode

    def remove_side_info(self, sidenode):
        del(self.sides[sidenode.id])


class SideNode(NodePoint):
    """
    id: (str)
    x: (float)
    y: (float)
    entryLaneNum: (int)
    exitLaneNum: (int)
    speed: (float)
    length: (float)
    route: (str) or (list:str) - R, S, L, U로 구성된 문자열
    """
    def __init__(self, id, x, y, entryLaneNum=None, exitLaneNum=None, speed=None, length=None, route=None, rslu=None):
        super().__init__(id, x, y)
        self.entryLaneNum = 0
        self.exitLaneNum = 0
        self.speed = 0.0
        self.length = 0.0
        self.route = ''
        self.set_line_num(entryLaneNum if entryLaneNum else 0, exitLaneNum if exitLaneNum else 0)
        self.set_road_speed(speed if speed else 0.0)
        self.set_road_length(length if length else 0.0)
        if route:
            self.set_route(route)
        self.rslu = rslu

    def show(self):
        print(self.id, self.x, self.y, self.entryLaneNum, self.exitLaneNum, self.length, self.route, self.rslu)

    def _check_route_num(self, routes):
        # routes: list
        return self.entryLaneNum == len(routes)

    def set_line_num(self, entry_num, exit_num):
        self.entryLaneNum = entry_num
        self.exitLaneNum = exit_num

    def set_road_speed(self, speed):
        self.speed = speed

    def set_road_length(self, length):
        self.length = length

    def set_route(self, routes):
        # 가장 오른쪽 차선부터 순서대로 list로 받음
        # (str) R-right, S-Stright, L-Left, U-Uturn, RSLU 순서
        # e.g. RSL, RS
        if type(routes) == list or type(routes) == tuple:
            if not self._check_route_num(routes):
                raise ValueError('entryLineNum != route num')
            routes = ','.join(routes)
        elif type(routes) == str:
            if not self._check_route_num(routes.split(',')):
                raise ValueError('entryLineNum != route num')
        else:
            raise ValueError('routes type must be str or list or tuple')
        self.route = routes


class Road:
    def __init__(self, rid, name, side1, side2, laneNum12, laneNum21, speed, length):
        self.id = rid
        self.name = name
        self.side1 = side1  # (icID, sID)
        self.side2 = side2  # (icID, sID)
        self.laneNum12 = laneNum12
        self.laneNum21 = laneNum21
        self.speed = speed
        self.length = length

    def show(self):
        print(f"id: {self.id}")
        print(f"name: {self.name}")
        print(f"side1: {self.side1}")
        print(f"side2: {self.side2}")
        print(f"laneNum12: {self.laneNum12}")
        print(f"laneNum21: {self.laneNum21}")
        print(f"speed: {self.speed}")
        print(f"length: {self.length}")


class TLPhase:
    """
    phase: R r L g G Y 중 하나를 shape만큼 사용
    """
    def __init__(self, shape=4):
        self.shape = shape
        self.phases = []

    def show(self):
        print('shape: ', self.shape)
        for i, phase in enumerate(self.phases):
            print(f'{i}: {self.phases[i]}')
        return self.shape, self.phases

    @property
    def tlphase(self):
        tmp = dict()
        for i, v in enumerate(self.phases):
            tmp[str(i)] = v
        return json.dumps(tmp)

    def _check_state(self, state):
        if self.shape != len(state):
            print('Value Error: tllight shape != state length')
            return False
        for c in state:
            if c not in ['R', 'r', 'L', 'g', 'G', 'Y']:
                print("Value Error: tllight state enum('R', 'r', 'L', 'g', 'G', 'Y')")
                return False
        return True

    def append(self, duration, state):
        self._check_state(state)
        self.phases.append({"duration": duration, "state": state})

    def pop(self):
        self.phases.pop()

    def insert(self, position, duration, state):
        self.phases.insert(position, {"duration": duration, "state": state})

    def remove(self, duration, state):
        self.phases.remove({"duration": duration, "state": state})


class TLLogic:
    def __init__(self, tid, programID, tltype, offset, shape, phases):
        self.id = tid
        self.programID = programID
        self.type = tltype
        self.offset = offset
        self.shape = shape
        self.phases = phases

    def show(self):
        print('id: ', self.id)
        print('programID: ', self.programID)
        print('type: ', self.type)
        print('offset: ', self.offset)
        print('shape: ', self.shape)
        print('phases: ', self.phases)
