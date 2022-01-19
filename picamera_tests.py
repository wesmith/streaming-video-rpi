#!/usr/bin/env python3

# WESmith 01/18/22 run webcam and picam from 
# the picamera module on the rpi 4.

from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2
import time

# note: '0' ok for picam, '1' not working for webcam: wants LED pin
camera = PiCamera(0)
camera.resolution = (640, 480)
rawCapture = PiRGBArray(camera, size=(640, 480))
camera.framerate = 32

time.sleep(0.1)

for frame in camera.capture_continuous(rawCapture, format='bgr',
                                       use_video_port=True):
    image = frame.array
    cv2.imshow('picamera', image)

    key = cv2.waitKey(1) & 0xFF
    
    rawCapture.truncate(0)
    
    if key == ord('q'):
        break
