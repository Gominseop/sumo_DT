import sys
import os
import time
import logging

from datetime import datetime

from utils.db_manager import DBManager
from utils.sumo_xml import SUMOGenerator

from mainui import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets


class WindowClass(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        QtCore.QCoreApplication.setOrganizationName("minseop")

        self.settings = QtCore.QSettings()

        self.dbm = None
        self.sumogen = SUMOGenerator()
        self.nodes = []
        self.output_name = ''

        self.ui.button_db.clicked.connect(self.db_connect)
        self.ui.button_network.clicked.connect(self.network_generate)
        self.ui.button_route.clicked.connect(self.route_generate)
        self.ui.button_sumo.clicked.connect(self.sumocfg_generate)
        self.ui.button_runsumo.clicked.connect(self.sumo_run)
        self.ui.button_runsumo_gui.clicked.connect(self.sumogui_run)

    def __del__(self):
        pass

    def db_connect(self):
        self.dbm = DBManager()
        self.dbm.initialize_db(
            host='141.223.65.208',
            port=3306,
            user='guest_user',
            password='postechime',
            db='filab_traffic',
            charset='utf8'
        )
        self.ui.output_log.append(f'{datetime.now()} : connect - database')

    def network_generate(self):
        node_raw = self.ui.input_node_list.toPlainText()
        self.nodes = node_raw.split(' ')
        self.output_name = self.ui.input_output_name.text()

        ics = self.dbm.read_intersection(self.nodes)
        self.ui.output_log.append(f'{datetime.now()} : read - intersections')

        tlids = set([ic.tlLogic for ic in ics])
        if '-1' in tlids:
            tlids.remove('-1')
        tlids = tuple(tlids)
        tls = self.dbm.read_tllight(tlids)
        self.ui.output_log.append(f'{datetime.now()} : read - traffic light logics')

        roads = self.dbm.read_road_from_ic(self.nodes)
        self.ui.output_log.append(f'{datetime.now()} : read - roads')

        # generator 구성
        for ic in ics:
            self.sumogen.add_intersection_by_node(ic)
        for tl in tls:
            self.sumogen.add_tllogic_by_tl(tl)
        for road in roads:
            self.sumogen.add_road_by_edge(road)

        # 경로는 절대 경로로
        # node 구성
        self.sumogen.generate_node_file(f'{self.output_name}.nod.xml')
        self.ui.output_log.append(f'{datetime.now()} : create - node file - {self.output_name}.nod.xml')
        # edge 구성
        self.sumogen.generate_edge_file(f'{self.output_name}.edg.xml')
        self.ui.output_log.append(f'{datetime.now()} : create - edge file - {self.output_name}.edg.xml')
        # connection 구성
        self.sumogen.generate_connection_file(f'{self.output_name}.con.xml')
        self.ui.output_log.append(f'{datetime.now()} : create - connection file - {self.output_name}.con.xml')
        # tllight 구성
        self.sumogen.generate_tll_file(f'{self.output_name}.tll.xml')
        self.ui.output_log.append(f'{datetime.now()} : create - traffic light logic file - {self.output_name}.tll.xml')

        # netccfg 구성
        self.sumogen.make_netccfg(f'{self.output_name}.netccfg', f'{self.output_name}.net.xml')
        self.ui.output_log.append(f'{datetime.now()} : create - network config file - {self.output_name}.netccfg')
        # net 구성
        self.sumogen.generate_net_file()
        self.ui.output_log.append(f'{datetime.now()} : create - network file - {self.output_name}.net.xml')

    def route_generate(self):
        begin = self.ui.input_route_begin.text()
        end = self.ui.input_route_end.text()
        rand = self.ui.input_route_rand.text()
        rand = True if rand == 'True' else False
        seed = self.ui.input_route_seed.text()
        period = self.ui.input_route_period.text()
        fringe = self.ui.input_route_fringe.text()
        self.sumogen.generate_route_file(f'{self.output_name}.net.xml', f'{self.output_name}.rou.xml',
                                         begin=int(begin), end=int(end), rand=rand, seed=int(seed),
                                         period=float(period), fringe_factor=float(fringe))
        self.ui.output_log.append(f'{datetime.now()} : create - route file - {self.output_name}.rou.xml')

    def sumocfg_generate(self):
        summary = self.ui.input_sumo_summary.text()
        summary = f'{self.output_name}_summary.xml' if summary == 'True' else ''
        summary_period = self.ui.input_sumo_summary_period.text()
        queue = self.ui.input_sumo_queue.text()
        queue = f'{self.output_name}_queue.xml' if queue == 'True' else ''
        queue_period = self.ui.input_sumo_queue_period.text()
        edge = self.ui.input_sumo_edge.text()
        edge = f'{self.output_name}_edge.xml' if edge == 'True' else ''
        lane = self.ui.input_sumo_lane.text()
        lane = f'{self.output_name}_lane.xml' if lane == 'True' else ''
        begin = self.ui.input_sumo_begin.text()
        end = self.ui.input_sumo_end.text()
        self.sumogen.make_sumocfg(f'{self.output_name}.sumocfg', int(begin), int(end),
                                  route_path=f'{self.output_name}.rou.xml',
                                  summary_path=summary, summary_period=summary_period,
                                  queue_path=queue, queue_period=queue_period,
                                  edge_path=edge, lane_path=lane)
        self.ui.output_log.append(f'{datetime.now()} : create - sumocfg file - {self.output_name}.sumocfg')

    def sumo_run(self):
        self.ui.output_log.append(f'{datetime.now()} : start - sumocfg file - {self.output_name}.sumocfg')
        self.sumogen.run_sumo(f'{self.output_name}.sumocfg')
        self.ui.output_log.append(f'{datetime.now()} : end - sumocfg file - {self.output_name}.sumocfg')

    def sumogui_run(self):
        self.ui.output_log.append(f'{datetime.now()} : start - sumocfg file - {self.output_name}.sumocfg')
        self.sumogen.run_sumogui(f'{self.output_name}.sumocfg')
        self.ui.output_log.append(f'{datetime.now()} : end - sumocfg file - {self.output_name}.sumocfg')


def run_ui():
    app = QtWidgets.QApplication(sys.argv)
    ui_window = WindowClass()
    ui_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_ui()
