# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\nn-use-cases\cv_filling_line_monitor\src\ui_main.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(640, 480)
        #MainWindow.setStyleSheet("background-color:#FFFFFF;  ")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
#         self.l_video_1 = QtWidgets.QLabel(self.centralwidget)
#         self.l_video_1.setStyleSheet("border: 1px solid #C0C0C0;  \n"
# #"background-color:#FFFFFF;  \n"
# "border-style: solid;  \n"
# "border-radius:0px;  \n"
# "")
#         self.l_video_1.setObjectName("l_video_1")
        #self.gridLayout.addWidget(self.l_video_1, 0, 2, 1, 1)
        self.l_video_0 = QtWidgets.QLabel(self.centralwidget)
        self.l_video_0.setStyleSheet("border: 1px solid #C0C0C0;  \n"
#"background-color:#FFFFFF;  \n"
"border-style: solid;  \n"
"border-radius:0px;  \n"
"")
        self.l_video_0.setObjectName("l_video_0")
        self.gridLayout.addWidget(self.l_video_0, 0, 1, 1, 1)
        self.graph_statistics = QChartView()
        self.graph_statistics.setMaximumSize(QtCore.QSize(16777215, 120))
        self.graph_statistics.setObjectName("graph_statistics")
        self.gridLayout.addWidget(self.graph_statistics, 1, 0, 1, 2)
        self.toolBox = QtWidgets.QToolBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolBox.sizePolicy().hasHeightForWidth())
        self.toolBox.setSizePolicy(sizePolicy)
        self.toolBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.toolBox.setStyleSheet(
        #"background-color:#FFFFFF;  \n"
"border-style: solid;  \n"
"border-radius:0px;  \n"
"")
        self.toolBox.setObjectName("toolBox")
        self.page_l70_sweat = QtWidgets.QWidget()
        self.page_l70_sweat.setGeometry(QtCore.QRect(0, 0, 200, 189))
        self.page_l70_sweat.setObjectName("page_l70_sweat")
        self.toolBox.addItem(self.page_l70_sweat, "")
        self.page_l71_sweat = QtWidgets.QWidget()
        self.page_l71_sweat.setGeometry(QtCore.QRect(0, 0, 200, 189))
        self.page_l71_sweat.setObjectName("page_l71_sweat")
        self.toolBox.addItem(self.page_l71_sweat, "")
        self.gridLayout.addWidget(self.toolBox, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 22))
        self.menubar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.menuFile.setObjectName("menuFile")
        self.menuDetection = QtWidgets.QMenu(self.menubar)
        self.menuDetection.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.menuDetection.setObjectName("menuDetection")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.menuFile.addAction(self.actionQuit)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuDetection.menuAction())
        self.retranslateUi(MainWindow)
        self.toolBox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Aseptic Behavior Monitor"))
        #self.l_video_1.setText(_translate("MainWindow", "video_1"))
        self.l_video_0.setText(_translate("MainWindow", "video_0"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_l70_sweat), _translate("MainWindow", "L70 Green"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_l71_sweat), _translate("MainWindow", "L71 Green"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuDetection.setTitle(_translate("MainWindow", "Detection"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
