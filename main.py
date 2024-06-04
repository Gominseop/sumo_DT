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

        if 'SUMO_HOME' in os.environ:
            sys.path.append(os.environ['SUMO_HOME'])

        QtCore.QCoreApplication.setOrganizationName("minseop")

        self.settings = QtCore.QSettings()

        self.dbm = None
        self.sumogen = None
        self.nodes = []
        self.output_name = ''

        self.roads = {}

        self.ui.button_db.clicked.connect(self.db_connect)
        self.ui.button_target.clicked.connect(self.data_load)
        self.ui.button_node.clicked.connect(self.node_generate)
        self.ui.button_edge.clicked.connect(self.edge_generate)
        self.ui.button_connection.clicked.connect(self.connection_generate)
        self.ui.button_tllogic.clicked.connect(self.tllogic_generate)
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
            user='root',
            password='filab1020',
            db='filab_traffic',
            charset='utf8'
        )
        self.ui.output_log.append(f'{datetime.now()} : connect - database')

    def data_load(self):
        self.sumogen = SUMOGenerator()

        node_raw = self.ui.input_node_list.toPlainText()
        self.nodes = node_raw.split(' ')

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

        leafs, sources, sinks = self.dbm.read_virtual_ic_road(self.nodes)
        self.ui.output_log.append(f'{datetime.now()} : read - virtual intersections & roads')

        road_ids = []
        source_ids = []
        sink_ids = []
        for road in roads:
            road_ids.append(road.id)
        for source in sources:
            source_ids.append(source.id)
        for sink in sinks:
            sink_ids.append(sink.id)

        self.roads["road"] = road_ids
        self.roads["source"] = source_ids
        self.roads["sink"] = sink_ids

        self.sumogen.add_leaf_element(leafs, sources, sinks)

        self.ui.output_log.append(f'{datetime.now()} : set - sumo generator')

    def node_generate(self):
        self.output_name = self.ui.input_output_name.text()
        self.sumogen.generate_node_file(f'{self.output_name}.nod.xml')
        self.ui.output_log.append(f'{datetime.now()} : create - node file - {self.output_name}.nod.xml')

    def edge_generate(self):
        self.output_name = self.ui.input_output_name.text()
        self.sumogen.generate_edge_file(f'{self.output_name}.edg.xml')
        self.ui.output_log.append(f'{datetime.now()} : create - edge file - {self.output_name}.edg.xml')

    def connection_generate(self):
        self.output_name = self.ui.input_output_name.text()
        self.sumogen.generate_connection_file(f'{self.output_name}.con.xml')
        self.ui.output_log.append(f'{datetime.now()} : create - connection file - {self.output_name}.con.xml')

    def tllogic_generate(self):
        self.output_name = self.ui.input_output_name.text()
        self.sumogen.generate_tll_file(f'{self.output_name}.tll.xml')
        self.ui.output_log.append(f'{datetime.now()} : create - traffic light logic file - {self.output_name}.tll.xml')

    def network_generate(self):
        self.output_name = self.ui.input_output_name.text()
        node = self.ui.input_node.text()
        edge = self.ui.input_edge.text()
        connection = self.ui.input_connection.text()
        tllogic = self.ui.input_tllogic.text()

        # netccfg 구성
        netcfg = self.sumogen.make_netccfg(f'{self.output_name}.netccfg', f'{self.output_name}.net.xml',
                                           node, edge, connection, tllogic)
        self.ui.output_log.append(f'{datetime.now()} : create - network config file - netcfg')
        # net 구성
        network = self.sumogen.generate_net_file()
        self.ui.output_log.append(f'{datetime.now()} : create - network file - network')

    def route_generate(self):
        self.output_name = self.ui.input_output_name.text()

        base = self.ui.input_route_base.text()
        step = self.ui.input_route_step.text()
        front = self.ui.input_route_front.text()
        back = self.ui.input_route_back.text()
        repeat = self.ui.input_route_repeat.text()

        base_time = datetime.now()
        if base != "now":
            base_time = datetime.strptime(base, '%Y-%m-%d %H:%M:%S')

        if self.roads["road"]:
            road_traffic = self.dbm.read_road_traffic(self.roads["road"], base_time=base_time, time_step=int(step))
        else:
            road_traffic = []
        source_traffic = self.dbm.read_road_traffic(self.roads["source"], base_time=base_time, time_step=int(step))
        sink_traffic = self.dbm.read_road_traffic(self.roads["sink"], base_time=base_time, time_step=int(step))
        self.ui.output_log.append(f'{datetime.now()} : read - traffic flow')

        self.sumogen.set_road_traffic(road_traffic, 'between')
        self.sumogen.set_road_traffic(source_traffic, 'source')
        self.sumogen.set_road_traffic(sink_traffic, 'sink')
        self.ui.output_log.append(f'{datetime.now()} : set - traffic flow')

        self.sumogen.generate_route_file(f'{self.output_name}_route.rou.xml', f'{self.output_name}_flow.rou.xml',
                                         f'{self.output_name}_detector.xml', f'{self.output_name}_traffic.txt',
                                         front_buffer=int(front), back_buffer=int(back), interval=3600, repeat=int(repeat))

        self.ui.output_log.append(f'{datetime.now()} : create - route file - {self.output_name}.rou.xml')

    def sumocfg_generate(self):
        network = self.ui.input_network.text()
        rou = self.ui.input_route.text()

        summary = self.ui.input_sumo_summary.text()
        summary = f'{self.output_name}_summary.xml' if summary == 'True' else ''
        summary_period = self.ui.input_sumo_summary_period.text()
        queue = self.ui.input_sumo_queue.text()
        queue = f'{self.output_name}_queue.xml' if queue == 'True' else ''
        queue_period = self.ui.input_sumo_queue_period.text()
        edge = self.ui.input_sumo_edge.text()
        edge = f'{self.output_name}.add.xml' if edge == 'True' else ''
        edge_period = self.ui.input_sumo_edge_period.text()
        begin = self.ui.input_sumo_begin.text()
        end = self.ui.input_sumo_end.text()
        self.sumogen.make_sumocfg(f'{self.output_name}.sumocfg', int(begin), int(end)+1, network=network, route=rou,
                                  route_path=f'{self.output_name}.rou.xml',
                                  summary_path=summary, summary_period=summary_period,
                                  queue_path=queue, queue_period=queue_period,
                                  edge_path=edge, edge_period=edge_period)
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
