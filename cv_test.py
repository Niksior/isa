# parts of the code are based on https://www.pyimagesearch.com/2016/01/04/unifying-picamera-and-cv2-videocapture-into-a-single-class-with-opencv/
# before rnning the code install imutils for python3 (pip3 install imutils)

import time
from imutils.video import VideoStream
from collections import deque
import serial
import imutils
import numpy as np
import cv2
import argparse
import math
from shapedetector import ShapeDetector

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())
redLower = (130,140,50)
redUpper = (180,255,255)
pts = deque(maxlen=args["buffer"])
usesPiCamera = True
cameraResolution = (640, 480)
vs = VideoStream(usePiCamera=usesPiCamera, resolution=cameraResolution, framerate=32).start()
time.sleep(2.0)
ser = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=0.05)

while True:
    frame = vs.read()
    height, width = frame.shape[0:2]
    scaleFactor = 4
    newWidth, newHeight = width//scaleFactor, height//scaleFactor
    resizedColor = cv2.resize(frame, (newWidth, newHeight), interpolation=cv2.INTER_CUBIC)
    blurred = cv2.GaussianBlur(resizedColor, (3, 3), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, redLower, redUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    sd = ShapeDetector()

    center = None
    x = 0
    radius = 0
    if len(cnts) > 0:
        for c in cnts:
            circle = sd.detect(c)
            kolo = (4*math.pi*circle) / math.pow((2*math.pi*radius), 2)
            if(kolo > 0.8):
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                x = int(x)
                y = int(y)
                radius = int(radius)
                if radius > 10:
                    cv2.circle(resizedColor, (int(x), int(y)), int(radius),
                        (0, 255, 255), 2)
                x=int(x)
                radius=int(radius)
                packet = '<{}, {}>'.format(x, radius)
                packetBytes = bytes(packet, 'utf-8')
                ser.write(packetBytes)
                ser.readall()
                    
    upscaledColor = cv2.resize(resizedColor, (width, height), interpolation=cv2.INTER_NEAREST)
    hsv2 = cv2.resize(hsv, (width, height), interpolation=cv2.INTER_NEAREST)  
    cv2.imshow('mask', cv2.resize(mask, (width, height), interpolation=cv2.INTER_NEAREST)  )
    cv2.imshow('hsv',hsv2)
    cv2.imshow("window", upscaledColor)
    key = cv2.waitKey(1) & 0xFF

cv2.destroyAllWindows()
vs.stop()
