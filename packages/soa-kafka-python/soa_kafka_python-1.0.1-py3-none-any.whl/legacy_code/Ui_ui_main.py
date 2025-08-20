# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\nn-use-cases\cv_filling_line_monitor\src\ui_main.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(640, 480)
        MainWindow.setStyleSheet("background-color:#FFFFFF;  ")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.l_detection = QtWidgets.QLabel(self.centralwidget)
        self.l_detection.setStyleSheet("border: 1px solid #C0C0C0;  \n"
"background-color:#FFFFFF;  \n"
"border-style: solid;  \n"
"border-radius:0px;  \n"
"")
        self.l_detection.setObjectName("l_detection")
        self.gridLayout.addWidget(self.l_detection, 0, 2, 1, 1)
        self.l_video = QtWidgets.QLabel(self.centralwidget)
        self.l_video.setStyleSheet("border: 1px solid #C0C0C0;  \n"
"background-color:#FFFFFF;  \n"
"border-style: solid;  \n"
"border-radius:0px;  \n"
"")
        self.l_video.setObjectName("l_video")
        self.gridLayout.addWidget(self.l_video, 0, 1, 1, 1)
        self.graph_statistics = QtWidgets.QGraphicsView(self.centralwidget)
        self.graph_statistics.setMaximumSize(QtCore.QSize(16777215, 120))
        self.graph_statistics.setObjectName("graph_statistics")
        self.gridLayout.addWidget(self.graph_statistics, 1, 0, 1, 3)
        self.toolBox = QtWidgets.QToolBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolBox.sizePolicy().hasHeightForWidth())
        self.toolBox.setSizePolicy(sizePolicy)
        self.toolBox.setMaximumSize(QtCore.QSize(120, 16777215))
        self.toolBox.setStyleSheet("background-color:#FFFFFF;  \n"
"border-style: solid;  \n"
"border-radius:0px;  \n"
"")
        self.toolBox.setObjectName("toolBox")
        self.page_l70_needle = QtWidgets.QWidget()
        self.page_l70_needle.setGeometry(QtCore.QRect(0, 0, 120, 189))
        self.page_l70_needle.setObjectName("page_l70_needle")
        self.toolBox.addItem(self.page_l70_needle, "")
        self.page_l71_needle = QtWidgets.QWidget()
        self.page_l71_needle.setGeometry(QtCore.QRect(0, 0, 120, 189))
        self.page_l71_needle.setObjectName("page_l71_needle")
        self.toolBox.addItem(self.page_l71_needle, "")
        self.page_l70_rru_belt = QtWidgets.QWidget()
        self.page_l70_rru_belt.setGeometry(QtCore.QRect(0, 0, 120, 189))
        self.page_l70_rru_belt.setObjectName("page_l70_rru_belt")
        self.toolBox.addItem(self.page_l70_rru_belt, "")
        self.page_l71_rru_belt = QtWidgets.QWidget()
        self.page_l71_rru_belt.setGeometry(QtCore.QRect(0, 0, 120, 189))
        self.page_l71_rru_belt.setObjectName("page_l71_rru_belt")
        self.toolBox.addItem(self.page_l71_rru_belt, "")
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
        self.menuNeedle_Pop_Up = QtWidgets.QMenu(self.menuDetection)
        self.menuNeedle_Pop_Up.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.menuNeedle_Pop_Up.setObjectName("menuNeedle_Pop_Up")
        self.menuRRU_Fallen_Cartridge = QtWidgets.QMenu(self.menuDetection)
        self.menuRRU_Fallen_Cartridge.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.menuRRU_Fallen_Cartridge.setObjectName("menuRRU_Fallen_Cartridge")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.actionL70_1 = QtWidgets.QAction(MainWindow)
        self.actionL70_1.setCheckable(True)
        self.actionL70_1.setChecked(True)
        self.actionL70_1.setObjectName("actionL70_1")
        self.actionL71_1 = QtWidgets.QAction(MainWindow)
        self.actionL71_1.setCheckable(True)
        self.actionL71_1.setChecked(True)
        self.actionL71_1.setObjectName("actionL71_1")
        self.actionL70_2 = QtWidgets.QAction(MainWindow)
        self.actionL70_2.setCheckable(True)
        self.actionL70_2.setChecked(True)
        self.actionL70_2.setObjectName("actionL70_2")
        self.actionL71_2 = QtWidgets.QAction(MainWindow)
        self.actionL71_2.setCheckable(True)
        self.actionL71_2.setChecked(True)
        self.actionL71_2.setObjectName("actionL71_2")
        self.menuFile.addAction(self.actionQuit)
        self.menuNeedle_Pop_Up.addAction(self.actionL70_1)
        self.menuNeedle_Pop_Up.addAction(self.actionL71_1)
        self.menuRRU_Fallen_Cartridge.addAction(self.actionL70_2)
        self.menuRRU_Fallen_Cartridge.addAction(self.actionL71_2)
        self.menuDetection.addAction(self.menuNeedle_Pop_Up.menuAction())
        self.menuDetection.addAction(self.menuRRU_Fallen_Cartridge.menuAction())
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuDetection.menuAction())

        self.retranslateUi(MainWindow)
        self.toolBox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.l_detection.setText(_translate("MainWindow", "Detection"))
        self.l_video.setText(_translate("MainWindow", "Video"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_l70_needle), _translate("MainWindow", "L70 Needle"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_l71_needle), _translate("MainWindow", "L71 Needle"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_l70_rru_belt), _translate("MainWindow", "L70 RRU Belt"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_l71_rru_belt), _translate("MainWindow", "L71 RRU Belt"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuDetection.setTitle(_translate("MainWindow", "Detection"))
        self.menuNeedle_Pop_Up.setTitle(_translate("MainWindow", "Needle Pop Up"))
        self.menuRRU_Fallen_Cartridge.setTitle(_translate("MainWindow", "RRU Fallen Cartridge"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.actionL70_1.setText(_translate("MainWindow", "L70"))
        self.actionL71_1.setText(_translate("MainWindow", "L71"))
        self.actionL70_2.setText(_translate("MainWindow", "L70"))
        self.actionL71_2.setText(_translate("MainWindow", "L71"))

