import json
from datetime import time, datetime, timedelta


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
        # e.g. [[R0,S0,L0],[R0,S0]]
        # e.g. R0,S0,L0;R0,S0
        if type(routes) == list or type(routes) == tuple:
            if not self._check_route_num(routes):
                raise ValueError('entryLineNum != route num')
            tr = []
            for route in routes:
                tr.append(','.join(route))
            routes = ';'.join(tr)
        elif type(routes) == str:
            if not self._check_route_num(routes.split(';')):
                raise ValueError('entryLineNum != route num')
        else:
            raise ValueError('routes type must be str or list or tuple')
        self.route = routes


class Road:
    def __init__(self, rid, name, side1, side2, laneNum, speed, length, available):
        self.id = rid
        self.name = name
        self.side1 = side1  # (icID, sID)
        self.side2 = side2  # (icID, sID)
        self.laneNum = laneNum
        self.speed = speed
        self.length = length
        self.available = available

    def show(self):
        print(f"id: {self.id}")
        print(f"name: {self.name}")
        print(f"side1: {self.side1}")
        print(f"side2: {self.side2}")
        print(f"laneNum: {self.laneNum}")
        print(f"speed: {self.speed}")
        print(f"length: {self.length}")
        print(f"available: {self.available}")


class TLPhase:
    """
    phase: R r L g G Y 중 하나를 shape만큼 사용
    """
    def __init__(self, shape=4, phases=None):
        # phases is None or dict
        self.shape = shape
        self.phases = []
        if phases is not None:
            for phase in phases.values():
                self.phases.append(phase)

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
        return tmp

    def _check_state(self, state):
        if self.shape != len(state):
            print('Value Error: tllight shape != state length')
            return False
        for c in state:
            if c not in ['R', 'r', 'L', 'l', 'g', 'G', 'Y', 'y', 'B', 'b']:
                print("Value Error: tllight state enum('R', 'r', 'L', 'l', 'g', 'G', 'Y', 'y', 'B', 'b')")
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

# 확장
class TLLogic:
    # TL program
    def __init__(self, tid, programID, tltype, offset, shape, phases, period=None):
        self.tl_id = tid
        self.programID = programID
        self.type = tltype
        self.offset = offset
        self.shape = shape
        self.phases = phases
        self.period = 0
        if period is None:
            for phase in phases.tlphase().values():
                self.period += phase["duration"]
        else:
            self.period = period

    def show(self):
        print('id: ', self.id)
        print('programID: ', self.programID)
        print('type: ', self.type)
        print('offset: ', self.offset)
        print('shape: ', self.shape)
        print('phases: ', self.phases)
        print('period: ', self.period)


class TLPlan:
    def __init__(self, plan_id, time_set=None):
        self.id = plan_id
        self.time_set = []
        if time_set is not None:
            for ts in time_set:
                # if ts[0] is str:
                #     self.time_set.append([datetime.strptime(ts[0], '%H:%M:%S').time(), ts[1]])
                self.time_set.append(ts)

    def show(self):
        print('plan_id: ', self.id)
        for i, ts in enumerate(self.time_set):
            print(f'{ts[0]}: {ts[1]}')
        return self.id, self.time_set

    @property
    def tlplans(self):
        tmp = dict()
        self.time_set.sort(key=lambda x: x[0])
        for i, v in enumerate(self.time_set):
            tmp[v[0]] = v[1]
        return tmp

    def append(self, from_time, program_id):
        # if from_time is str:
        #     self.time_set.append([datetime.strptime(from_time, '%H:%M:%S').time(), program_id])
        self.time_set.append([from_time, program_id])

    def pop(self):
        self.time_set.pop()

    def insert(self, position, from_time, program_id):
        # if from_time is str:
        #     target = [time.strptime(from_time, '%H:%M:%S'), program_id]
        self.time_set.insert(position, [from_time, program_id])

    def remove(self, from_time, program_id):
        self.time_set.remove([from_time, program_id])


class TLLight:
    def __init__(self, tid, shape, plan, plan_list, program_list, yellow=4, all_red=0):
        self.id = tid
        self.shape = shape
        self.plan = plan
        self.plan_list = plan_list
        self.program = None
        self.program_list = program_list
        self.yellow = yellow
        self.all_red = all_red

    def show(self):
        print('id: ', self.id)
        print('shape: ', self.shape)
        print('plan: ', self.plan)
        print('plan_list: ', self.plan_list)
        print('program: ', self.program)
        print('program_list: ', self.program_list)
        print('yellow: ', self.yellow)
        print('all_red: ', self.all_red)


