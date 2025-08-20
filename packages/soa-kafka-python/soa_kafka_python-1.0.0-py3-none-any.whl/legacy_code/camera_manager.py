import cv2
from queue import Queue
from threading import Thread
import traceback
import time
import logging
import json
from datetime import datetime
from utils.dynamic_logger import DynamicLogger
import numpy as np
import os

class CameraManager:
    _log = None

    def __init__(self, cap_list, frame_queue_list, line_id, hyper_params, hyper_params_segment, cam_list):
        # with open(r"src/configs/hyperparams.json") as json_data_file:
        #     self.__hyper_params = json.load(json_data_file)
        self.__line = line_id
        self.__hyper_params = hyper_params
        self.__hyper_params_segment = hyper_params_segment
        self._log = DynamicLogger(self.__hyper_params)
        self.__use_cached_video = self.__hyper_params["use_cached_video"]
        self.__cap_list = cap_list
        self.__video_path_list = cam_list
        # for cap in self.__cap_list:
        #     cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        for cap in self.__cap_list:
            print(cap.get(cv2.CAP_PROP_FPS))
        self.__frame_queue_list = frame_queue_list
        self.__cached_frame_queue_list = [Queue() for _ in frame_queue_list]
        self.__is_running = False
        self.__cap_thread_list = []
        self.__clean_thread = None
        self.__cache_video_thread = None
        self.__cam_list = self.__hyper_params_segment["cam_idx"]
    
    def start(self):
        self.__is_running = True
        self._log(logging.INFO, "Cam reading starts.")
        for id, cap in enumerate(self.__cap_list):
            thread_capture = Thread(target=self.capture_queue, args=(id, cap, self.__cached_frame_queue_list[id], self.__video_path_list[id]))
            self.__cap_thread_list.append(thread_capture)
        #print(bool(self.__use_cached_video))
        self.__clean_thread = Thread(target=self.clean_queue)
        # if(bool(self.__use_cached_video)):
        #     self.__cache_video_thread = Thread(target=self.cache_video)
        for thread_capture in self.__cap_thread_list:
            thread_capture.start()
        self.__clean_thread.start()
        #self.__cache_video_thread.start()
        #time.sleep(1)
        #self.__clean_thread.start()
        #time.sleep(1)
 
    def stop(self):
        self.__is_running = False
        # if(bool(self.__use_cached_video)):
        #     self.__cache_video_thread.join()
        self.__clean_thread.join()
        for thread_capture in self.__cap_thread_list:
            thread_capture.join()
        self._log(logging.INFO, f"All cameras stopped.")
    
    def is_stop(self):
        return self.__is_running == False

    def capture_queue(self, id, cap, queue, video_path):
        try:
            self._log(logging.INFO, f"Camera {id} starts.")
            is_new_connection = False
            while self.__is_running:
                timestamp_now = datetime.utcnow()
                if(timestamp_now.minute in [45,30,15,0] and timestamp_now.second in [0,1]): # refresh stream every 15 mins
                    if(not is_new_connection):
                        cap.release()
                        cap = cv2.VideoCapture(video_path)
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        is_new_connection = True
                        self._log(logging.INFO, f"Camera {id} new cam connection.")
                elif(timestamp_now.minute in [45,30,15,0] and timestamp_now.second < 5):
                    is_new_connection = False
                timestamp_1 = datetime.utcnow()
                return_value, frame = cap.read()
                #timestamp_1 = cap.get(cv2.CAP_PROP_TIMESTAMP)
                timestamp_2 = datetime.utcnow()
                #print(timestamp_1, timestamp_2)

                if return_value:
                    #result, frame_compressed = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                    #queue.put_nowait((timestamp_1, timestamp_2, frame_compressed))
                    queue.put_nowait((timestamp_1, timestamp_2, frame.copy()))
                else:
                    queue.put_nowait((timestamp_1, timestamp_2, None))
                del frame
                #time.sleep(0.1)
        except:
            self._log(logging.INFO, traceback.format_exc())
        finally:
            self._log(logging.INFO, f"Camera {id} stops.")
            cap.release()

    def clean_queue(self):
        self._log(logging.INFO, f"Clean thread starts.")
        try:
            while self.__is_running:
                frame_items = [f.get(timeout=30) for f in self.__cached_frame_queue_list]
                max_cap_idx = np.argmax([frame_item[1] for frame_item in frame_items])
                for idx, frame_queue in enumerate(self.__cached_frame_queue_list):
                    timestamp_1, timestamp_2, frame = frame_items[idx]
                    #print(timestamp_1, timestamp_2)
                    if(idx != max_cap_idx):
                        try:
                            while timestamp_1<frame_items[max_cap_idx][0]:
                                del frame
                                timestamp_1, timestamp_2, frame = frame_queue.get(timeout=30)
                                #print(idx, max_cap_idx,timestamp_1, timestamp_2)
                        except:
                            print("queue exhausted")
                    #print(timestamp_1, timestamp_2)
                    #result, frame_compressed = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                    #self.__frame_queue_list[idx].put_nowait(frame_compressed)
                    self.__frame_queue_list[idx].put_nowait(frame)
                    del frame
                    #print(idx, max_cap_idx,timestamp_1, timestamp_2,self.__cached_frame_queue_list[idx].qsize())
                #time.sleep(1/30)
        except:
            self._log(logging.INFO, traceback.format_exc())
        finally:
            self._log(logging.INFO, f"Clean thread stops.")

    def cache_video(self):
        self._log(logging.INFO, f"Video cache thread starts.")
        out_codec = cv2.VideoWriter_fourcc('m', 'p', '4', 'v') 
        out_fps = self.__hyper_params["out_fps"]
        out_width = 1920
        out_height = 1080
        video_frames = self.__hyper_params["video_cache_length"] * out_fps
        frame_num = 0
        out_list = []
        video_writer_all = None
        try:
            while self.__is_running:
                result_list = [] 
                #print(frame_num)
                if(frame_num % video_frames == 0):
                    #print(frame_num)
                    frame_num+=1
                    for i, out in enumerate(out_list):
                        out.release()
                    date_str = datetime.now().strftime("%Y_%m_%d")
                    parent_path = os.path.join(self.__hyper_params_segment["video_output_path"],
                                                self.__line,
                                                date_str,
                                                "cache")
                    if(not os.path.exists(parent_path)):
                        os.makedirs(parent_path)
                    video_suffix = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                    # out_list = [cv2.VideoWriter(
                    #                     os.path.join(parent_path,
                    #                                  self.__hyper_params_segment["cam_config"][cam_name]["output_prefix"]+video_suffix+".mp4"), 
                    #                     out_codec, 
                    #                     out_fps, 
                    #                     (out_width, out_height)) 
                    #     for cam_name in self.__cam_list]
                    video_writer_all = cv2.VideoWriter(
                                        os.path.join(parent_path,
                                                     self.__hyper_params_segment["video_output_all_prefix"]+video_suffix+".mp4"), 
                                        out_codec, 
                                        out_fps, 
                                        (int(out_width*3), 
                                        int(out_height*2))
                                    )
                # for idx, (_,_,frame) in enumerate(frame_items):
                #     frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                #     out_list[idx].write(frame)
                for idx, frame_queue in enumerate(self.__frame_queue_list):
                    try:
                        frame = frame_queue.get(timeout=30)
                    except:
                        print("queue exhausted")
                        break
                    #frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                    #out_list[idx].write(frame)
                    result_list.append(frame)
                    #print(idx, max_cap_idx,timestamp_1, timestamp_2,self.__cached_frame_queue_list[idx].qsize())
                #time.sleep(1/30)
                result_list.append(np.zeros((out_height, out_width, 3), dtype=np.uint8))
                frame_up = np.hstack((result_list[0], 
                                result_list[1],
                                result_list[2]))
                frame_down = np.hstack((result_list[3], 
                                    result_list[4],
                                    result_list[5]))
                frame_all = np.vstack((frame_up, frame_down))
                video_writer_all.write(frame_all)
                frame_num += 1
        except:
            self._log(logging.INFO, traceback.format_exc())
        finally:
            self._log(logging.INFO, f"Video cache thread stops.")
            # for out in out_list:
            #     out.release()
            video_writer_all.release()

