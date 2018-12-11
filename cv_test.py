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

# def skalujKolor():
#     time.sleep(5.0)
#     avg_h = 0
#     avg_s = 0
#     avg_v = 0
#     i = 0
#     for _, row in enumerate(roi):
#         avg = np.average(row, 0)
#         avg_h += avg[0]
#         avg_s += avg[1]
#         avg_v += avg[2]
#         i+=1
#     avg_h /= i
#     avg_s /= i
#     avg_v /= i
#     print("HUE:{}, SAT:{}, VAL:{}".format(avg_h, avg_s, avg_v))
#     blueLower = (max(0,avg_h), max(0, avg_s - 50), max(0,avg_v - 50))
#     blueUpper = (min (255, avg_h), min(255, avg_s + 50), min(255, avg_v + 50))

# def translate(value, oldMin, oldMax, newMin=-100, newMax=100):
#     # Figure out how 'wide' each range is
#     oldRange = oldMax - oldMin
#     newRange = newMax - newMin
#     NewValue = (((value - oldMin) * newRange) / oldRange) + newMin
#     return int(NewValue)

        ######XDXDXD#####
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())
greenLower = (160,140,50)
greenUpper = (180,255,255)
pts = deque(maxlen=args["buffer"])
        #####DXDXDX######

usesPiCamera = True
cameraResolution = (640, 480)

# initialize the video stream and allow the cammera sensor to warmup
vs = VideoStream(usePiCamera=usesPiCamera, resolution=cameraResolution, framerate=60).start()
time.sleep(2.0)
# blueLower = (max(0,174), max(0, 217 - 50), max(0,185 - 50))
# blueUpper = (min (255, 174), min(255, 255 + 50), min(255, 85 + 50))
# colorTolerance = 10
paused = False
# roiSize = (6, 6) # roi size on the scaled down image (converted to HSV)
# detected = False

# initialize serial communication
ser = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=0.05)

while True:
    if not paused:
        frame = vs.read()
        
        height, width = frame.shape[0:2]
        scaleFactor = 4
        newWidth, newHeight = width//scaleFactor, height//scaleFactor
        resizedColor = cv2.resize(frame, (newWidth, newHeight), interpolation=cv2.INTER_CUBIC)


        ##############XDD###
        blurred = cv2.GaussianBlur(resizedColor, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, greenLower, greenUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None
        x = 0
        radius = 0
        if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
    
		    # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(resizedColor, (int(x), int(y)), int(radius),
                    (0, 255, 255), 2)
                cv2.circle(resizedColor, center, 5, (0, 0, 255), -1)
        # update the points queue
        pts.appendleft(center)
        # loop over the set of tracked points
        for i in range(1, len(pts)):
            # if either of the tracked points are None, ignore
            # them
            if pts[i - 1] is None or pts[i] is None:
                continue
    
            # otherwise, compute the thickness of the line and
            # draw the connecting lines
            # thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
            # cv2.line(resizedColor, pts[i - 1], pts[i], (0, 0, 255), thickness)
        x=int(x)
        radius=int(radius)
        print('x=')
        print(x)
        print('r=')
        print(radius)
        packet = '<{}, {}>'.format(x, radius)
        packetBytes = bytes(packet, 'utf-8')
        ser.write(packetBytes)
        # ser.read_all()   
        upscaledColor = cv2.resize(resizedColor, (width, height), interpolation=cv2.INTER_NEAREST)     
        cv2.imshow("resizedColor", upscaledColor)
        key = cv2.waitKey(1) & 0xFF
        ##############XDDD##

        # resizedColor_blurred = cv2.GaussianBlur(resizedColor, (5, 5), 0)
        # resizedHSV = cv2.cvtColor(resizedColor_blurred, cv2.COLOR_BGR2HSV)
        # roi = resizedHSV[newHeight//2 - roiSize[0]//2 : newHeight //2 + roiSize[0]//2, newWidth//2 - roiSize[1]//2 : newWidth//2 + roiSize[1]//2, :]
        # blueLowerWithTolerance = (blueLower[0] - colorTolerance,) + blueLower[1:]
        # blueUpperWithTolerance = (blueUpper[0] + colorTolerance,) + blueUpper[1:]
        # mask = cv2.inRange(resizedHSV, blueLowerWithTolerance, blueUpperWithTolerance)
        # cv2.erode(mask, None, iterations=5)
        # cv2.dilate(mask, None, iterations=5)
        # (_,contours, hierarchy) = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # boundingBoxes = []
        # biggestObject_BoundingBox = None
        # biggestObjectMiddle = None
        # if contours:
        #     largestContour = max(contours, key=cv2.contourArea)
        #     biggestObject_BoundingBox = cv2.boundingRect(largestContour)
        #     for i, contour in enumerate(contours):
        #         area = cv2.contourArea(contour)
        #         if area > ((newWidth * newHeight)/256):
        #             x,y,w,h = cv2.boundingRect(contour)
        #             boundingBoxes.append((x,y,w,h))
        # else:
        #     pass
        # upscaledColor = cv2.resize(resizedColor, (width, height), interpolation=cv2.INTER_NEAREST)
        # draw ROI on upscaled image
        # xROI, yROI = width//2 - roiSize[1]//2 * scaleFactor, height//2 - roiSize[0]//2 * scaleFactor
        # cv2.rectangle(upscaledColor, (xROI, yROI), (xROI + roiSize[0]*scaleFactor, yROI + roiSize[1]*scaleFactor), (0, 0, 0), thickness=3)
