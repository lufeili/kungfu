#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import math
import time

import cv2
from numpy import array
import numpy as np

import threading
import pygame

pygame.mixer.init()
sound_punch = pygame.mixer.Sound('sounds/punch.wav')
sound_kick = pygame.mixer.Sound('sounds/kick.wav')
sound_flying_kick = pygame.mixer.Sound('sounds/flyingkick.wav')
sound_ko = pygame.mixer.Sound('sounds/ko.wav')

SCREEN_WIDTH=1600 
SCREEN_HEIGHT=900

lock = threading.Lock()
animation_start={'flip':False,
                    'sound':None,                    
                    'frames':[{'body_points':[[134, 60], [134, 102], [111, 116], [157, 116], [93, 139], [176, 139], [120, 150], [157, 150], [125, 175], [148, 175], [120, 255], [157, 250], [120, 315], [157, 315]],'delay':10}]}
animation_stand={ 'flip':False,
                    'sound':None,
                    'frames':[{'body_points':[[133, 50], [133, 90], [104, 109], [158, 109], [99, 154], [163, 154], [94, 198], [167, 193], [113, 173], [143, 173], [108, 252], [148, 252], [108, 330], [148, 330]],'delay':10}]}
animation_standby={ 'flip':False,
                    'sound':None,
                    'frames':[{'body_points':[[133, 67], [123, 111], [98, 116], [138, 121], [108, 141], [158, 161], [138, 116], [183, 156], [108, 191], [128, 191], [98, 256], [143, 256], [88, 320], [148, 315]],'delay':10}]}
animation_punch={'flip':False,
                    'sound':sound_punch,
                  'frames':[{'body_points':[[133, 67], [123, 111], [98, 116], [138, 121], [108, 141], [158, 161], [138, 116], [183, 156], [108, 191], [128, 191], [98, 256], [143, 256], [88, 320], [148, 315]],'delay':50},
                            {'body_points':[[179, 75], [168, 118], [141, 118], [184, 129], [152, 135], [217, 129], [184, 118], [290, 124], [130, 194], [157, 205], [104, 264], [163, 275], [82, 328], [157, 328]],'delay':100}]}
animation_kick={'flip':False,
                'sound':sound_kick,                    
                'frames':[{'body_points':[[133, 67], [123, 111], [98, 116], [138, 121], [108, 141], [158, 161], [138, 116], [183, 156], [108, 191], [128, 191], [98, 256], [143, 256], [88, 320], [148, 315]],'delay':10},
                          {'body_points':[[37, 50], [48, 94], [26, 116], [70, 105], [32, 155], [92, 144], [54, 122], [114, 166], [70, 188], [92, 177], [70, 254], [126, 150], [70, 320], [126, 220]],'delay':30},
                          {'body_points':[[19, 64], [34, 111], [8, 132], [65, 116], [24, 163], [97, 148], [50, 132], [76, 132], [76, 200], [97, 174], [81, 257], [170, 153], [86, 320], [242, 137]],'delay':100}]}
animation_flying_kick={'flip':False, 
                        'sound':sound_flying_kick,                   
                        'frames':[  {'body_points':[[133, 67], [123, 111], [98, 116], [138, 121], [108, 141], [158, 161], [138, 116], [183, 156], [108, 191], [128, 191], [98, 256], [143, 256], [88, 320], [148, 315]],'delay':10},                                    
                                    {'body_points':[[76, 5], [78, 51], [53, 64], [101, 58], [66, 92], [127, 94], [94, 64], [129, 84], [92, 135], [112, 122], [64, 183], [156, 100], [94, 220], [130, 170]],'delay':100},
                                    {'body_points':[[19, -56], [34, -9], [8, 12], [65, -4], [24, 43], [97, 28], [50, 12], [76, 12], [76, 80], [97, 54], [30, 110], [170, 80], [100, 120], [242, 100]],'delay':200}]}

animation_dict = {'standby':animation_standby, 
                'kick':animation_kick, 
                'flying_kick':animation_flying_kick,
                'punch':animation_punch, 
                'start':animation_start,
                'stand':animation_stand}

posture_animation_map = {'stand':'standby', 'left_arm_up':'punch', 'right_arm_up':'punch', 'left_leg_up':'kick', 'right_leg_up':'flying_kick' }


def normalize_keypoint(points):
    points_res = np.array(points)
    min_h = min(points_res[:,0])
    min_w = min(points_res[:,1])
    body_h = max(points_res[:,0])-min_h
    body_w = max(points_res[:,1])-min_w
    points_res = np.ceil((points_res - np.array([min_h,min_w]))/np.array([body_h,body_w])*np.array([100,100]))
    
    return points_res


def flip_points(points, axis_x=118):
    points_res = np.array(points)   
    points_res = (points_res - np.array([axis_x,0]))*np.array([-1,1]) + np.array([axis_x,0])
    return points_res#.tolist()