if __name__ == '__main__':
    with open(r"src/configs/hyperparams.json") as json_data_file:
        hyper_params = json.load(json_data_file)
    log = DynamicLogger(hyper_params)
    log(logging.INFO, f"Video cache process starts.")
    out_codec = cv2.VideoWriter_fourcc('m', 'p', '4', 'v') 
    out_fps = hyper_params["out_fps"]
    out_width = int(1920/2)
    out_height = int(1080/2)
    video_frames = hyper_params["video_cache_length"] * out_fps
    frame_num = 0
    line = "71"
    hyper_params_segment = hyper_params["streaming_cache"][line]
    out_list = []
    cam_list = hyper_params["streaming_cache"][line]["cam_list_live"]
    cap_list = [cv2.VideoCapture(video_path) for video_path in cam_list]
    for cap in cap_list:
        print(cap.get(cv2.CAP_PROP_BUFFERSIZE))
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    frame_queue_list = [Queue() for _ in cam_list]
    cam_name_list = hyper_params_segment["cam_idx"]
    camera_manager = CameraManager(cap_list, frame_queue_list, line, hyper_params, hyper_params["streaming_cache"][line], cam_list)
    #frame_list = []
    camera_manager.start()
    is_running = True
    try:
        while is_running:
            result_list = [] 
            #print(frame_num)
            if(frame_num % video_frames == 0):
                #print(frame_num)
                frame_num+=1
                for i, out in enumerate(out_list):
                    out.release()
                    del out
                date_str = datetime.now().strftime("%Y_%m_%d")
                parent_path = os.path.join(hyper_params_segment["video_output_path"],
                                            line,
                                            date_str,
                                            "cache")
                if(not os.path.exists(parent_path)):
                    os.makedirs(parent_path)
                video_suffix = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                out_list = [cv2.VideoWriter(
                                    os.path.join(parent_path,
                                                 hyper_params_segment["cam_config"][cam_name]["output_prefix"]+video_suffix+".mp4"), 
                                    out_codec, 
                                    out_fps, 
                                    (out_width, out_height)) 
                    for cam_name in cam_name_list]

            for idx, frame_queue in enumerate(frame_queue_list):
                try:
                    frame = frame_queue.get(timeout=30)
                except:
                    print("queue exhausted")
                    break
                #frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                frame = cv2.resize(frame, (out_width, out_height))
                out_list[idx].write(frame)
                #result_list.append(frame)
                #print(idx, max_cap_idx,timestamp_1, timestamp_2,self.__cached_frame_queue_list[idx].qsize())
            #time.sleep(1/30)
            # result_list.append(np.zeros((out_height, out_width, 3), dtype=np.uint8))
            # frame_up = np.hstack((result_list[0], 
            #                 result_list[1],
            #                 result_list[2]))
            # frame_down = np.hstack((result_list[3], 
            #                     result_list[4],
            #                     result_list[5]))
            # frame_all = np.vstack((frame_up, frame_down))
            # video_writer_all.write(frame_all)
            cv2.imshow(f"Output Video", np.zeros((400, 600, 3), dtype=np.uint8))
            if cv2.waitKey(1) & 0xFF == ord('q'): is_running = False
            frame_num += 1
    except:
        log(logging.INFO, traceback.format_exc())
    finally:
        log(logging.INFO, f"Video cache process stops.")
        camera_manager.stop()
        for out in out_list:
            out.release()
        #video_writer_all.release()