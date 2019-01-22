import cv2

class ShapeDetector:
    def __init__(self):
        pass

    def detect(self, c):
        area = int(cv2.contourArea(c))
        circle = area
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.01 * peri, True)
        return area;