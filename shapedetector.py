import cv2

class ShapeDetector:
    def __init__(self):
        pass

    def detect(self, c):
        circle = False
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        if len(approx) > 5:
            circle = True
        return circle