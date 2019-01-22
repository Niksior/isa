import cv2
import math

class ShapeDetector:
    def __init__(self):
        pass

    def detect(self, c):
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        x = int(x)
        y = int(y)
        radius = int(radius)
        area = int(cv2.contourArea(c))
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        if(len(approx) > 5):
            kolo = (4*math.pi*area) / math.pow((2*math.pi*radius), 2)
            if(kolo > 0.7):
                return True
        return False