class Parameter:
    def __init__(self):
        self.params = dict()
        self.params_base = dict()

    def add_param_base(self, param_name, param_type):
        self.params_base[param_name] = param_type
        return True

    def add_params_base(self, param_names, param_types):
        if len(param_names) != len(param_types):
            return False
        check = True
        for n, t in zip(param_names, param_types):
            if not self.add_param_base(n, t):
                check
        return check

    def delete_param_base(self, param_name):
        if param_name in self.params_base:
            del(self.params_base[param_name])
            return True
        else:
            return False

    def delete_params_base(self, param_names):
        check = True
        for n in param_names:
            if not self.delete_param_base(n):
                check = False
        return check

    def add_param(self, param_name, param_value, dummy=False):
        if param_name not in self.params_base:
            print('error: param_name')
            return False
        if not dummy and type(param_value) != self.params_base[param_name]:
            if type(param_value) in {tuple, list} and type(self.params_base[param_name]) == list:
                for i in param_value:
                    if type(i) != self.params_base[param_name][0]:
                        print(f'error: value type, "{i}" is not "{str(self.params_base[param_name][0])}" list')
                        return False
            else:
                print(f'error: param_type, "{param_value}" is not "{str(self.params_base[param_name])}"')
                return False
        self.params[param_name] = param_value
        return True

    def add_params(self, param_names, param_values, dummy=False):
        if len(param_names) != len(param_values):
            return False
        check = True
        for n, v in zip(param_names, param_values):
            if not self.add_param(n, v, dummy):
                check = False
        return check

    def delete_param(self, param_name):
        if param_name in self.params:
            del(self.params[param_name])
            return True
        else:
            return False

    def delete_params(self, param_names):
        check = True
        for n in param_names:
            if not self.delete_param(n):
                check = False
        return check

    def clear_param(self):
        self.params = dict()

    def print_param(self):
        print(self.params)

    def print_param_base(self):
        print(self.params)


