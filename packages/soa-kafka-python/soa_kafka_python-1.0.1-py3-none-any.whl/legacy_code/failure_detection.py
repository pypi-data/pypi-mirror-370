from PyQt5.QtCore import QThread, pyqtSignal, Qt ,QDateTime, QDate, QTime,QTimer
import cv2
import datetime
# from detector import Detector
import threading
from cpe_operation_remind_detector import CPEOperationRemindDetector
from utils.db.data_access_manager import DataAccessManager
from utils.alarm_controller import AlarmController
from entities.alarm import Alarm
from entities.alarm_transformer import transform_to as alarm_transform
import numpy as np
import traceback
from pathlib import Path
import logging
from utils.dynamic_logger import DynamicLogger
import time
import os
import tensorflow as tf
physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    #tf.config.experimental.set_memory_growth(physical_devices[0], True)
    tf.config.experimental.set_virtual_device_configuration(
        physical_devices[0],
        [tf.config.LogicalDeviceConfiguration(memory_limit=1200)] 
    )


class FailureDetection(QThread):
    webcam_images = pyqtSignal(object)
    ##time_series = pyqtSignal(object)
    # __max_signal_queue_len = 20
    # __audio_alarm_interval = 30
    # __max_alarms = 3
    # __signal_queue = []
    # __is_infront = False
    # __is_active = True
    # __is_running = True
    # __last_alarm = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    # __alarm_count = 0

    def __int__(self, parent=None):
        super(FailureDetection, self).__init__(parent) 
        # self.__db_configs = None
        # self.__station = None
        # self.__line = None
        # self.__site = None
        # self.__hyper_params = None
        # self.__db_controller = None
        # self.__alarm_controller = None
        # self.is_stopped = True
        # #self.__last_alarm = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        # #self.__alarm_count = 0
        # self.__detector_name = None
    
    def stop(self): 
        self.__is_running = False

    def set_is_infront(self, is_infront):
        self.__is_infront = is_infront
    
    def set_is_active(self, is_active):
        self.__is_active = is_active
    
    def set_context(self, station, line, site, db_configs, hyper_params, detector_name, id):
        self.__id = id
        self.__station = station
        self.__line = line
        self.__site = site
        self.__hyper_params = hyper_params
        self.__detector_name = detector_name
        self.__alarm_interval = self.__hyper_params["line_config"][self.__detector_name][self.__line]["alarm_interval"]
        self.__audio_alarm_interval = self.__hyper_params["line_config"][self.__detector_name][self.__line]["inter_alarm_interval"]
        self.__max_alarms = self.__hyper_params["line_config"][self.__detector_name][self.__line]["max_alarms"]
        self.__signal_queue = []
        self.__is_infront = False
        self.__is_active = True
        self.__is_running = True
        self.__last_alarm = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        self.__alarm_count = 0
        ################
        self.__db_configs = db_configs
        self._log = DynamicLogger(self.__hyper_params)
        self.__max_signal_queue_len = self.__hyper_params["line_config"][self.__detector_name][self.__line]["max_signal_queue_len"]
        self.__db_controller = DataAccessManager(self.__hyper_params, self.__db_configs)
        self.__alarm_controller = AlarmController(self.__hyper_params)
        self.__frame_per_round = self.__hyper_params["line_config"][self.__detector_name][self.__line]["frame_per_round"]
        if(self.__hyper_params["line_config"][detector_name][line]["cam_mode"]=="video"):
            self.__video_path_list = self.__hyper_params["line_config"][detector_name][line]["cam_list_video"]
        else:
            self.__video_path_list = self.__hyper_params["line_config"][detector_name][line]["cam_list_live"]
        #print(cam_list)
        self.__cam_list = [cv2.VideoCapture(video_path) for video_path in self.__video_path_list]
        self.__cam_idx = self.__hyper_params["line_config"][detector_name][line]["cam_idx"]
        # to be replaced by a factory
        if(detector_name == "cpe_operation_remind"):
            self.__detector = CPEOperationRemindDetector(self.__hyper_params, self.__line)
        self.__frame_num = 0
    
    # Alarm suppression
    def _should_send_alarm(self):
        res = False
        timenow = (datetime.datetime.utcnow())
        #timetext = timenow.strftime('%Y-%m-%d %H:%M:%S')

        if(len(self.__signal_queue) > 0):
            if((timenow - self.__signal_queue[-1]).total_seconds() >= self.__audio_alarm_interval):
                self.__signal_queue = []
                self.__alarm_count = 0
        if(len(self.__signal_queue) < self.__max_signal_queue_len):
            self.__signal_queue.append(timenow)
            if(len(self.__signal_queue) == self.__max_signal_queue_len):
                if((timenow >= self.__last_alarm)
                   and (timenow - self.__last_alarm).total_seconds() >= self.__alarm_interval
                   and self.__alarm_count < self.__max_alarms):
                    res = True
                    self.__alarm_count += 1
                    self.__last_alarm = timenow
                    if(self.__alarm_count >= self.__max_alarms):
                        self.__alarm_count = 0
                        self.__last_alarm = timenow + datetime.timedelta(seconds=self.__audio_alarm_interval)
        else:
            self.__signal_queue.pop(0)
            self.__signal_queue.append(timenow)
            if((timenow >= self.__last_alarm)
                   and (timenow - self.__last_alarm).total_seconds() >= self.__alarm_interval
                   and self.__alarm_count < self.__max_alarms):
                    res = True
                    self.__alarm_count += 1
                    self.__last_alarm = timenow
                    if(self.__alarm_count >= self.__max_alarms):
                        self.__alarm_count = 0
                        self.__last_alarm = timenow + datetime.timedelta(seconds=self.__audio_alarm_interval)
        
        return res
    
    def _send_alarms(self, timetext, text, img_path, alarm_topic):
        if(self._should_send_alarm()):
            alarm_types = self.__hyper_params["line_config"][self.__detector_name][self.__line]["alarm_type"]
            alarm_to_persit = Alarm(
                Site = self.__site,
                Area = "ap",
                Line = self.__line,
                Station = self.__station,
                AlarmType = self.__detector_name,
                ReminderType = (",").join(alarm_types),
                AlarmContent = text,
                Severity = 5,
                EventTime = timetext,
                CreatedTime = timetext
            )
            #self.__db_controller.add_rows([alarm_to_persit])
            self._log(logging.INFO, f"{self.__line} sends alarm")
            #print("Send Alarm")
            text = f"line {self.__line} {text}"
            for alarm_type in alarm_types:
                if(alarm_type=="email"):
                    t = threading.Thread(target=self.__alarm_controller.send_email_alarms,args=(text, timetext, img_path, self.__hyper_params["line_config"][self.__detector_name][self.__line]))
                    t.start()
                elif(alarm_type=="local"):
                    if(alarm_topic is None or alarm_topic == ""):
                        audio_file = self.__hyper_params["line_config"][self.__detector_name][self.__line]["audio_file"]
                    else:
                        audio_file = self.__hyper_params["line_config"][self.__detector_name][self.__line]["alarm_option"][alarm_topic]["audio_file"]
                    t = threading.Thread(target=self.__alarm_controller.send_audio_alarms,args=(audio_file))
                    t.start()
                elif(alarm_type=="plc"):
                    if(alarm_topic is None or alarm_topic == ""):
                        ns = self.__hyper_params["line_config"][self.__detector_name][self.__line]["audio_sytem_ns"]
                        audio_signal_start = self.__hyper_params["line_config"][self.__detector_name][self.__line]["audio_signal_start"]
                    else:
                        ns = self.__hyper_params["line_config"][self.__detector_name][self.__line]["alarm_option"][alarm_topic]["audio_sytem_ns"]
                        audio_signal_start = self.__hyper_params["line_config"][self.__detector_name][self.__line]["alarm_option"][alarm_topic]["audio_signal_start"]
                    t = threading.Thread(target=self.__alarm_controller.send_plc_alarms,args=(ns, audio_signal_start))
                    t.start()
                elif(alarm_type=="http"):
                    t = threading.Thread(target=self.__alarm_controller.send_http_alarms,args=(self.__detector_name, self.__line))
                    t.start()
    
    def run(self):
        self.is_stopped = False
        saved_image_path = f"{self.__hyper_params['snapshot_path']}\\{self.__detector_name}\\line_{self.__line}\\"
        # cache video
        out_codec = cv2.VideoWriter_fourcc('m', 'p', '4', 'v') 
        out_fps = 12
        out_width = 1920
        out_height = 1080
        video_frames = 1800 * out_fps
        saved_video_path = f"{self.__hyper_params['snapshot_path']}\\{self.__detector_name}\\cache_line_{self.__line}\\"
        #time.sleep(2)
        
        text = ""
        count = 0
        self.__cam_list[0].set(cv2.CAP_PROP_POS_FRAMES, 600)
        while self.__is_running:
            images_to_return = []
            for cam_id, cap in enumerate(self.__cam_list):
                try:
                    # clear opencv cache
                    for i in range(2):
                        success,image = cap.read()
                    if(not success):
                        self.__cam_list[cam_id] = cv2.VideoCapture(self.__video_path_list[cam_id])
                        continue
                    #image_raw = image.copy()
                    #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    image_return = image.copy()
                    # # cache video
                    # if(self.__frame_num % video_frames == 0):
                    #     if(self.__frame_num > 0):
                    #         self.__out_video.release()
                    #     self.__frame_num = 0
                    #     video_suffix = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                    #     self.__out_video = cv2.VideoWriter(os.path.join(saved_video_path,f"cached_video_{self.__detector_name}_{self.__line}_{video_suffix}.mp4"), 
                    #                 out_codec, 
                    #                 out_fps, 
                    #                 (out_width, out_height))
                    # self.__out_video.write(image_return)
                    # self.__frame_num += 1
                    #image_test = image.copy()
                    #image_raw = cv2.resize(image_raw, (880, 600), interpolation=cv2.INTER_LINEAR) 
                    if(self.__is_active and (count + (self.__id*2)) % self.__frame_per_round == 0): 
                        result, text, image_return, alarm_topic = self.__detector.detect(image_return, self.__cam_idx[cam_id])
                        image_return = cv2.resize(image_return, (1920, 1080), interpolation=cv2.INTER_LINEAR) 
                        if(result):
                            time_now = (datetime.datetime.utcnow())
                            time_now_text = time_now.strftime('%Y-%m-%d %H:%M:%S')
                            #print(needle_idx)
                            #print(f"{saved_image_path}{time_now.strftime('%Y%m%d%H%M%S')}_popup.png")
                            snapshot_path = f"{saved_image_path}{time_now.strftime('%Y%m%d%H%M%S%f')}_{self.__detector_name}_{self.__cam_idx[cam_id]}.jpg"
                            #snapshot_path_raw = f"{saved_image_path}{time_now.strftime('%Y%m%d%H%M%S')}_{self.__detector_name}_{self.__cam_idx[cam_id]}_raw.jpg"
                            #snapshot_path_test =f"{saved_image_path}{time_now.strftime('%Y%m%d%H%M%S')}_popup_test.jpg"
                            #cv2.imwrite(snapshot_path, cv2.cvtColor(image_return, cv2.COLOR_RGB2BGR))
                            cv2.imwrite(snapshot_path, image_return)
                            #cv2.imwrite(snapshot_path_raw, image_test)
                            #cv2.imwrite(snapshot_path_test, image_test)
                            self._send_alarms(time_now_text, text, snapshot_path, alarm_topic)
                        # else:
                        #     text = ""
                    #print(result)
                    # cache video
                    if(self.__frame_num % video_frames == 0):
                        if(self.__frame_num > 0):
                            self.__out_video.release()
                        self.__frame_num = 0
                        video_suffix = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                        self.__out_video = cv2.VideoWriter(os.path.join(saved_video_path,f"cached_video_{self.__detector_name}_{self.__line}_{video_suffix}.mp4"), 
                                    out_codec, 
                                    out_fps, 
                                    (out_width, out_height))
                        
                    self.__out_video.write(image_return)
                    self.__frame_num += 1
                    cv2.putText(image_return, text, (40, 60), cv2.FONT_HERSHEY_TRIPLEX, 2.0, (0, 0, 255), 2)
                    images_to_return.append(image_return)
                except:
                    self._log(logging.INFO, traceback.format_exc())
                    # print(traceback.format_exc())
                    # print(e)
            if(self.__is_infront):
                #print(self.__line, self.__detector_name)
                self.webcam_images.emit(images_to_return)
            #image = self.__frame_queue.get(False)
            count += 1
            count = count % 10000
        self.__out_video.release()
        self._log(logging.INFO, f"{self.__line} thread stoped")
        #print("thread stoped")
        self.is_stopped = True