############################
        # hsv_conv_img = cv2.cvtColor(upscaledColor, cv2.COLOR_BGR2HSV)
        # bright_red_lower_bounds = (0, 100, 100)
        # bright_red_upper_bounds = (10, 255, 255)
        # bright_red_mask = cv2.inRange(hsv_conv_img, bright_red_lower_bounds, bright_red_upper_bounds)
        # dark_red_lower_bounds = (160, 100, 100)
        # dark_red_upper_bounds = (179, 255, 255)
        # dark_red_mask = cv2.inRange(hsv_conv_img, dark_red_lower_bounds, dark_red_upper_bounds)
        # # after masking the red #     packet = '<packet, {}, {}>'.format(scaled[0], scaled[1])
        #     packetBytes = bytes(packet, 'utf-8')
        #     ser.write(packetBytes)
        #     ser.read_all()shades out, I add the two images 
        # weighted_mask = cv2.addW#     packet = '<packet, {}, {}>'.format(scaled[0], scaled[1])
        #     packetBytes = bytes(packet, 'utf-8')
        #     ser.write(packetBytes)
        #     ser.read_all()eighted(bright_red_mask, 1.0, dark_red_mask, 1.0, 0.0)
        # # then the result is blu#     packet = '<packet, {}, {}>'.format(scaled[0], scaled[1])
        #     packetBytes = bytes(packet, 'utf-8')
        #     ser.write(packetBytes)
        #     ser.read_all()rred
        # blurred_mask = cv2.GaussianBlur(weighted_mask,(9,9),3,3)
        # # some morphological operations (closing) to remove small blobs 
        # erode_element = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        # dilate_element = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 8))
        # eroded_mask = cv2.erode(blurred_mask,erode_element)
        # dilated_mask = cv2.dilate(eroded_mask,dilate_element)
        # # on the color-masked, blurred and morphed image I apply the cv2.HoughCircles-method to detect circle-shaped objects 
        # detected_circles = cv2.HoughCircles(dilated_mask, cv2.HOUGH_GRADIENT, 1, 150, param1=100, param2=20, minRadius=20, maxRadius=200)
        # if detected_circles is not None:
        #     if not detected:
        #         skalujKolor()
        #         detected = True
        #     for circle in detected_circles[0, :]:
        #         cv2.circle(upscaledColor, (circle[0], circle[1]), circle[2], (0,255,0),thickness=3)
##############################
        # for boundingBox in boundingBoxes:
        #     x,y,w,h = boundingBox
        #     cv2.rectangle(resizedColor, (x, y), (x+w, y+h), (255, 255, 0), thickness=1)
        #     cv2.rectangle(upscaledColor, (x*scaleFactor, y*scaleFactor),
        #                 ((x+w)*scaleFactor, (y+h)*scaleFactor), (255, 255, 0), thickness=2)
        
        # if biggestObject_BoundingBox:
        #     x, y, w, h = biggestObject_BoundingBox
        #     biggestObjectMiddle = ((x+ w//2)*scaleFactor, (y + h//2)*scaleFactor)
        #     cv2.rectangle(resizedColor, (x, y), (x+w, y+h), (0, 0, 255), thickness=2)
        #     cv2.rectangle(upscaledColor, (x*scaleFactor, y*scaleFactor),
        #                     ((x+w)*scaleFactor, (y+h)*scaleFactor), (0, 0, 255), thickness=3)
        #     cv2.circle(upscaledColor, biggestObjectMiddle, 2, (255, 0, 0), thickness=2)
        #     screenMiddle = width//2, height//2
        #     distanceVector = tuple(map(lambda x, y: x - y, biggestObjectMiddle, screenMiddle))
        #     scaled = (translate(distanceVector[0], -width//2, width//2), translate(distanceVector[1], -height//2, height//2) )
        #     cv2.line(upscaledColor, screenMiddle, biggestObjectMiddle, (0, 0, 255))
        #     packet = '<packet, {}, {}>'.format(scaled[0], scaled[1])
        #     packetBytes = bytes(packet, 'utf-8')
        #     ser.write(packetBytes)
        #     ser.read_all()

        # cv2.imshow("video", upscaledColor)
        # cv2.imshow("roi", roi)
        # cv2.imshow("mask", mask)
        # modTolerances = False

    # handle keys 
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    # elif key == ord('a'):
    #     avg_h = 0
    #     avg_s = 0
    #     avg_v = 0
    #     i = 0
    #     for _, row in enumerate(roi):
    #         avg = np.average(row, 0)
    #         avg_h += avg[0]
    #         avg_s += avg[1]
    #         avg_v += avg[2]
    #         i+=1
    #     avg_h /= i
    #     avg_s /= i
    #     avg_v /= i
    #     print("HUE:{}, SAT:{}, VAL:{}".format(avg_h, avg_s, avg_v))
    #     blueLower = (max(0,avg_h), max(0, avg_s - 50), max(0,avg_v - 50))
    #     blueUpper = (min (255, avg_h), min(255, avg_s + 50), min(255, avg_v + 50))

    # loopEnd= time.time()
# cleanup

cv2.destroyAllWindows()
vs.stop()
