# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainui.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(617, 998)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.button_db = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.button_db.setFont(font)
        self.button_db.setObjectName("button_db")
        self.verticalLayout_2.addWidget(self.button_db)
        self.frame_node = QtWidgets.QFrame(self.centralwidget)
        self.frame_node.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_node.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_node.setObjectName("frame_node")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_node)
        self.verticalLayout.setObjectName("verticalLayout")
        self.text_node_list = QtWidgets.QLabel(self.frame_node)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.text_node_list.setFont(font)
        self.text_node_list.setTextFormat(QtCore.Qt.RichText)
        self.text_node_list.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.text_node_list.setObjectName("text_node_list")
        self.verticalLayout.addWidget(self.text_node_list)
        self.input_node_list = QtWidgets.QTextEdit(self.frame_node)
        self.input_node_list.setObjectName("input_node_list")
        self.verticalLayout.addWidget(self.input_node_list)
        self.verticalLayout_2.addWidget(self.frame_node)
        self.frame_output = QtWidgets.QFrame(self.centralwidget)
        self.frame_output.setMaximumSize(QtCore.QSize(16777215, 66))
        self.frame_output.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_output.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_output.setObjectName("frame_output")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_output)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.text_output_name = QtWidgets.QLabel(self.frame_output)
        self.text_output_name.setMaximumSize(QtCore.QSize(16777215, 32))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.text_output_name.setFont(font)
        self.text_output_name.setAlignment(QtCore.Qt.AlignCenter)
        self.text_output_name.setObjectName("text_output_name")
        self.horizontalLayout.addWidget(self.text_output_name)
        self.input_output_name = QtWidgets.QLineEdit(self.frame_output)
        self.input_output_name.setObjectName("input_output_name")
        self.horizontalLayout.addWidget(self.input_output_name)
        self.verticalLayout_2.addWidget(self.frame_output)
        self.button_network = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.button_network.setFont(font)
        self.button_network.setObjectName("button_network")
        self.verticalLayout_2.addWidget(self.button_network)
        self.frame_route = QtWidgets.QFrame(self.centralwidget)
        self.frame_route.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_route.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_route.setObjectName("frame_route")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame_route)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.text_route_param = QtWidgets.QLabel(self.frame_route)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.text_route_param.setFont(font)
        self.text_route_param.setObjectName("text_route_param")
        self.verticalLayout_3.addWidget(self.text_route_param)
        self.frame_route_param = QtWidgets.QFrame(self.frame_route)
        self.frame_route_param.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frame_route_param.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_route_param.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_route_param.setObjectName("frame_route_param")
        self.gridLayout = QtWidgets.QGridLayout(self.frame_route_param)
        self.gridLayout.setObjectName("gridLayout")
        self.text_route_param1 = QtWidgets.QLabel(self.frame_route_param)
        self.text_route_param1.setMaximumSize(QtCore.QSize(16777215, 32))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.text_route_param1.setFont(font)
        self.text_route_param1.setAlignment(QtCore.Qt.AlignCenter)
        self.text_route_param1.setObjectName("text_route_param1")
        self.gridLayout.addWidget(self.text_route_param1, 0, 0, 1, 1)
        self.input_route_begin = QtWidgets.QLineEdit(self.frame_route_param)
        self.input_route_begin.setObjectName("input_route_begin")
        self.gridLayout.addWidget(self.input_route_begin, 0, 1, 1, 1)
        self.input_route_end = QtWidgets.QLineEdit(self.frame_route_param)
        self.input_route_end.setObjectName("input_route_end")
        self.gridLayout.addWidget(self.input_route_end, 0, 2, 1, 1)
        self.text_route_param2 = QtWidgets.QLabel(self.frame_route_param)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.text_route_param2.setFont(font)
        self.text_route_param2.setAlignment(QtCore.Qt.AlignCenter)
        self.text_route_param2.setObjectName("text_route_param2")
        self.gridLayout.addWidget(self.text_route_param2, 1, 0, 1, 1)
        self.input_route_rand = QtWidgets.QLineEdit(self.frame_route_param)
        self.input_route_rand.setObjectName("input_route_rand")
        self.gridLayout.addWidget(self.input_route_rand, 1, 1, 1, 1)
        self.input_route_seed = QtWidgets.QLineEdit(self.frame_route_param)
        self.input_route_seed.setObjectName("input_route_seed")
        self.gridLayout.addWidget(self.input_route_seed, 1, 2, 1, 1)
        self.text_route_param3 = QtWidgets.QLabel(self.frame_route_param)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.text_route_param3.setFont(font)
        self.text_route_param3.setAlignment(QtCore.Qt.AlignCenter)
        self.text_route_param3.setObjectName("text_route_param3")
        self.gridLayout.addWidget(self.text_route_param3, 2, 0, 1, 1)
        self.input_route_period = QtWidgets.QLineEdit(self.frame_route_param)
        self.input_route_period.setObjectName("input_route_period")
        self.gridLayout.addWidget(self.input_route_period, 2, 1, 1, 1)
        self.input_route_fringe = QtWidgets.QLineEdit(self.frame_route_param)
        self.input_route_fringe.setObjectName("input_route_fringe")
        self.gridLayout.addWidget(self.input_route_fringe, 2, 2, 1, 1)
        self.verticalLayout_3.addWidget(self.frame_route_param)
        self.verticalLayout_2.addWidget(self.frame_route)
        self.button_route = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.button_route.setFont(font)
        self.button_route.setObjectName("button_route")
        self.verticalLayout_2.addWidget(self.button_route)
        self.frame_sumo = QtWidgets.QFrame(self.centralwidget)
        self.frame_sumo.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_sumo.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_sumo.setObjectName("frame_sumo")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frame_sumo)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.text_sumo_param = QtWidgets.QLabel(self.frame_sumo)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.text_sumo_param.setFont(font)
        self.text_sumo_param.setObjectName("text_sumo_param")
        self.verticalLayout_4.addWidget(self.text_sumo_param)
        self.frame_sumo_param = QtWidgets.QFrame(self.frame_sumo)
        self.frame_sumo_param.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frame_sumo_param.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_sumo_param.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_sumo_param.setObjectName("frame_sumo_param")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame_sumo_param)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.input_sumo_summary = QtWidgets.QLineEdit(self.frame_sumo_param)
        self.input_sumo_summary.setObjectName("input_sumo_summary")
        self.gridLayout_2.addWidget(self.input_sumo_summary, 1, 1, 1, 1)
        self.text_sumo_param3 = QtWidgets.QLabel(self.frame_sumo_param)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.text_sumo_param3.setFont(font)
        self.text_sumo_param3.setAlignment(QtCore.Qt.AlignCenter)
        self.text_sumo_param3.setObjectName("text_sumo_param3")
        self.gridLayout_2.addWidget(self.text_sumo_param3, 3, 0, 1, 1)
        self.input_sumo_summary_period = QtWidgets.QLineEdit(self.frame_sumo_param)
        self.input_sumo_summary_period.setObjectName("input_sumo_summary_period")
        self.gridLayout_2.addWidget(self.input_sumo_summary_period, 1, 2, 1, 1)
        self.input_sumo_queue_period = QtWidgets.QLineEdit(self.frame_sumo_param)
        self.input_sumo_queue_period.setObjectName("input_sumo_queue_period")
        self.gridLayout_2.addWidget(self.input_sumo_queue_period, 2, 2, 1, 1)
        self.input_sumo_lane = QtWidgets.QLineEdit(self.frame_sumo_param)
        self.input_sumo_lane.setObjectName("input_sumo_lane")
        self.gridLayout_2.addWidget(self.input_sumo_lane, 3, 2, 1, 1)
        self.text_sumo_param2 = QtWidgets.QLabel(self.frame_sumo_param)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.text_sumo_param2.setFont(font)
        self.text_sumo_param2.setAlignment(QtCore.Qt.AlignCenter)
        self.text_sumo_param2.setObjectName("text_sumo_param2")
        self.gridLayout_2.addWidget(self.text_sumo_param2, 2, 0, 1, 1)
        self.input_sumo_queue = QtWidgets.QLineEdit(self.frame_sumo_param)
        self.input_sumo_queue.setObjectName("input_sumo_queue")
        self.gridLayout_2.addWidget(self.input_sumo_queue, 2, 1, 1, 1)
        self.text_sumo_param1 = QtWidgets.QLabel(self.frame_sumo_param)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.text_sumo_param1.setFont(font)
        self.text_sumo_param1.setAlignment(QtCore.Qt.AlignCenter)
        self.text_sumo_param1.setObjectName("text_sumo_param1")
        self.gridLayout_2.addWidget(self.text_sumo_param1, 1, 0, 1, 1)
        self.input_sumo_edge = QtWidgets.QLineEdit(self.frame_sumo_param)
        self.input_sumo_edge.setObjectName("input_sumo_edge")
        self.gridLayout_2.addWidget(self.input_sumo_edge, 3, 1, 1, 1)
        self.text_sumo_param4 = QtWidgets.QLabel(self.frame_sumo_param)
        self.text_sumo_param4.setMaximumSize(QtCore.QSize(16777215, 32))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.text_sumo_param4.setFont(font)
        self.text_sumo_param4.setMidLineWidth(0)
        self.text_sumo_param4.setAlignment(QtCore.Qt.AlignCenter)
        self.text_sumo_param4.setObjectName("text_sumo_param4")
        self.gridLayout_2.addWidget(self.text_sumo_param4, 4, 0, 1, 1)
        self.input_sumo_begin = QtWidgets.QLineEdit(self.frame_sumo_param)
        self.input_sumo_begin.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.input_sumo_begin.setObjectName("input_sumo_begin")
        self.gridLayout_2.addWidget(self.input_sumo_begin, 4, 1, 1, 1)
        self.input_sumo_end = QtWidgets.QLineEdit(self.frame_sumo_param)
        self.input_sumo_end.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.input_sumo_end.setObjectName("input_sumo_end")
        self.gridLayout_2.addWidget(self.input_sumo_end, 4, 2, 1, 1)
        self.verticalLayout_4.addWidget(self.frame_sumo_param)
        self.verticalLayout_2.addWidget(self.frame_sumo)
        self.button_sumo = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.button_sumo.setFont(font)
        self.button_sumo.setObjectName("button_sumo")
        self.verticalLayout_2.addWidget(self.button_sumo)
        self.frame_sumo_run = QtWidgets.QFrame(self.centralwidget)
        self.frame_sumo_run.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_sumo_run.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_sumo_run.setObjectName("frame_sumo_run")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_sumo_run)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.button_runsumo = QtWidgets.QPushButton(self.frame_sumo_run)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.button_runsumo.setFont(font)
        self.button_runsumo.setObjectName("button_runsumo")
        self.horizontalLayout_2.addWidget(self.button_runsumo)
        self.button_runsumo_gui = QtWidgets.QPushButton(self.frame_sumo_run)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.button_runsumo_gui.setFont(font)
        self.button_runsumo_gui.setObjectName("button_runsumo_gui")
        self.horizontalLayout_2.addWidget(self.button_runsumo_gui)
        self.verticalLayout_2.addWidget(self.frame_sumo_run)
        self.output_log = QtWidgets.QTextEdit(self.centralwidget)
        self.output_log.setObjectName("output_log")
        self.verticalLayout_2.addWidget(self.output_log)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 617, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.button_db.setText(_translate("MainWindow", "DB Connect"))
        self.text_node_list.setText(_translate("MainWindow", "Node List"))
        self.input_node_list.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Gulim\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">3500006301 3500006700 3500007500 3500007900 3500008000 3510000200 3510000250 3510000300 3510000400 3510000450 3510021700 3510021750 3510021500 3510021400 3500065800 3500065850 3500062500 3500062550 3510021350 3510021300 3510021200 3510021250 3500062100 3500060600 3500060650 3500060660 3500062400 3500060100 3500060800 3500058900 3500060850 3500060860 3500059350 3500058550 3500302300 3500051804 3500051802 3500007400 3500007100 3500006900 3500058700 3500006901 3500058500 3500006600 3500006650 3500006660 3500006800 3500007300 3500007350 3500059300 3500059800 3500059850</p></body></html>"))
        self.text_output_name.setText(_translate("MainWindow", "Output File Name"))
        self.input_output_name.setText(_translate("MainWindow", "test"))
        self.button_network.setText(_translate("MainWindow", "Generate Network"))
        self.text_route_param.setText(_translate("MainWindow", "Route Parameter (Random)"))
        self.text_route_param1.setText(_translate("MainWindow", "begin, end"))
        self.input_route_begin.setText(_translate("MainWindow", "0"))
        self.input_route_end.setText(_translate("MainWindow", "3600"))
        self.text_route_param2.setText(_translate("MainWindow", "rand, seed"))
        self.input_route_rand.setText(_translate("MainWindow", "False"))
        self.input_route_seed.setText(_translate("MainWindow", "77"))
        self.text_route_param3.setText(_translate("MainWindow", "period, fringe_factor"))
        self.input_route_period.setText(_translate("MainWindow", "0.5"))
        self.input_route_fringe.setText(_translate("MainWindow", "20"))
        self.button_route.setText(_translate("MainWindow", "Generate Route (Random)"))
        self.text_sumo_param.setText(_translate("MainWindow", "Sumo Parameter"))
        self.input_sumo_summary.setText(_translate("MainWindow", "True"))
        self.text_sumo_param3.setText(_translate("MainWindow", "edge, lane"))
        self.input_sumo_summary_period.setText(_translate("MainWindow", "100"))
        self.input_sumo_queue_period.setText(_translate("MainWindow", "100"))
        self.input_sumo_lane.setText(_translate("MainWindow", "False"))
        self.text_sumo_param2.setText(_translate("MainWindow", "queue, period"))
        self.input_sumo_queue.setText(_translate("MainWindow", "True"))
        self.text_sumo_param1.setText(_translate("MainWindow", "summary, period"))
        self.input_sumo_edge.setText(_translate("MainWindow", "True"))
        self.text_sumo_param4.setText(_translate("MainWindow", "begin, end"))
        self.input_sumo_begin.setText(_translate("MainWindow", "200"))
        self.input_sumo_end.setText(_translate("MainWindow", "3600"))
        self.button_sumo.setText(_translate("MainWindow", "Generate Sumocfg"))
        self.button_runsumo.setText(_translate("MainWindow", "Run Sumo"))
        self.button_runsumo_gui.setText(_translate("MainWindow", "Run Sumo GUI"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
