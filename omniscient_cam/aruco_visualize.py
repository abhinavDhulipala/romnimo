import numpy as np
import cv2
import cv2.aruco as aruco

print("Finding Camera")
cap = cv2.VideoCapture(1) 
marker_size = .1    # Add to have the length of one side of the marker, in meters
aruco_dictionary = cv2.aruco.DICT_4X4_1000    # OpenCV Aruco dictionary
camera_matrix = np.array([[1382.905, 0, 1005.053],
                            [0, 1379.942, 541.149],
                            [0, 0, 1]])
dist_coeff = np.array([.118, -.188, .004, .002, .134])

while(True):
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_1000)
    arucoParameters = aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(
        gray, aruco_dict, parameters=arucoParameters)
    frame = aruco.drawDetectedMarkers(frame, corners)
    if ids is not None:
        rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_size, camera_matrix, dist_coeff)
        for i in range(len(ids)):
            aruco.drawAxis(frame, camera_matrix, dist_coeff, rvec[i], tvec[i], 0.1)
    cv2.imshow('Display', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
