import numpy as np
import cv2
import cv2.aruco as aruco
import time
import math

class Aruco_processor:
    def __init__(self, origin_mark=10):
        self.marker_size = .1    
        self.aruco_dictionary = aruco.Dictionary_get(cv2.aruco.DICT_4X4_1000)
        self.aruco_parameters = aruco.DetectorParameters_create()
        self.camera_matrix = np.array([[1382.9051260696745, 0, 1005.0528067934058],
                                    [0, 1379.9417912461442, 541.1493795515057],
                                    [0, 0, 1]])
        self.dist_coeff = np.array([0.11798477738494176, -0.1883468380171588, 0.0035953735855806007, 0.0024175441482927108, 0.13373412015090186])
        self.origin_marker = origin_mark

    # Switch the coordinate frame
    def inverse_frame(self, rvec, tvec):
        R, _ = cv2.Rodrigues(rvec)
        R = np.matrix(R).T
        invTvec = np.dot(-R, np.matrix(tvec))
        invRvec, _ = cv2.Rodrigues(R)
        return invRvec, invTvec

    # Get the relative position of one marker in the others frame
    def relative_position(self, rvec1, tvec1, rvec2, tvec2):
        rvec1, tvec1 = rvec1.reshape((3, 1)), tvec1.reshape((3, 1))
        rvec2, tvec2 = rvec2.reshape((3, 1)), tvec2.reshape((3, 1))
        invRvec, invTvec = self.inverse_frame(rvec2, tvec2)
        origin_rvec, origin_tvec = self.inverse_frame(invRvec, invTvec)
        composed = cv2.composeRT(rvec1, tvec1, invRvec, invTvec)
        composedRvec, composedTvec = composed[0], composed[1]
        composedRvec = composedRvec.reshape((3, 1))
        composedTvec = composedTvec.reshape((3, 1))
        return composedRvec, composedTvec   

    def get_g(self, rvec, tvec):
        g_matrix = np.identity(4)
        rmat = cv2.Rodrigues(rvec)[0]
        g_matrix[:3, :3] = rmat
        g_matrix[:3, 3] = tvec
        return np.linalg.inv(g_matrix)

        # def get_idxs(self, ids, ms):
    #     idxs = np.zeros(len(ms))
    #     for i in range(len(ids)):
    #         for j in range(len(ms)):
    #             if ids[i] == ms[j]:
    #                 idxs[j] = i 
    #     return idxs


    def get_marker_transforms(self, frame, origin_id=10):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = aruco.detectMarkers(gray, self.aruco_dictionary, parameters=self.aruco_parameters)
        if ids is None:
            print("No markers")
            return None, None, None
        rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(corners, self.marker_size, self.camera_matrix, self.dist_coeff)
        origin_idx = np.where(np.array(ids) == origin_id)
        print(origin_idx)
        if len(origin_idx) == 0:
            print("Origin is not in view")
            return None, None, None
        new_rvecs = []
        new_tvecs = []
        for i in range(len(ids)):
            r, t = self.relative_position(rvec[origin_idx[0][0]], tvec[origin_idx[0][0]], rvec[i], tvec[i])
            new_rvecs.append(r)
            new_tvecs.append(t)
        return ids, new_rvecs, new_tvecs

    def get_marker_coords_by_id(self, frame, id_num, origin_id=10):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = aruco.detectMarkers(gray, self.aruco_dictionary, parameters=self.aruco_parameters)
        if ids is None:
            print("No markers")
            return None
        rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(corners, self.marker_size, self.camera_matrix, self.dist_coeff)
        origin_idx = -1
        id_idx = -1
        ids = np.array(ids)[:, 0]
        for i in range(len(ids)):
            if ids[i] == origin_id:
                origin_idx = i
            if ids[i] == id_num:
                id_idx = i
        if origin_idx < 0 or id_idx < 0:
            print("Origin or id is not in view")
            return None
        g_ac = self.get_g(rvec[origin_idx], tvec[origin_idx])
        t_c = np.array([tvec[id_idx][0][0], tvec[id_idx][0][1], tvec[id_idx][0][2], 1])
        return g_ac @ t_c
    
    def rvec_to_deg(self, rveca, rvecb):
        r_ca = cv2.Rodrigues(rveca)[0]
        r_cb = cv2.Rodrigues(rvecb)[0]

        r_ab = r_ca.T @ r_cb

        theta_x = math.atan2(r_ab[2,1], r_ab[2,2]) * 180 / math.pi 
        theta_y = math.atan2(-r_ab[2,0], math.sqrt(r_ab[2,1]**2 + r_ab[2,2]**2)) * 180 / math.pi
        theta_z = math.atan2(r_ab[1,0], r_ab[0,0]) * 180 / math.pi

        return theta_z
        

    def get_marker_orientation_by_id(self, frame, id_num, origin_id=10):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = aruco.detectMarkers(gray, self.aruco_dictionary, parameters=self.aruco_parameters)
        if ids is None:
            print("No markers")
            return None
        rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(corners, self.marker_size, self.camera_matrix, self.dist_coeff)
        origin_idx = -1
        id_idx = -1
        ids = np.array(ids)[:, 0]
        for i in range(len(ids)):
            if ids[i] == origin_id:
                origin_idx = i
            if ids[i] == id_num:
                id_idx = i
        if origin_idx < 0 or id_idx < 0:
            print("Origin or id is not in view")
            return None
        return self.rvec_to_deg(rvec[origin_idx], rvec[id_idx])

    def marker_to_grid(self, tvec):
        if tvec is None:
            return None
        return np.array([round(tvec[0] / .2127), round(tvec[1] / .4647)])
    
    def get_id_pos(self, frame, id):
        return self.marker_to_grid(self.get_marker_coords_by_id(frame, id))


    # Call to get the car position
    def get_car_pos(self, frame):
        return self.get_id_pos(frame, 16)

    # Call to get the car orientation
    def get_car_deg(self, frame):
        return self.get_marker_orientation_by_id(frame, 16)

    def get_crash_tiles(self, frame):
        crashes_pose = []
        crashes_pose.append(self.get_id_pos(frame, 13))
        crashes_pose.append(self.get_id_pos(frame, 14))
        crashes_pose.append(self.get_id_pos(frame, 15))
        return list(filter(lambda e: e is not None, crashes_pose))



if __name__ == '__main__':
    print("Finding cam")
    cap = cv2.VideoCapture(1) 
    print("cam found")
    ap = Aruco_processor()
    while(True):
        time.sleep(.5)
        ret, frame = cap.read()
        t1 = ap.get_marker_coords_by_id(frame, 16)
        print("t1")
        if t1 is not None:
            print(ap.marker_to_grid(t1))
        print("orientation")
        print(ap.get_marker_orientation_by_id(frame, 16))
    cap.release()
    cv2.destroyAllWindows()

