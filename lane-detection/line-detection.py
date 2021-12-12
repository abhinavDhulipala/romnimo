# Line Detection
import cv2
import numpy as np
import math
import time

# Returns a full line to be drawn on the image with starting and ending coordinates
def get_full_line(min_line, y_max, x_max, is_horizontal):
	x1, y1, x2, y2 = min_line[0], min_line[1], min_line[2], min_line[3]
	slope = (y2 - y1)/(x2 - x1)
	b = y1 - slope * x1
	x_bottom, y_bottom = math.floor(-b/slope), 0
	x_top, y_top = math.floor((y_max-b)/slope), y_max
	distance_to_vertical = None
	if not is_horizontal:
		y_coord = y_max - 300
		distance_to_vertical = round(abs((y_coord - b)/slope - x_max/2))
	if is_horizontal:
		return [x_bottom, math.floor(y_bottom*1), x_top, math.floor(y_top * 0.9)]
	else:
		return [math.floor(x_bottom*0.95), y_bottom, math.floor(x_top*1.05), y_top], distance_to_vertical

def get_vertical_edge(SRC_PATH):
	img = cv2.imread(SRC_PATH)
	print("Length (y) of image in pixels: %d", len(img))
	print("Width (x) of image in pixels: %d", len(img[0]))
	x_max = len(img[0])
	y_max = len(img)
	center_line = [x_max/2, 0, x_max/2, y_max]
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

	kernel_size = 17
	blur_gray = cv2.GaussianBlur(gray,(kernel_size, kernel_size),0)

	low_threshold = 50
	high_threshold = 150
	edges = cv2.Canny(blur_gray, low_threshold, high_threshold)

	rho = 500
	theta = (np.pi / 180) * 2
	threshold = 15
	min_line_length = 50
	max_line_gap = 20
	line_image = np.copy(img) * 0
	line_image_follow = np.copy(img) * 0

	lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]), min_line_length, max_line_gap)
	min_line = None
	min_dist = 999999999

	n = len(lines)
	print("Number of lines detected:%d", n)
	for i in range(n):
		print(lines[i])
		for x1,y1,x2,y2 in lines[i]:
			xy_avg = abs((x1 + x2)/2 - x_max/2 + y1)
			if min_dist > xy_avg and (abs(y1 - y2) > 40):
				min_dist = xy_avg
				min_line = [x1, y1, x2, y2]
			cv2.line(line_image,(x1,y1),(x2,y2),(255,0,0),5)

	print(min_line)
	full_line, distance_to_vertical = get_full_line(min_line, y_max, x_max, False)
	lines_edges = cv2.addWeighted(img, 0.8, line_image, 1, 0)
	cv2.line(line_image_follow,(full_line[0],full_line[1]),(full_line[2],full_line[3]),(255,0,0),20)
	line_follow = cv2.addWeighted(img, 0.8, line_image_follow, 1, 0)
	cv2.imwrite('src1.png', lines_edges)
	cv2.imwrite('src2.png', line_follow)
	print(distance_to_vertical)
	return distance_to_vertical


def get_horizontal_edge(SRC_PATH):
	img = cv2.imread(SRC_PATH)
	print("Length (y) of image in pixels: %d", len(img))
	print("Width (x) of image in pixels: %d", len(img[0]))
	x_max = len(img[0])
	y_max = len(img)
	center_line = [x_max/2, 0, x_max/2, y_max]
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

	kernel_size = 17
	blur_gray = cv2.GaussianBlur(gray,(kernel_size, kernel_size),0)

	low_threshold = 50
	high_threshold = 150
	edges = cv2.Canny(blur_gray, low_threshold, high_threshold)

	rho = 500
	theta = (np.pi / 180) * 2
	threshold = 15
	min_line_length = 50
	max_line_gap = 20
	line_image = np.copy(img) * 0
	line_image_follow = np.copy(img) * 0

	lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]), min_line_length, max_line_gap)
	min_line = None
	min_dist = -1

	n = len(lines) # number of lines
	print("Number of lines detected:%d", n)
	for i in range(n):
		print(lines[i])
		for x1,y1,x2,y2 in lines[i]:
			y_avg = abs(y2)
			if min_dist < y_avg and (abs(x2 - x1) > 50):
				min_dist = y_avg
				min_line = [x1, y1, x2, y2]
			cv2.line(line_image,(x1,y1),(x2,y2),(255,0,0),5)
	if (min_line is None):
		print('None min_line')
	full_line = get_full_line(min_line, y_max, x_max, True)

	print(min_line)
	lines_edges = cv2.addWeighted(img, 0.8, line_image, 1, 0)
	cv2.line(line_image_follow,(full_line[0],full_line[1]),(full_line[2],full_line[3]),(255,0,0),20)
	line_follow = cv2.addWeighted(img, 0.8, line_image_follow, 1, 0)
	cv2.imwrite('src1.png', lines_edges)
	cv2.imwrite('src2.png', line_follow)


start_time = time.time()
for i in range(1):
	get_vertical_edge('src.png')
end_time = time.time()
print("Total time = %f", end_time - start_time)
