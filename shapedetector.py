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

    def detect2(self, c):
        circle = cv2.HoughCircles(c, cv2.HOUGH_GRADIENT, 3, 100)
        print(circle)
        if circle is not None:
            return True
        return False