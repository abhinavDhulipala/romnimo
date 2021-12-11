import numpy as np
import cv2
import cv2.aruco as aruco

cap = cv2.VideoCapture(0) # TODO: Make work with USB cam

while(True):
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_1000)
    arucoParameters = aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(
        gray, aruco_dict, parameters=arucoParameters)
    frame = aruco.drawDetectedMarkers(frame, corners)
    cv2.imshow('Display', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()

# Takes a stream, finds aruco maker poses in each frame and publishes as a dictionary
def publishPoses(cam):
    cap = cv2.VideoCapture(cam)
    while(True):
        ret, frame = cap.read()



if __name__ == '__main__':
    publishPoses(0)    #TODO: Make work with USB cam   