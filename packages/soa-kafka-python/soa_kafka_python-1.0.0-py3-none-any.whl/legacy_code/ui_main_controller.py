'''
Descripttion: 
version: 
Author: Author
Date: 2023-07-03 08:56:35
LastEditors: Author
LastEditTime: 2023-10-18 14:52:43
'''
from PyQt5.QtWidgets import QApplication, QMainWindow,QGraphicsScene
from PyQt5.QtCore import QThread, pyqtSignal, Qt ,QDateTime, QDate, QTime,QTimer
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5 import QtCore
from ui_main import Ui_MainWindow
import sys
import cv2
import datetime, time
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis,QScatterSeries
import threading
from pathlib import Path
import json
from utils.db.data_access_manager import DataAccessManager
from failure_detection import FailureDetection
from entities.alarm import Alarm
import pandas as pd
import logging
from utils.dynamic_logger import DynamicLogger
from queue import Queue
from camera_manager import CameraManager
import time


class UI_Main_Controller(QMainWindow, Ui_MainWindow):
    __monitor_pool = []
    __camera_manager_list = []
    __l_video_width = 1080
    __l_video_height = 800
    
    def __init__(self) -> None:
        super().__init__()
        with open(r"src/configs/database.json") as json_data_file:
            self.__db_config = json.load(json_data_file)
        with open(r"src/configs/hyperparams.json") as json_data_file:
            self.__hyper_params = json.load(json_data_file)
        self._log = DynamicLogger(self.__hyper_params)
        self._log(logging.INFO, f"Initializing Aspetic Behavior Monitor app")
        self.setupUi(self)
        desktop = QApplication.desktop()
        rect = desktop.availableGeometry()
        self.setGeometry(rect)
        #self.__db_controller = DataAccessManager(self.__hyper_params, self.__db_config)
        #self.createChart()
        self.toolBox.currentChanged.connect(self._on_toolbox_changed)
        self.actionQuit.triggered.connect(self._on_actionQuit_triggered)
        # disable fallen cartridge
        # self.page_l70_rru_belt.setVisible(False)
        # self.page_l71_rru_belt.setVisible(False)
        # self.actionL70_2.setVisible(False)
        # self.actionL71_2.setEnabled(False)
        ##########################
        self._chart_init()
        self._timer_init()
        ####
        self.video_label_list = []
        self.video_label_list.append(self.l_video_0)
        # self.video_label_list.append(self.l_video_1)
        ####
        self.__frame_queue_list = []
        for detection_seg_name in self.__hyper_params["section_included"]:
            for idx, line_id in enumerate(self.__hyper_params["lines"]):
            #for idx, line_id in enumerate(self.__hyper_params["line_config"][detection_seg_name]):
                self._log(logging.INFO, f"Starting line {line_id} thread for {detection_seg_name}")
                monitor = FailureDetection()
                monitor.set_context(detection_seg_name, line_id, "STJ", self.__db_config, self.__hyper_params, detection_seg_name, idx)
                monitor.webcam_images.connect(self._set_video_image)
                #monitor.time_series.connect(self._set_time_series)
                self.__monitor_pool.append(monitor)
        for line_id in self.__hyper_params["streaming_cache"]:
            if(self.__hyper_params["streaming_cache"][line_id]["cam_mode"]=="video"):
                cam_list = self.__hyper_params["streaming_cache"][line_id]["cam_list_video"]
            else:
                cam_list = self.__hyper_params["streaming_cache"][line_id]["cam_list_live"]
            # cap_list = [cv2.VideoCapture(video_path) for video_path in cam_list]
            # for _ in cap_list:
            #     frame_queue = Queue(maxsize=-1)
            #     self.__frame_queue_list.append(frame_queue)
            #camera_manager = CameraManager(cap_list, self.__frame_queue_list, line_id, self.__hyper_params, self.__hyper_params["streaming_cache"][line_id])
            #self.__camera_manager_list.append(camera_manager)
        self.__monitor_pool[0].set_is_infront(True)
        self._start_monitoring()
        self._log(logging.INFO, f"Aspetic Behavior Monitor app stated")
    
    def _run_camera(self):
        for camera_manager in self.__camera_manager_list:
            camera_manager.start()

    def _check_thread(self, sleep_time=180,threads_pool=[]):
        for i in range(0,10080):
            for t in threads_pool:
                #print(t)
                if(t.is_stopped):
                    print('started')
                    t.start() 
            time.sleep(sleep_time)
            
    def _start_monitoring(self):
        #self.createChart()
        #self._run_camera()
        time.sleep(3)
        for monitor in self.__monitor_pool:
            # monitor.run_camera()
            monitor.start()
        # for camera_manager in self.__camera_manager_list:
        #     camera_manager.start()
        
        # self.t_check=threading.Thread(target=self._check_thread,args=(180,self.__monitor_pool))
        # self.t_check.setName('Thread:check')
        # self.t_check.start()
    
    # def _restart_monitoring(self):
    #     #self.createChart()
    #     for monitor in self.__monitor_pool:
    #         monitor.stop()
    #     for monitor in self.__monitor_pool:
    #         monitor.start()
            
    def _timer_init(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._drawLine)
        self.timer.start(5000)
        
    def _drawLine(self):
        i = self.toolBox.currentIndex()
        
        #print(configs["stations"][i])
        #exit(0)
        # tmp_time_series = pd.DataFrame()
        # line_id = list(self.__hyper_params["line_config"].keys())[i]
        # station = "needle"
        # site = "STJ"
        # time_now = datetime.datetime.utcnow()
        # time_now_text = time_now.strftime('%Y-%m-%d %H:%M:%S')
        # time_from = (datetime.datetime.utcnow() - datetime.timedelta(days=1))
        # time_from_text = time_from.strftime('%Y-%m-%d %H:%M:%S')
        # condition = {
        #     Alarm.EventTime >= time_from_text,
        #     Alarm.EventTime <= time_now_text,
        #     Alarm.Line == line_id,
        #     Alarm.Station == station,
        #     Alarm.Area == "ap",
        #     Alarm.Site == site,
        # }
        # collect = self.__db_controller.query_rows(condition, Alarm)
        # if(len(collect)>0):
        #     tmp_time_series = collect[["EventTime"]]
        #     tmp_time_series["value"] = 1
        #     #print(tmp_time_series.head())
        #     tmp_time_series = tmp_time_series[["value","EventTime"]].values.tolist()
        
        # #tmp_time_series = self.__db_controller.get_alarms(station, line, site, time_from_text, timetext)
        # self._set_time_series(tmp_time_series)
        # if(self.__camera_manager.is_stop()):
        #     self._run_camera()
        #     time.sleep(1)
        for i, monitor in enumerate(self.__monitor_pool):
            if(not monitor.isRunning()):
                self._log(logging.INFO, f"Restarting line {i}th thread")
                monitor.start()
                
    def _set_video_image(self, image_list):
        for id, image in enumerate(image_list):
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (self.__l_video_width, self.__l_video_height), interpolation=cv2.INTER_LINEAR)
            showImage = QImage(image.data, image.shape[1],image.shape[0],QImage.Format_RGB888)
            #print(self.l_video.width,self.l_video.height)
            #showImage = QImage(image.data, self.l_video.width(),self.l_video.height(),QImage.Format_RGB888)
            self.video_label_list[id].setPixmap(QPixmap.fromImage(showImage))
    
    def _set_time_series(self, time_series):
        #self.series = QLineSeries() 
        bjtime = QDateTime.currentDateTime()
        self.dtaxisX.setMin(bjtime.addDays(-1))
        self.dtaxisX.setMax(bjtime)
        self.series.clear()
        #print(len(time_series))
        for node, t in time_series:
            bj_t = t + datetime.timedelta(hours=8)
            x_time=time.mktime(bj_t.timetuple())
            self.series.append(int(x_time)*1000, 1)
        
    def _on_toolbox_changed(self):
        for monitor in self.__monitor_pool:
            monitor.set_is_infront(False)
        #print(self.toolBox.currentIndex())
        if(self.toolBox.currentIndex()<len(self.__monitor_pool)):
            self.__monitor_pool[self.toolBox.currentIndex()].set_is_infront(True)
        
    def _on_actionQuit_triggered(self):
        # self.__camera_manager.stop()
        # time.sleep(1)
        for monitor in self.__monitor_pool:
            monitor.stop()
            monitor.wait()
        # for camera_manager in self.__camera_manager_list:
        #     camera_manager.stop()
        app = QApplication.instance()
        self._log(logging.INFO, f"Stoping Aspetic Behavior Monitor app")
        app.quit()
        
    def _on_actionL70_1_triggered(self,state):
        self.__monitor_pool[0].set_is_active(state)
    
    def _on_actionL71_1_triggered(self,state):
        self.__monitor_pool[1].set_is_active(state)
            
    def _on_actionL70_2_triggered(self,state):
        self.__monitor_pool[2].set_is_active(state)
            
    def _on_actionL71_2_triggered(self,state):
        self.__monitor_pool[3].set_is_active(state)
        
    def _chart_init(self):
        #self.series = QLineSeries() 
        self.series = QScatterSeries()
        self.chart = QChart()
        self.series.setMarkerSize(8.0)
        
        #self.series.setName("alarms")
        self.chart.legend().hide()
        self.chart.addSeries(self.series)
        self.dtaxisX = QDateTimeAxis()
        self.vlaxisY = QValueAxis()

        self.vlaxisY.setMin(0)	
        self.vlaxisY.setMax(2) 

        self.dtaxisX.setFormat("MM-dd hh")

        self.dtaxisX.setTickCount(12) 
        self.vlaxisY.setTickCount(2)

        #self.vlaxisY.setTitleText("Alarm")

        self.chart.addAxis(self.dtaxisX,Qt.AlignBottom)
        self.chart.addAxis(self.vlaxisY,Qt.AlignLeft)

        self.series.attachAxis(self.dtaxisX)
        self.series.attachAxis(self.vlaxisY)
        
        self.graph_statistics.setChart(self.chart)
        self.graph_statistics.setRenderHint(QPainter.Antialiasing)
        
    def createChart(self):
        lineSeries = QLineSeries()
        
        xValue = QDateTime()
        xValue.setDate(QDate(2019, 1, 18))
        xValue.setTime(QTime(9, 34))
        yValue = 12
        lineSeries.append(xValue.toMSecsSinceEpoch(), yValue)
        
        xValue.setDate(QDate(2020, 5, 11))
        xValue.setTime(QTime(11, 14))
        yValue = 22
        lineSeries.append(xValue.toMSecsSinceEpoch(), yValue)

        
        chart = QChart()
        #chart.legend().hide()
        chart.addSeries(lineSeries)
        
        axisX = QDateTimeAxis()
        axisX.setTickCount(12)
        axisX.setFormat('MM-dd hh:mm')
        chart.addAxis(axisX, Qt.AlignBottom)
        lineSeries.attachAxis(axisX)
        
        axisY = QValueAxis()
        #axisY.setLabelFormat('%i')
        axisY.setTitleText('Alarms')
        chart.addAxis(axisY, Qt.AlignLeft)
        lineSeries.attachAxis(axisY)
        
        chartView = QChartView(chart)
        chartView.setRenderHint(QPainter.Antialiasing)
        
        #self.graph_statistics = QtWidgets.QGraphicsView(self.centralwidget)
        #self.graph_statistics.setMaximumSize(QtCore.QSize(16777215, 120))
        #self.graph_statistics.setObjectName("graph_statistics")
        #self.gridLayout.addWidget(self.graph_statistics, 1, 0, 1, 3)
        chartView.setMaximumSize(QtCore.QSize(16777215, 200))
        self.gridLayout.addWidget(chartView, 1, 0, 1, 3)
        #self.setCentralWidget(chartView)
