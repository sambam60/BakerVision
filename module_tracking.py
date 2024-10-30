import cv2
import mediapipe as mp
import time
import math
import numpy as np


class HandTracker():
    def __init__(self,static_mode=False,num_hands=6,min_detect_conf=0.5,min_track_conf=0.6):
        self.static_mode=static_mode
        self.num_hands=num_hands # number of hands to track
        self.min_detect_conf=min_detect_conf 
        self.min_track_conf=min_track_conf

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(self.static_mode,self.num_hands,
                                        self.min_detect_conf,self.min_track_conf)
        self.mp_drawer=mp.solutions.drawing_utils
        self.finger_tips=[4,8,12,16,20]

    def detect_hands(self,frame,should_draw=True):
        rgb_img=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        self.output=self.hands.process(rgb_img)

        if self.output.multi_hand_landmarks:
            for hand_points in self.output.multi_hand_landmarks:
                if should_draw:
                    self.mp_drawer.draw_landmarks(frame,hand_points,
                                               self.mp_hands.HAND_CONNECTIONS)

        return frame

    def get_hand_points(self,frame,hand_idx=0,should_draw=True):
        x_coords=[]
        y_coords=[]
        box=[]
        self.points_list=[]
        if self.output.multi_hand_landmarks:
            curr_hand=self.output.multi_hand_landmarks[hand_idx]
            for idx,landmark in enumerate(curr_hand.landmark):
                height,width,channels=frame.shape
                x_pos,y_pos=int(landmark.x*width),int(landmark.y*height)
                x_coords.append(x_pos)
                y_coords.append(y_pos)
                self.points_list.append([idx,x_pos,y_pos])
                if should_draw:
                    cv2.circle(frame,(x_pos,y_pos),5,(255,0,255),cv2.FILLED)

            x_min,x_max=min(x_coords),max(x_coords)
            y_min,y_max=min(y_coords),max(y_coords)
            box=x_min,y_min,x_max,y_max

            if should_draw:
                cv2.rectangle(frame,(x_min-20,y_min-20),(x_max+20,y_max+20),
                              (0,255,0),2)

        return self.points_list,box

    def check_fingers(self):
        raised=[]

        if self.points_list:
            #check thumb 
            if self.finger_tips[0]<len(self.points_list) and self.finger_tips[0]-1<len(self.points_list):
                if self.points_list[self.finger_tips[0]][1]>self.points_list[self.finger_tips[0]-1][1]:
                    raised.append(1)
                else:
                    raised.append(0)

            #other fingers
            for i in range(1,5):
                if self.finger_tips[i]<len(self.points_list) and self.finger_tips[i]-2<len(self.points_list):
                    if self.points_list[self.finger_tips[i]][2]<self.points_list[self.finger_tips[i]-2][2]:
                        raised.append(1)
                    else:
                        raised.append(0)

        return raised

    def calc_distance(self,point1,point2,frame,should_draw=True,radius=15,thickness=3):
        x1,y1=self.points_list[point1][1:]
        x2,y2=self.points_list[point2][1:]
        center_x,center_y=(x1+x2)//2,(y1+y2)//2

        if should_draw:
            cv2.line(frame,(x1,y1),(x2,y2),(255,0,255),thickness)
            cv2.circle(frame,(x1,y1),radius,(255,0,255),cv2.FILLED)
            cv2.circle(frame,(x2,y2),radius,(255,0,255),cv2.FILLED)
            cv2.circle(frame,(center_x,center_y),radius,(0,0,255),cv2.FILLED)
        dist=math.hypot(x2-x1,y2-y1)

        return dist,frame,[x1,y1,x2,y2,center_x,center_y]


def run_demo():
    prev_time=0
    curr_time=0
    video=cv2.VideoCapture(1)
    tracker=HandTracker()
    while True:
        success,frame=video.read()
        frame=tracker.detect_hands(frame)
        points,box=tracker.get_hand_points(frame)
        if len(points)!=0:
            print(points[4])   # print something 

        curr_time=time.time()
        fps=1/(curr_time-prev_time)
        prev_time=curr_time

        cv2.putText(frame,str(int(fps)),(10,70),cv2.FONT_HERSHEY_PLAIN,3,
                    (255,0,255),3)

        cv2.imshow("Camera Feed",frame)
        cv2.waitKey(1)


if __name__=="__main__":
    run_demo()