class EdgeParameter(Parameter):
    def __init__(self, mid, file_name, period=None, begin=None, end=None, exclude_empty=None,
                 with_internal=None, max_travel_time=None, min_samples=None, speed_threshold=None, vtypes=None,
                 track_vehicles=None, detect_persons=None, write_attributes=None, edges=None, edges_file=None,
                 aggregate=None):
        super(EdgeParameter, self).__init__()
        self.n = ['id', 'file', 'period', 'begin', 'end', 'excludeEmpty', 'withInternal', 'maxTraveltime', 'minSamples',
             'speedThreshold', 'vTypes', 'trackVehicles', 'detectPersons', 'writeAttributes', 'edges', 'edgesFile',
             'aggregate']
        self.t = [str, str, int, int, int, str, bool, float, float, float, str, bool, [str], [str], [str], str, bool]
        self.add_params_base(self.n, self.t)

        #self._id = None
        self.id = mid
        self.file = file_name
        self.period = period
        self.begin = begin
        self.end = end
        self.excludeEmpty = exclude_empty
        self.withInternal = with_internal
        self.maxTraveltime = max_travel_time
        self.minSamples = min_samples
        self.speedThreshold = speed_threshold
        self.vTypes = vtypes
        self.trackVehicles = track_vehicles
        self.detectPersons = detect_persons
        self.writeAttributes = write_attributes
        self.edges = edges
        self.edgesFile = edges_file
        self.aggregate = aggregate

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, v):
        if not (v is None or self.add_param('id', v)):
            raise ValueError("Invalid type")
        self._id = v

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, v):
        if not (v is None or self.add_param('file', v)):
            raise ValueError("Invalid type")
        self._file = v

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, v):
        if not (v is None or self.add_param('period', v)):
            raise ValueError("Invalid type")
        self._period = v

    @property
    def begin(self):
        return self._begin

    @begin.setter
    def begin(self, v):
        if not (v is None or self.add_param('begin', v)):
            raise ValueError("Invalid type")
        self._begin = v

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, v):
        if not (v is None or self.add_param('end', v)):
            raise ValueError("Invalid type")
        self._end = v

    @property
    def excludeEmpty(self):
        return self._excludeEmpty

    @excludeEmpty.setter
    def excludeEmpty(self, v):
        if not (v is None or self.add_param('excludeEmpty', v)):
            raise ValueError("Invalid type")
        self._excludeEmpty = v

    @property
    def withInternal(self):
        return self._withInternal

    @withInternal.setter
    def withInternal(self, v):
        if not (v is None or self.add_param('withInternal', v)):
            raise ValueError("Invalid type")
        self._withInternal = v

    @property
    def maxTraveltime(self):
        return self._maxTraveltime

    @maxTraveltime.setter
    def maxTraveltime(self, v):
        if not (v is None or self.add_param('maxTraveltime', v)):
            raise ValueError("Invalid type")
        self._maxTraveltime = v

    @property
    def minSamples(self):
        return self._minSamples

    @minSamples.setter
    def minSamples(self, v):
        if not (v is None or self.add_param('minSamples', v)):
            raise ValueError("Invalid type")
        self._minSamples = v

    @property
    def speedThreshold(self):
        return self._speedThreshold

    @speedThreshold.setter
    def speedThreshold(self, v):
        if not (v is None or self.add_param('speedThreshold', v)):
            raise ValueError("Invalid type")
        self._speedThreshold = v

    @property
    def vTypes(self):
        return self._vTypes

    @vTypes.setter
    def vTypes(self, v):
        if not (v is None or self.add_param('vTypes', v)):
            raise ValueError("Invalid type")
        self._vTypes = v

    @property
    def trackVehicles(self):
        return self._trackVehicles

    @trackVehicles.setter
    def trackVehicles(self, v):
        if not (v is None or self.add_param('trackVehicles', v)):
            raise ValueError("Invalid type")
        self._trackVehicles = v

    @property
    def detectPersons(self):
        return self._detectPersons

    @detectPersons.setter
    def detectPersons(self, v):
        if not (v is None or self.add_param('detectPersons', v)):
            raise ValueError("Invalid type")
        self._detectPersons = v

    @property
    def writeAttributes(self):
        return self._writeAttributes

    @writeAttributes.setter
    def writeAttributes(self, v):
        if not (v is None or self.add_param('writeAttributes', v)):
            raise ValueError("Invalid type")
        self._writeAttributes = v

    @property
    def edges(self):
        return self._edges

    @edges.setter
    def edges(self, v):
        if not (v is None or self.add_param('edges', v)):
            raise ValueError("Invalid type")
        self._edges = v

    @property
    def edgesFile(self):
        return self._edgesFile

    @edgesFile.setter
    def edgesFile(self, v):
        if not (v is None or self.add_param('edgesFile', v)):
            raise ValueError("Invalid type")
        self._edgesFile = v

    @property
    def aggregate(self):
        return self._aggregate

    @aggregate.setter
    def aggregate(self, v):
        if not (v is None or self.add_param('aggregate', v)):
            raise ValueError("Invalid type")
        self._aggregate = v

    def edgeParameter_to_dict(self):
        jd = dict()
        if self.id is not None:
            jd['id'] = self.id
        if self.file is not None:
            jd['file'] = self.file
        if self.period is not None:
            jd['period'] = self.period
        if self.begin is not None:
            jd['begin'] = self.begin
        if self.end is not None:
            jd['end'] = self.end
        if self.excludeEmpty is not None:
            jd['excludeEmpty'] = self.excludeEmpty
        if self.withInternal is not None:
            jd['withInternal'] = self.withInternal
        if self.maxTraveltime is not None:
            jd['maxTraveltime'] = self.maxTraveltime
        if self.minSamples is not None:
            jd['minSamples'] = self.minSamples
        if self.speedThreshold is not None:
            jd['speedThreshold'] = self.speedThreshold
        if self.vTypes is not None:
            jd['vTypes'] = self.vTypes
        if self.trackVehicles is not None:
            jd['trackVehicles'] = self.trackVehicles
        if self.detectPersons is not None:
            jd['detectPersons'] = self.detectPersons
        if self.writeAttributes is not None:
            jd['writeAttributes'] = self.writeAttributes
        if self.edges is not None:
            jd['edges'] = self.edges
        if self.edgesFile is not None:
            jd['edgesFile'] = self.edgesFile
        if self.aggregate is not None:
            jd['aggregate'] = self.aggregate
        return jd

    def dict_to_edgeParameter(self, value):
        if 'id' in value and value['id'] is not None:
            self.id = value['id']
        if 'file' in value and value['file'] is not None:
            self.file = value['file']
        if 'period' in value and value['period'] is not None:
            self.period = value['period']
        if 'begin' in value and value['begin'] is not None:
            self.begin = value['begin']
        if 'end' in value and value['end'] is not None:
            self.end = value['end']
        if 'excludeEmpty' in value and value['excludeEmpty'] is not None:
            self.excludeEmpty = value['excludeEmpty']
        if 'withInternal' in value and value['withInternal'] is not None:
            self.withInternal = value['withInternal']
        if 'maxTraveltime' in value and value['maxTraveltime'] is not None:
            self.maxTraveltime = value['maxTraveltime']
        if 'minSamples' in value and value['minSamples'] is not None:
            self.minSamples = value['minSamples']
        if 'speedThreshold' in value and value['speedThreshold'] is not None:
            self.speedThreshold = value['speedThreshold']
        if 'vTypes' in value and value['vTypes'] is not None:
            self.vTypes = value['vTypes']
        if 'trackVehicles' in value and value['trackVehicles'] is not None:
            self.trackVehicles = value['trackVehicles']
        if 'detectPersons' in value and value['detectPersons'] is not None:
            self.detectPersons = value['detectPersons']
        if 'writeAttributes' in value and value['writeAttributes'] is not None:
            self.writeAttributes = value['writeAttributes']
        if 'edges' in value and value['edges'] is not None:
            self.edges = value['edges']
        if 'edgesFile' in value and value['edgesFile'] is not None:
            self.edgesFile = value['edgesFile']
        if 'aggregate' in value and value['aggregate'] is not None:
            self.aggregate = value['aggregate']


