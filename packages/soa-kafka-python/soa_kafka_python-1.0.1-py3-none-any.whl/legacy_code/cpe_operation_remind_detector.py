import numpy as np
import cv2
import datetime
import json
import os
import sys
import traceback
import logging
from shapely.geometry import Polygon, LineString, box
from utils.dynamic_logger import DynamicLogger
from utils.db.data_access_manager import DataAccessManager
from PIL import ImageDraw, ImageFont, Image
import tensorflow as tf
from tensorflow import keras
from models.yolo7.model.nets.yolo_tiny import get_model
from models.yolo7.model.utils.utils import (get_classes, preprocess_input, resize_image)
from entities.state_enum import StateEnum
physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    #tf.config.experimental.set_memory_growth(physical_devices[0], True)
    tf.config.experimental.set_virtual_device_configuration(
        physical_devices[0],
        [tf.config.LogicalDeviceConfiguration(memory_limit=2000)] 
    )
sys.path.append(r'..')

MAX_DETECTION = 6

class CPEOperationRemindDetector():
    def __init__(self,hyper_params, line_id):
        # super().__init__()
        self.__hyper_params = hyper_params
        #self.__db_controller = DataAccessManager(self.__hyper_params, self.__db_configs)
        self._log = DynamicLogger(self.__hyper_params)
        self.__line_id = line_id
        self.__current_state = StateEnum.CPE_Second_Filtration_Remind_End
        self.__last_state_timestampe = datetime.datetime.now()
        classes_path = self.__hyper_params["line_config"]["cpe_operation_remind"][line_id]["classes_path"] 
        anchor_path = self.__hyper_params["line_config"]["cpe_operation_remind"][line_id]["anchor_path"]
        self.__class_names, _ = get_classes(classes_path)
        self.__input_shape = [640, 640]
        self.__letterbox_image = True
        self.__hyper_params = hyper_params
        self.__line_id = line_id
        self.__last_distance_diff = 0
        self.__model = get_model(self.__hyper_params["line_config"]["cpe_operation_remind"][line_id]["model_path"],
                                 classes_path,
                                 anchor_path,
                                 self.__input_shape,
                                 self.__hyper_params["line_config"]["cpe_operation_remind"][line_id]["score_threshold_min"],
                                 0.7,
                                 self.__letterbox_image)
        annotations_path = self.__hyper_params["line_config"]["cpe_operation_remind"][line_id]["annotations_path"]
        self.__entre_line, self.__rack_ready_area, self.__interest_area = self._get_interest_area_pts(annotations_path)
        self.__rack_detected_times = 0
        self.__rack_ready_detected_times = 0
        self.__person_ready_detected_times = 0
        #text = ""
    
    def _get_interest_area_pts(self, annotations_file):
        #print(annotations_file)
        with open(annotations_file, 'r') as fid:
            annotation = json.load(fid)
        interest_pts_all = annotation['shapes']
        entre_line = []
        rack_ready_area = []
        interest_area = []
        for pts in interest_pts_all:
            if(pts['label'] == 'cpe_entre_line'):
                entre_line.append(pts['points'])
            if(pts['label'] == 'rack_area'):
                rack_ready_area.append(pts['points'])
            if(pts['label'] == 'detectable_area'):
                interest_area.append(pts['points'])
        entre_line = np.array(entre_line, dtype=int)[0]
        rack_ready_area = np.array(rack_ready_area, dtype=int)[0]
        interest_area = np.array(interest_area, dtype=int)[0]
        
        return entre_line, rack_ready_area, interest_area
    
    def _line_intersect(self, line_pts_src, line_pts_tgt):
        is_intersect = False
        line_src = LineString(line_pts_src)
        line_tgt = LineString(line_pts_tgt)

        if(len(line_src.intersection(line_tgt).coords) > 0):
            intersection_coords = line_src.intersection(line_tgt).coords[0]
            line_start = line_pts_src[0]
            line_end = line_pts_src[1]
            #if(np.sqrt(np.power(line_end[0] - intersection_coords[0], 2) + np.power(line_end[1] - intersection_coords[1], 2)) > np.sqrt(np.power(line_start[0] - intersection_coords[0], 2) + np.power(line_start[1] - intersection_coords[1], 2))):
            distance_diff = np.sqrt(np.power(line_end[0] - intersection_coords[0], 2) + np.power(line_end[1] - intersection_coords[1], 2)) - np.sqrt(np.power(line_start[0] - intersection_coords[0], 2) + np.power(line_start[1] - intersection_coords[1], 2))
            if(self.__last_distance_diff > distance_diff):
                is_intersect = True
            self.__last_distance_diff = distance_diff

        return is_intersect
        #return len(line_src.intersection(line_tgt).coords) > 0
    
    def _poly_intersect(self, ploy_pts_src, ploy_pts_tgt):
        poly_src = Polygon(ploy_pts_src)
        poly_tgt = Polygon(ploy_pts_tgt)

        return round(poly_src.intersection(poly_tgt).area/poly_src.area,3) > 0.5
    
    def _cvt_rect_to_poly(self, rect):
        x_min, y_min, x_max, y_max = rect
        
        return np.array([[x_min, y_min], [x_min, y_max], [x_max, y_max], [x_max, y_min]], dtype=int)
    
    def detect(self, image_cv,_):
        bboxes, scores, classes = [], [], []
        text, status_text, alarm_topic = "", "", ""
        triger_alarm = False
        try:
            image_np = image_cv.copy()
            img_target = image_np
            image_data  = resize_image(Image.fromarray(np.uint8(img_target)), (self.__input_shape[1], self.__input_shape[0]), self.__letterbox_image)
            image_data  = np.expand_dims(preprocess_input(np.array(image_data, dtype='float32')), 0)
            input_image_shape = np.expand_dims(np.array([Image.fromarray(np.uint8(img_target)).size[1], Image.fromarray(np.uint8(img_target)).size[0]], dtype='float32'), 0)
            out_boxes, out_scores, out_classes = self.__model([image_data, input_image_shape], training=False)
            for i, c in list(enumerate(out_classes)):
                predicted_class = self.__class_names[int(c)]
                box             = out_boxes[i]
                score           = "{:.2f}".format(out_scores[i])
                #print(score)
                #print(box)
                top, left, bottom, right = box

                top     = max(0, np.floor(top).astype('int32'))
                left    = max(0, np.floor(left).astype('int32'))
                bottom  = min(Image.fromarray(np.uint8(img_target)).size[1], np.floor(bottom).astype('int32'))
                right   = min(Image.fromarray(np.uint8(img_target)).size[0], np.floor(right).astype('int32'))
                bboxes.append([top, left, bottom, right])
                scores.append(score)
                classes.append(predicted_class)

            for i in range(len(classes)):
                ymin = int(bboxes[i][0])
                xmin = int(bboxes[i][1])
                ymax = int(bboxes[i][2])
                xmax = int(bboxes[i][3])
                #print(ymin,xmin,ymax,xmax)
                cv2.rectangle(image_cv, (xmin, ymin), (xmax, ymax), (0,255,0), 1)
                #cv2.rectangle(image_cv, (xmin, ymin), (xmin+(len(classes[i])+len(str(scores[i])))*15, ymin-30), (0,255,0), -1)
                cv2.putText(image_cv, f"{classes[i]} " + str(scores[i]),(xmin, int(ymin-10)),0, 0.75, (255,255,255),1)
                #text = classes[i]
            
            if(len(classes)==0):
                text = ""
                #pass
            else:
                cpe_tower_ids = np.argwhere(np.array(classes) == "cpe_tower")
                person_ids = np.argwhere(np.array(classes) == "person")
                person_ready_ids = np.argwhere(np.array(classes) == "person_ready")
                rack_ids = np.argwhere(np.array(classes) == "rack")
                rack_ready_ids = np.argwhere(np.array(classes) == "rack_ready")

                cpe_tower_ids = np.hstack(cpe_tower_ids) if len(cpe_tower_ids) > 0 else cpe_tower_ids
                person_ids = np.hstack(person_ids) if len(person_ids) > 0 else person_ids
                person_ready_ids = np.hstack(person_ready_ids) if len(person_ready_ids) > 0 else person_ready_ids
                rack_ids = np.hstack(rack_ids) if len(rack_ids) > 0 else rack_ids
                rack_ready_ids = np.hstack(rack_ready_ids) if len(rack_ready_ids) > 0 else rack_ready_ids
                # print(operate_table_ids)
                # print(operator_hold_filter_ids)
                # print(rack_packed_ids)
                # for sampling
                if(len(person_ready_ids) > 0
                   or len(rack_ids) > 0 
                   or len(rack_ready_ids) > 0 ):
                    time_now = (datetime.datetime.utcnow())
                    saved_image_path = f"{self.__hyper_params['snapshot_path']}\\cpe_operation_remind\\line_{self.__line_id}\\"
                    snapshot_path = f"{saved_image_path}{time_now.strftime('%Y%m%d%H%M%S')}_cpe_operation_remind_test.jpg"
                    image_debug = cv2.cvtColor(image_cv, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(snapshot_path, image_debug)
                # end
                if(len(rack_ids) > 0 and self.__current_state == StateEnum.CPE_Second_Filtration_Remind_End):
                    self.__rack_detected_times += 1
                if(len(rack_ready_ids) > 0 and (self.__current_state == StateEnum.CPE_Second_Filtration_Remind_Start
                                            or self.__current_state == StateEnum.CPE_Second_Filtration_Filter_Checked)):
                    self.__rack_ready_detected_times += 1
                if(len(person_ready_ids) > 0 and self.__current_state == StateEnum.CPE_Second_Filtration_Remind_Start):
                    self.__person_ready_detected_times += 1
                if(self.__current_state == StateEnum.CPE_Second_Filtration_Remind_End):
                    if(self.__rack_detected_times > MAX_DETECTION and len(rack_ids) > 0):
                        if(self._poly_intersect(self._cvt_rect_to_poly([bboxes[rack_ids[0]][1],bboxes[rack_ids[0]][0],bboxes[rack_ids[0]][3],bboxes[rack_ids[0]][2]]),self._cvt_rect_to_poly(np.hstack(self.__rack_ready_area)))):
                            self.__current_state = StateEnum.CPE_Second_Filtration_Remind_Start
                            text = "Found empty rack" # for debug
                            self.__last_state_timestampe = datetime.datetime.now()
                            self.__rack_detected_times = 0
                            self.__rack_ready_detected_times = 0
                            self.__person_ready_detected_times = 0
                elif(self.__current_state == StateEnum.CPE_Second_Filtration_Remind_Start):
                    if(self.__person_ready_detected_times > MAX_DETECTION):
                        self.__current_state = StateEnum.CPE_Second_Filtration_Filter_Checked
                        text = "Start Reminding"
                        #self.__last_state_timestampe = datetime.datetime.now()
                        self.__rack_detected_times = 0
                        self.__rack_ready_detected_times = 0
                        self.__person_ready_detected_times = 0
                    elif(self.__rack_ready_detected_times > MAX_DETECTION):
                        self.__current_state = StateEnum.CPE_Second_Filtration_Remind_End
                        text = "No Lift Up"
                        #self.__last_state_timestampe = datetime.datetime.now()
                        self.__rack_detected_times = 0
                        self.__rack_ready_detected_times = 0
                        self.__person_ready_detected_times = 0
                    else:
                        time_diff = (datetime.datetime.now() - self.__last_state_timestampe).total_seconds() / 1
                        if(time_diff > 10800):
                            self.__current_state = StateEnum.CPE_Second_Filtration_Remind_End
                            text = "Time over and no Lift Up"
                            self.__last_state_timestampe = datetime.datetime.now()
                            self.__rack_detected_times = 0
                            self.__rack_ready_detected_times = 0
                            self.__person_ready_detected_times = 0
                elif(self.__current_state == StateEnum.CPE_Second_Filtration_Filter_Checked):
                    #is_operate_table_left = True
                    if(self.__rack_ready_detected_times > MAX_DETECTION):
                        self.__current_state = StateEnum.CPE_Second_Filtration_Remind_End
                        text = "Assemply complete" # for debug
                        self.__rack_detected_times = 0
                        self.__rack_ready_detected_times = 0
                        self.__person_ready_detected_times = 0
                        self.__last_state_timestampe = datetime.datetime.now()
                    else:
                        time_diff = (datetime.datetime.now() - self.__last_state_timestampe).total_seconds() / 1
                        if(time_diff > 10800):
                            self.__current_state = StateEnum.CPE_Second_Filtration_Remind_End
                            text = "Time over" # for debug
                            self.__last_state_timestampe = datetime.datetime.now()
                            self.__rack_detected_times = 0
                            self.__rack_ready_detected_times = 0
                            self.__person_ready_detected_times = 0
                has_intersected_cpe_tower = False
                for i in cpe_tower_ids:
                    # for bbox in bboxes[cpe_tower_ids]:
                    ymin = int(bboxes[i][0])
                    xmin = int(bboxes[i][1])
                    ymax = int(bboxes[i][2])
                    xmax = int(bboxes[i][3])
                    #if(is_cpe_tower_move_in):
                    if(self._line_intersect([[xmin, ymax], [xmax, ymax]], self.__entre_line)):
                        #if(self._line_intersect([[xmin, ymax], [xmax, ymax]], self.__entre_line)):
                        text = "CPE Tower Entering"
                        #self.__last_state_timestampe = datetime.datetime.now
                        has_intersected_cpe_tower = True
                if(not has_intersected_cpe_tower):
                    self.__last_distance_diff = 0


            if(self.__current_state == StateEnum.CPE_Second_Filtration_Remind_Start):
                status_text = "Monitoring"
            elif(self.__current_state == StateEnum.CPE_Second_Filtration_Filter_Checked):
                status_text = "Filter Lift up checked"
            elif(self.__current_state == StateEnum.CPE_Second_Filtration_Remind_End):
                status_text = "Non Monitoring"

            if(text == "CPE Tower Entering"):
                alarm_topic = "cpe_tower"
                triger_alarm = True
            elif(text == "Start Reminding"):
                alarm_topic = "sop"
                triger_alarm = True
            elif(text == "Time over and no Lift Up"):
                alarm_topic = "end"
                triger_alarm = True
            elif(len(text) > 0):
                alarm_topic = "end"
                triger_alarm = True
            else:
                alarm_topic = ""
                triger_alarm = False

            # mask = np.zeros(image_cv.shape[:2], np.uint8)
            # cv2.fillPoly(mask, self.__crop_area, 255)
            # image_cv = cv2.bitwise_and(image_cv, image_cv, mask=mask)
            cv2.putText(image_cv, f"{status_text} -- {text}", (40, 60), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255), 2)
            cv2.polylines(image_cv, [self._cvt_rect_to_poly(np.hstack(self.__rack_ready_area))], 1, (255,0,255), 2) 
            image_cv = cv2.resize(image_cv, (1920, 1080), interpolation=cv2.INTER_LINEAR)
            #image_cv = np.asarray(image)
        except:
            self._log(logging.INFO, traceback.format_exc().encode('utf-8', 'ignore'))
            classes = []
            text = ""
            status_text = ""
            # print(traceback.format_exc())
            # print(e)

        return triger_alarm, f"{status_text} -- {text}", image_cv, alarm_topic