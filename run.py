import numpy as np
import sys
import cv2
from animation import PkAnimator, SCREEN_WIDTH,SCREEN_HEIGHT,sound_ko, posture_animation_map
import time
from mmpose.apis import (inference_top_down_pose_model, init_pose_model,
                         process_mmdet_results, vis_pose_result)
try:
    from mmdet.apis import inference_detector, init_detector
    has_mmdet = True
except (ImportError, ModuleNotFoundError):
    has_mmdet = False

device = 'cuda:0'
det_config = 'configs/yolox_tiny_8x8_300e_coco.py'
det_checkpoint = 'checkpoints/yolox_tiny_8x8_300e_coco_20210806_234250-4ff3b67e.pth'

g_body_detector = init_detector(det_config, det_checkpoint, device=device.lower())
# build the pose model from a config file and a checkpoint file
pose_config = 'configs/hrnet_w32_coco_256x192.py'
pose_checkpoint = 'checkpoints/hrnet_w32_coco_256x192-c78dce93_20200708.pth'
g_body_aligner = init_pose_model(
    pose_config, pose_checkpoint, device=device.lower())

dataset = g_body_aligner.cfg.data['test']['type']


font = cv2.FONT_HERSHEY_SIMPLEX
STDHEIGHT = 600

score_dict = {'standby':0, 'punch':1, 'kick':2, 'flying_kick':3}


def get_pose_results(img):
    return_value = None
    
    mmdet_results = inference_detector(g_body_detector, img)
    # keep the person class bounding boxes.
    #person_results = process_mmdet_results(mmdet_results, 1)
    rects = process_mmdet_results(mmdet_results, 1)
            
    if len(rects) > 0:
        pose_results, returned_outputs = inference_top_down_pose_model(
        g_body_aligner,
        img,
        rects,
        #bbox_thr=0.3
        bbox_thr=0.66, #!!!important-lucy  
        format='xyxy',
        dataset=dataset,
        return_heatmap=False,
        outputs=None)        
        
        if len(pose_results) > 0:
            return_value = pose_results            
    
    return return_value


def get_body_points(pose_results):
        return_value = None               
        

        if pose_results is not None and np.amin(pose_results[0]['keypoints'][...,2])>0.5:            
            pose = pose_results[0]['keypoints'][...,:2]
            return pose.tolist()
        
        return return_value


def get_normalized_pose(frame):
    rt_pose = None

    pose_results = get_pose_results(frame)  
    if pose_results is not None:
        frame = vis_pose_result(
            g_body_aligner,
            frame,
            pose_results,
            dataset=dataset,
            kpt_score_thr=0.3,
            radius=4,
            thickness=1,
            show=False)
        
        pose = get_body_points(pose_results)
        if pose is not None:
            rt_pose = normalize_keypoint(pose)

    return frame, rt_pose


def normalize_keypoint(points):
    points_res = np.array(points)
    min_h = min(points_res[:,0])
    min_w = min(points_res[:,1])
    body_h = max(points_res[:,0])-min_h
    body_w = max(points_res[:,1])-min_w
    points_res = np.ceil((points_res - np.array([min_h,min_w]))/np.array([body_h,body_w])*np.array([100,100]))
    return points_res


def check_player_posture(pose):
    status = 'stand'
    if pose[9][1] < pose[0][1]:
        status='left_hand_above_head'
    elif pose[10][1] < pose[0][1]:
        status = 'right_hand_above_head'
    elif pose[15][1] < 95:
        status = 'left_leg_up'       
    elif pose[16][1] < 95:
        status = 'right_leg_up'
    elif pose[9][1] < 25:
        status = 'left_arm_up'
    elif pose[10][1] < 25:
        status = 'right_arm_up'
    else:
        status = 'stand'
      
    return status


def resize_frame(frame):
    resize_rate = STDHEIGHT / frame.shape[0]
    resized_frame = cv2.resize(frame,(int(frame.shape[1]*resize_rate),STDHEIGHT))
    return resized_frame

def render_number(frame, pose_type):
    textSize = 2
    textThick = 3
    color = (0, 255, 0)
    return cv2.putText(frame, str(pose_type), (30, 80), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, textSize, color, textThick)