class Output:
    def __init__(self, oid, file_base_name, target, period=None, edge_params=None, tllogics=None, tls_type=None):
        self.oid = oid
        self.file_base_name = file_base_name
        self.target = target
        self.period = period
        self.edge_params = edge_params
        self.tllogics = tllogics
        self.tls_type = tls_type

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, v):
        if type(v) == set:
            tmp = v - {'summary', 'queue', 'edge', 'lane', 'tllight'}
            if len(tmp) != 0:
                raise ValueError("target can be subset of {'summary', 'queue', 'edge', 'lane', 'tllight'}")
            self._target = v
        elif v is None:
            self._target = v
        else:
            raise TypeError("target(set) can be subset of {'summary', 'queue', 'edge', 'lane', 'tllight'}")

    @property
    def edge_params(self):
        return self._edge_params

    @edge_params.setter
    def edge_params(self, v):
        if type(v) == EdgeParameter or v is None:
            self._edge_params = v
        else:
            raise TypeError('type of edge_params must be EdgeParameter')

    @property
    def tls_type(self):
        return self._tls_type

    @tls_type.setter
    def tls_type(self, v):
        if type(v) == set:
            tmp = v - {'SaveTLSStates', 'SaveTLSSwitchTimes', 'SaveTLSSwitchStates', 'SaveTLSProgram'}
            if len(tmp) != 0:
                raise ValueError("target can be subset of "
                                 "{'SaveTLSStates', 'SaveTLSSwitchTimes', 'SaveTLSSwitchStates', 'SaveTLSProgram'}")
            self._tls_type = v
        elif v is None:
            self._tls_type = v
        else:
            raise ValueError("tls_type can be one of {'SaveTLSStates', 'SaveTLSSwitchTimes', 'SaveTLSSwitchStates', "
                             "'SaveTLSProgram'}")

    def show(self):
        print('id: ', self.oid)
        print('file_base_name: ', self.file_base_name)
        print('target: ', self.target)
        print('period: ', self.period)
        print('edge_params: ', self.edge_params)
        print('tllogics: ', self.tllogics)
        print('tls_type: ', self.tls_type)


if __name__ == '__main__':
    ep = EdgeParameter(mid='test', file_name='test_test', end=3600)
    print(ep.id)
    oo = Output('test', 'file', {'summary', 'queue', 'edge'}, period=100, edge_params=ep)
    print('ss')