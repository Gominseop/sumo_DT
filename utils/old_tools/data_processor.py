import json
import sys
import numpy as np
sys.path.append('utils')
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, ElementTree
from element import SideNode, TLPhase, ICNode, Road, TLLogic, EdgeParameter, Output
from utils.sumo_xml import SUMOGenerator
from utils.db_manager import DBManager


class ResultSetting:
    def __init__(self, parameter_list):
        self.settings = dict()
        self.monitored_items = dict()
        self.parameter_list = parameter_list
        self.cut_type = ['lower', 'upper', 'both']
        self.monitor_type = ['range', 'match', 'in']

    def _check_threshold(self, target, cut_type, threshold):
        if target not in self.parameter_list:
            raise ValueError('target is not in available parameter list')
        if cut_type not in ['lower', 'upper', 'both']:
            raise ValueError('cut type must be one of lower, upper, both')
        if cut_type in ['lower', 'upper'] and type(threshold) not in [int, float]:
            raise TypeError('threshold must be int or float')
        if cut_type == 'both':
            if type(threshold) != list:
                raise TypeError('when cut type is both, threshold must be list')
            elif len(threshold) != 2:
                raise ValueError('when cut type is both, threshold must have two value')
            elif type(threshold[0]) not in [int, float] or type(threshold[1]) not in [int, float]:
                raise TypeError('each threshold must be int or float')

    def set_threshold(self, target, cut_type, threshold):
        self._check_threshold(target, cut_type, threshold)
        thres = [-np.inf, np.inf]
        if cut_type == 'lower':
            thres[0] = np.float(threshold)
        elif cut_type == 'upper':
            thres[1] = np.float(threshold)
        elif cut_type == 'both':
            thres[0] = np.float(threshold[0])
            thres[1] = np.float(threshold[1])
        self.settings[target] = {'type': cut_type, 'threshold': thres}

    def del_threshold(self, target):
        if target not in self.settings:
            raise ValueError('target is not in settings')
        del(self.settings[target])

    def _check_monitored_item(self, target, monitor_type, value):
        if target not in self.parameter_list:
            raise ValueError('target is not in available parameter list')
        if monitor_type not in ['range', 'match', 'in']:
            raise ValueError('monitor type must be one of range, match, in')
        if monitor_type == 'range':
            if type(value) not in [list, tuple]:
                raise TypeError('when monitor type is range, value must be list or tuple')
            if len(value) != 2:
                raise ValueError('when monitor type is range, value must have two value')
        if monitor_type == 'in':
            if type(value) not in [list, tuple, set]:
                raise TypeError('when monitor type is range, value must be list or tuple or set')

    def set_monitored_item(self, target, monitor_type, value):
        self._check_monitored_item(target, monitor_type, value)
        if target not in self.parameter_list:
            raise ValueError('target is not in available parameter list')
        self.monitored_items[target] = {'type': monitor_type, 'value': value}

    def del_monitored_item(self, target):
        if target not in self.monitored_items:
            raise ValueError('target is not in monitored_items')
        del(self.monitored_items[target])


class SummaryResultSetting(ResultSetting):
    def __init__(self):
        super(SummaryResultSetting, self).__init__(
            ['time', 'loaded', 'inserted', 'running', 'waiting', 'ended', 'arrived', 'collisions', 'teleports',
             'halting', 'stopped', 'meanWaitingTime', 'meanTravelTime', 'meanSpeed', 'meanSpeedRelative', 'duration']
        )


class QueueResultSetting(ResultSetting):
    def __init__(self):
        super(QueueResultSetting, self).__init__(
            ['timestep', 'id', 'queueing_time', 'queueing_length', 'queueing_length_experimental']
        )


class EdgeResultSetting(ResultSetting):
    def __init__(self):
        super(EdgeResultSetting, self).__init__(
            ['begin', 'end', 'id', 'traveltime', 'overlapTraveltime', 'density', 'laneDensity', 'occupancy',
             'waitingTime', 'timeLoss', 'speed', 'speedRelative', 'departed', 'arrived', 'entered', 'left',
             'laneChangedFrom', 'laneChangedTo']
        )


class LineResultSetting(ResultSetting):
    def __init__(self):
        super(LineResultSetting, self).__init__(
            ['begin', 'end', 'edge_id', 'lane_id', 'sampledSeconds', 'traveltime', 'overlapTraveltime', 'density',
             'laneDensity', 'occupancy', 'waitingTime', 'timeLoss', 'speed', 'speedRelative', 'departed', 'arrived',
             'entered', 'left', 'laneChangedFrom', 'laneChangedTo']
        )


class TllightResultSetting(ResultSetting):
    def __init__(self, category='TLSSwitchStates'):
        # if category == 'TLSStates':
        name_list = ['time', 'id', 'programID', 'phase', 'state']
        if category == 'TLSSwitchTimes':
            name_list = ['id', 'programID', 'fromLane', 'toLane', 'begin', 'end', 'duration']
        if category == 'TLSSwitchStates':
            name_list = ['time', 'id', 'programID', 'phase', 'state']
        if category == 'TLSProgram':
            name_list = ['id', 'type', 'programID', 'duration', 'state']
        super(TllightResultSetting, self).__init__(name_list)


class ResultProcessor:
    def __init__(self):
        self.result_file = ''
        self.result_setting = '' # setting 형태의 파일
        pass

    def xml2csv(self):
        # 이미 있는 모듈 사용해도 좋아~
        pass

    def result_check(self, file_type, file_path, setting):
        # file에서 자동ㅇ
        pass

    def queue_alarm(self):
        pass

    def summary_alarm(self):
        pass

    # 각 result에 대해서 어떻게 처리할지 고려
    # 특정 대상에 대해 일정 값을 넘으면 반응하는 형식
    # parameter: {type: [upper, lower, both], threshold: }



if __name__ == '__main__':
    print('data processor')
    print(np.inf > 5)