pk_animator = PkAnimator('background/back_pk.jpg')    
pk_animator.set_player1_animation('standby')
pk_animator.set_player2_animation('standby')
pk_animator.run()

cam = cv2.VideoCapture(0) #'wushu.mp4'
while cam.isOpened():
    #t_start=time.time()
   
    flag, frame = cam.read()
    if not flag:
        break   

    if pk_animator.player1_ready == False:
        pk_animator.set_player1_animation('stand')
    else:
        pk_animator.set_player1_animation('standby')

    if pk_animator.player2_ready == False:
        pk_animator.set_player2_animation('stand')
    else:
        pk_animator.set_player2_animation('standby')


    color = (255, 255, 255)
    bg_color = (100, 33, 3)
    frame = resize_frame(frame)
    image = frame
    img_shape = image.shape            #Image Shape：return[rows，columns]
    img_height = img_shape[0]          #height（rows）
    img_width = img_shape[1]           #width（columns）
          
    a=0 # x start
    b=int(img_height) # x end
    c=0 # y start
    d=int(img_width/2) # y end
    crop_img_1 = image[a:b,c:d]   #Crop Image
    
    a=0
    b=int(img_height)
    c=int(img_width/2)
    d=int(img_width)
    crop_img_2 = image[a:b,c:d]    
    
    frame=crop_img_1
    frame=resize_frame(frame)
    
    new_posture ='standby'
    
    frame, pose = get_normalized_pose(frame)
    if pose is not None:
        new_posture = check_player_posture(pose)
        if pk_animator.game_start_flag == True:                              
            if new_posture in posture_animation_map:                    
                pk_animator.set_player1_animation(posture_animation_map[new_posture])
                pk_animator.score1 += score_dict[posture_animation_map[new_posture]]
                if pk_animator.score1 >100:
                    pk_animator.score1 = 100
                pk_animator.health1 = 100-pk_animator.score2
                pk_animator.health2 = 100-pk_animator.score1
        else:
            if new_posture in ('left_hand_above_head','right_hand_above_head'):
                pk_animator.player1_ready =True
                pk_animator.set_player1_animation('standby')
            if pk_animator.player1_ready==True and pk_animator.player2_ready == True:
                pk_animator.game_start_flag = True
                pk_animator.winner_text=''
                pk_animator.show_help(False)

    k=frame.shape[1]/frame.shape[0]
    pk_animator.frame1 = cv2.resize(frame, (int(450*k),450))   #450
        
#########################################################  
    
    frame2=crop_img_2
    frame2=resize_frame(frame2)
    new_posture =0
    frame2, pose2 = get_normalized_pose(frame2)
    if pose2 is not None:
        new_posture = check_player_posture(pose2)
        if pk_animator.game_start_flag == True:      
            if new_posture in posture_animation_map:
                pk_animator.set_player2_animation(posture_animation_map[new_posture])
                pk_animator.score2 += score_dict[posture_animation_map[new_posture]]
                if pk_animator.score2 > 100:
                    pk_animator.score2=100
                pk_animator.health1 = 100-pk_animator.score2
                pk_animator.health2 = 100-pk_animator.score1                   
        else:
            if new_posture in ('left_hand_above_head','right_hand_above_head'):
                pk_animator.player2_ready =True
                pk_animator.set_player2_animation('standby')
            if pk_animator.player1_ready==True and pk_animator.player2_ready == True:
                pk_animator.game_start_flag = True
                pk_animator.winner_text=''
                pk_animator.show_help(False)
                
    
    pk_animator.frame2 =cv2.resize(frame2, (int(450*k),450))
    
    if pk_animator.health1<=0:
        pk_animator.winner_text='Player2 Wins!!!'
        sound_ko.play()
        pk_animator.initialize()
    if pk_animator.health2<=0:
        pk_animator.winner_text='Player1 Wins!!!'
        sound_ko.play()
        pk_animator.initialize()

    #print(time.time()-t_start)
    k=cv2.waitKey(1)
    if k==ord("q") or k== 27:   #27:"Esc"
        pk_animator.exit_flag = True
        break

    pk_animator.show_playground()

sys.exit()