class PkAnimator(object):
    def __init__(self, background_image_file):        
        self.background_image =cv2.imread(background_image_file)
        self.background_image = cv2.resize(self.background_image,(640,480))
        self.playground_image = copy.deepcopy(self.background_image)
        
        self.frame1 = None
        self.frame2 = None
        self.winner_text=''
        self.show_help_flag = True
        self.initialize()


    def initialize(self):        
        self.exit_flag = False
        
        self.player1_animation=None
        self.player2_animation=None
        self.player1_points=None       
        self.player2_points=None
        self.player1_offset=(120,100)
        self.player2_offset=(280,100)
        
        self.game_start_flag = False
        self.player1_ready = False
        self.player2_ready = False
        self.score1=0
        self.score2=0
        self.health1=100
        self.health2=100


    def set_player1_animation(self, animation_key):
        self.player1_animation = animation_dict[animation_key]

    def set_player2_animation(self, animation_key):
        self.player2_animation = animation_dict[animation_key]

    def show_help(self, flag):
        self.show_help_flag = flag

    def show_playground(self):
        lock.acquire()
        # 背景色
        cv2.rectangle(self.playground_image, (0, 0), (640, 480),(0,0,0),thickness=-1)
        self.playground_image = copy.deepcopy(self.background_image)
        
        self.playground_image=self.render_health_bar(self.health1,(60,0),(0,0,128))
        self.playground_image=self.render_health_bar(self.health2,(640- 260,0),(128,0,0))
        self.playground_image=self.render_score(self.score1,(0,0),(0,0,255))
        self.playground_image=self.render_score(self.score2,(640-60,0),(255,0,0))
                
        cv2.putText(self.playground_image, text=self.winner_text, org=(100,100), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=2,color=(0, 255, 0), thickness=5)
        if self.show_help_flag == True:
            cv2.putText(self.playground_image, text="START: Raise hands above head        EXIT: Press 'Esc'", org=(100,50), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,color=(0, 255, 0), thickness=1)
            cv2.putText(self.playground_image, text="Punch: Left or Right hand Up", org=(100,80), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,color=(0, 255, 0), thickness=1)
            cv2.putText(self.playground_image, text="Kick: Left leg Up", org=(100,110), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,color=(0, 255, 0), thickness=1)
            cv2.putText(self.playground_image, text="Flying Kick: Right leg Up", org=(100,140), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,color=(0, 255, 0), thickness=1)
            
        if self.player1_points is not None:
            pts1 = copy.deepcopy(self.player1_points)
            pts1 += np.array(self.player1_offset)
            self.playground_image=draw_stick_figure(self.playground_image, pts1,(0,0,255))
        if self.player2_points is not None:
            pts2 = copy.deepcopy(self.player2_points)
            pts2=flip_points(pts2)
            pts2 += np.array(self.player2_offset)           
            self.playground_image=draw_stick_figure(self.playground_image, pts2,(255,0,0))
        
        self.playground_image = cv2.resize(self.playground_image,(SCREEN_WIDTH,SCREEN_HEIGHT))
        
        y1=self.playground_image.shape[0]-self.frame1.shape[0]
        y2 = self.playground_image.shape[0]
        x1 = 0
        x2 = self.frame1.shape[1]
        player1_roi = self.playground_image[y1:y2, x1:x2]
        self.playground_image[y1:y2, x1:x2] = cv2.addWeighted(player1_roi,0,self.frame1,1,0)
        
        y1=self.playground_image.shape[0]-self.frame2.shape[0]
        y2 = self.playground_image.shape[0]
        x1 = self.playground_image.shape[1]-self.frame2.shape[1]
        x2 = self.playground_image.shape[1]
        player2_roi = self.playground_image[y1:y2, x1:x2]
        self.playground_image[y1:y2, x1:x2] = cv2.addWeighted(player2_roi,0,self.frame2,1,0)

        cv2.imshow("Playground",self.playground_image)
        cv2.waitKey(10)        
        lock.release()
        

    def render_health_bar(self,health,pos, color):
        self.playground_image=cv2.rectangle(self.playground_image,pos,(pos[0]+200,pos[1]+20),(64,64,64),-1)
        self.playground_image=cv2.rectangle(self.playground_image,pos,(pos[0]+int(200*(health/100)),pos[1]+20),color,-1)
        self.playground_image=cv2.putText(self.playground_image, text=str(health), org=(pos[0]+80,pos[1]+15), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,color=(128, 128, 128), thickness=2)
        return self.playground_image


    def render_score(self, score, pos, color):
        self.playground_image=cv2.rectangle(self.playground_image,pos,(pos[0]+60,pos[1]+40),(255,128,64),-1)
        self.playground_image=cv2.rectangle(self.playground_image,(pos[0]+2,pos[1]+2),(pos[0]+58,pos[1]+38),color,-1)
        self.playground_image=cv2.putText(self.playground_image, text=str(score), org=(pos[0]+10,pos[1]+30), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255,255,255), thickness=2)
        return self.playground_image


    def run(self):
        # t1 = threading.Thread(target=self.play_animation, args=(self.player1_animation,(0,0)))
        # t2 = threading.Thread(target=self.play_animation, args=(self.player2_animation,(150,0)))
        t1 = threading.Thread(target=self.play_animation_1)
        t1.setDaemon(True)
        t2 = threading.Thread(target=self.play_animation_2)
        t2.setDaemon(True)
        t1.start()        
        t2.start()
       
        
    def play_animation_1(self):             
        while self.exit_flag == False:
            if self.player1_animation is not None:
                sound = self.player1_animation['sound']   
                if sound is not None:
                    sound.play()
                for frame in self.player1_animation['frames']:
                    self.player1_points = frame['body_points']                    
                    time.sleep(frame['delay']/1000)
            time.sleep(0.01)  
        pass

    def play_animation_2(self):        
        while self.exit_flag == False:
            if self.player1_animation is not None:
                sound = self.player2_animation['sound']
                if sound is not None:
                    sound.play()        
                for frame in self.player2_animation['frames']:
                    self.player2_points = frame['body_points']
                    time.sleep(frame['delay']/1000)
            time.sleep(0.01)   
        pass


