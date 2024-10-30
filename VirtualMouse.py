import cv2
import numpy as np
import HandTrackingModule as htm
import time
import mouse
import autopy.mouse
from playsound import playsound
import os
import rumps
import threading

#User interface
from tkinter import *
import customtkinter


import sys

class HandTrackingApp(rumps.App):
    def __init__(self):
        super(HandTrackingApp, self).__init__(name='Virtual Mouse', icon='./Hand.png')

        # Define instance variables
        self.base_dir = os.path.dirname(__file__)
        self.file_path_left = os.path.join(self.base_dir, './focus_change_keyboard.caf')
        self.file_path_right = os.path.join(self.base_dir, './focus_change_small.caf')
        self.file_path_start = os.path.join(self.base_dir, './jbl_begin.caf')
        self.file_path_double = os.path.join(self.base_dir, './focus_change_large.caf')
        self.file_path_webcam = os.path.join(self.base_dir, './jbl_cancel.caf')

        self.wCam, self.hCam = 1920, 1080
        self.frameR = 380  # Frame Reduction
        self.smoothening = 7

        self.pTime = 0
        self.plocX, self.plocY = 0, 0
        self.clocX, self.clocY = 0, 0

        self.current_camera_index = 0  # Default camera index
        self.cap = cv2.VideoCapture(self.current_camera_index)

        self.cap.set(3, self.wCam)
        self.cap.set(4, self.hCam)
        self.detector = htm.handDetector(maxHands=1)
        self.wScr, self.hScr = autopy.screen.size()

        self.menu = [
            rumps.MenuItem('Start hand tracking', callback=self.Actual_App),
            rumps.MenuItem('Cycle Webcam', callback=self.add_webcam_index),
            rumps.MenuItem('Reset Webcam', callback=self.reset_webcam_index),
            rumps.MenuItem('Stop Hand Tracking', callback=self.quit),
        ]

        self.running = False  # Flag to indicate whether the app is running

    def add_webcam_index(self, _):
        try:
            playsound(self.file_path_webcam)
            self.cap.release()
            self.cap = cv2.VideoCapture(self.current_camera_index + 1)
        except Exception as e:
            print(f"Error in add_webcam_index: {e}")

    def reset_webcam_index(self, _):
        try:
            playsound(self.file_path_webcam)
            self.cap.release()
            self.cap = cv2.VideoCapture(0)
        except Exception as e:
            print(f"Error in reset_webcam_index: {e}")

    def Actual_App(self, _):
        try:
            playsound(self.file_path_start)
            if not self.running:
                self.running = True
                thread = threading.Thread(target=self.run_actual_app)
                thread.start()
        except Exception as e:
            print(f"Error in Actual_App: {e}")

    def run_actual_app(self):
        try:
            while self.running:
                # 1. Find hand Landmarks
                success, img = self.cap.read()
                img = self.detector.findHands(img)
                lmList, bbox = self.detector.findPosition(img)

                # 2. Get the tip of the index and middle fingers
                if len(lmList) != 0:
                    x1, y1 = lmList[8][1:]
                    x2, y2 = lmList[12][1:]

                # 3. Check which fingers are up
                fingers = self.detector.fingersUp()
                cv2.rectangle(img, (self.frameR, self.frameR), (self.wCam - self.frameR, self.hCam - self.frameR),
                              (255, 0, 255), 2)

                # Only Thumb Finger: Moving Mode
                if len(fingers) >= 3 and fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and \
                        fingers[4] == 0:
                    # 5. Convert Coordinates
                    x3 = np.interp(x1, (self.frameR, self.wCam - self.frameR), (0, self.wScr))
                    y3 = np.interp(y1, (self.frameR, self.hCam - self.frameR), (0, self.hScr))

                    # 6. Smoothen Values
                    self.clocX = self.plocX + (x3 - self.plocX) / self.smoothening
                    self.clocY = self.plocY + (y3 - self.plocY) / self.smoothening

                    # 7. Move Mouse
                    autopy.mouse.move(self.wScr - self.clocX, self.clocY)
                    cv2.circle(img, (x1, y1), 15, (0, 128, 255), cv2.FILLED)
                    self.plocX, self.plocY = self.clocX, self.clocY

                # Both Thumb and index fingers are up: Left Clicking Mode
                if len(fingers) >= 3 and fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and \
                        fingers[4] == 0:
                    # 9. Find distance between fingers
                    length, img, lineInfo = self.detector.findDistance(4, 8, img)  # Use thumb (4) and index (8) fingers
                    # 10. Click mouse if distance short

                    if length < 45:
                        cv2.circle(img, (lineInfo[2], lineInfo[1]),
                                   7, (0, 255, 0), cv2.FILLED)
                        playsound(self.file_path_left)
                        autopy.mouse.click()

                # Right click when middle and index close
                if len(fingers) >= 3 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
                    # 9. Find distance between fingers
                    length, img, lineInfo = self.detector.findDistance(8, 12, img)  # Use index (8) and middle (12) fingers
                    # 10. Click mouse if distance short

                    if length < 50:
                        cv2.circle(img, (lineInfo[2], lineInfo[1]),
                                   7, (0, 255, 0), cv2.FILLED)
                        playsound(self.file_path_right)
                        mouse.click(button="right")

                # Double click when thumb close to index WHILE middle finger is up
                if len(fingers) >= 3 and fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and \
                        fingers[4] == 0:
                    length, img, lineInfo = self.detector.findDistance(4, 8, img)  # Use index (8) and middle (12) fingers
                    # 10. Click mouse if distance short

                    if length < 50:
                        cv2.circle(img, (lineInfo[2], lineInfo[1]),
                                   7, (0, 255, 0), cv2.FILLED)
                        playsound(self.file_path_double)
                        mouse.double_click(button='left')

                if len(fingers) >= 3 and fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and \
                        fingers[4] == 0:
                    mouse.wheel(delta=3)
                elif len(fingers) >= 3 and fingers[0] == 0 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and \
                        fingers[4] == 1:
                    mouse.wheel(delta=-3)



                if cv2.waitKey(1) & 0xFF == ord('q'):
                    # Release the camera when the loop is terminated
                    self.cap.release()
                    cv2.destroyAllWindows()
                    self.running = False
                    break
        except Exception as e:
            print(f"Error in run_actual_app: {e}")
        finally:
            # Release resources when the thread is terminated
            self.cap.release()
            cv2.destroyAllWindows()
            self.running = False

    def quit(self, _):
        # Callback to handle quitting the application
        self.running = False




app = HandTrackingApp()
app.run()