def draw_stick_figure(image, landmarks, color=(100, 33, 3), bg_color=(255, 255, 255)):
    image_width, image_height = image.shape[1], image.shape[0]
    landmark_point = []
    for index, landmark in enumerate(landmarks):
        landmark_x = min(int(landmark[0]), image_width - 1)
        landmark_y = min(int(landmark[1]), image_height - 1)
        landmark_point.append([index, (landmark_x, landmark_y)])

    # 修正腿根位置至腰部中点
    right_leg = landmark_point[8]  #左腰
    left_leg = landmark_point[9]   #右腰

    leg_x = int(int((right_leg[1][0] + left_leg[1][0])) / 2) #计算腰的横轴位置
    leg_y = int(int((right_leg[1][1] + left_leg[1][1])) / 2) #计算腰的纵轴位置

    #重置腰的位置
    landmark_point[9][1] = (leg_x, leg_y)
    landmark_point[8][1]= (leg_x, leg_y)

    # 返回值为头部的中心点，半径
    (face_x, face_y), face_radius = min_enclosing_face_circle(landmark_point)
    face_x = int(face_x)
    face_y = int(face_y)
    face_radius = int(face_radius)

    stick_radius01 = int(face_radius * (4 / 7))
    stick_radius02 = int(stick_radius01 * (2 / 4))
    stick_radius03 = int(stick_radius02 * (3 / 4))

    #
    draw_list = [3, 2, 9, 8,]

    # 画头
    cv2.circle(image, (face_x, face_y), face_radius, color, -1)

    for landmark_info in landmark_point:
        index = landmark_info[0]
        if index in draw_list:

            point01 = [p for p in landmark_point if p[0] == index][0]
            point02 = [p for p in landmark_point if p[0] == (index + 2)][0]
            point03 = [p for p in landmark_point if p[0] == (index + 4)][0]

            image = draw_stick(
                image,         #原图
                point01[1],    #3
                stick_radius01,
                point02[1],    #5
                stick_radius02,
                color=color,
                bg_color=bg_color,
            )

            image = draw_stick(
                image,
                point02[1],     #5
                stick_radius02,
                point03[1],     #7
                stick_radius03,
                color=color,
                bg_color=bg_color,
            )
    return image


def min_enclosing_face_circle(landmark_point):
    landmark_array = np.empty((0, 2), int)
    index_list = [0,1]
    for index in index_list:
        np_landmark_point = [np.array((landmark_point[index][1][0], landmark_point[index][1][1]))]
        landmark_array = np.append(landmark_array, np_landmark_point, axis=0)
    center, radius = cv2.minEnclosingCircle(points=landmark_array) # 寻找包裹轮廓的最小圆

    return center, radius


def draw_stick(
        image,
        point01,
        point01_radius,
        point02,
        point02_radius,
        color=(100, 33, 3),
        bg_color=(255, 255, 255),
):
    cv2.circle(image, point01, point01_radius, color, -1)
    cv2.circle(image, point02, point02_radius, color, -1)
    draw_list = []
    for index in range(2):  #计算圆上点的坐标
        rad = math.atan2(point02[1] - point01[1], point02[0] - point01[0]) # 计算弧度
        rad = rad + (math.pi / 2) + (math.pi * index)
        point_x = int(point01_radius * math.cos(rad)) + point01[0]  # math.cos()在此函数中传递的值以弧度为单位。
        point_y = int(point01_radius * math.sin(rad)) + point01[1]
        draw_list.append([point_x, point_y])

        point_x = int(point02_radius * math.cos(rad)) + point02[0]
        point_y = int(point02_radius * math.sin(rad)) + point02[1]
        draw_list.append([point_x, point_y])

    points = np.array((draw_list[0], draw_list[1], draw_list[3], draw_list[2]))
    cv2.fillConvexPoly(image, points=points, color=color)
    
    return image

